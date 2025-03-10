# Copyright (c) 2022 NVIDIA CORPORATION.  All rights reserved.
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import math
import os
import sys
import inspect
import hashlib
import ctypes

from typing import Tuple
from typing import List
from typing import Dict
from typing import Any
from typing import Callable

from warp.types import *
from warp.utils import *

import warp.codegen
import warp.build
import warp.config

# represents either a built-in or user-defined function
class Function:

    def __init__(self,
                 func,
                 key,
                 namespace,
                 input_types=None,
                 value_func=None,
                 module=None,
                 variadic=False,
                 doc="",
                 group="",
                 hidden=False,
                 skip_replay=False):
        
        self.func = func   # points to Python function decorated with @wp.func, may be None for builtins
        self.key = key
        self.namespace = namespace
        self.value_func = value_func    # a function that takes a list of args and returns the value type, e.g.: load(array, index) returns the type of value being loaded
        self.input_types = input_types
        self.doc = doc
        self.group = group
        self.module = module
        self.variadic = variadic        # function can take arbitrary number of inputs, e.g.: printf()
        self.hidden = hidden            # function will not be listed in docs
        self.skip_replay = skip_replay  # whether or not operation will be performed during the forward replay in the backward pass

        if (func):
            self.adj = warp.codegen.Adjoint(func)

            # record input types    
            self.input_types = {}            
            for a in self.adj.args:
                self.input_types[a.label] = a.type
            
        if (module):
            module.register_function(self)

# caches source and compiled entry points for a kernel (will be populated after module loads)
class Kernel:
    
    def __init__(self, func, key, module):

        self.func = func
        self.module = module
        self.key = key

        self.forward_cpu = None
        self.backward_cpu = None
        
        self.forward_cuda = None
        self.backward_cuda = None

        self.adj = warp.codegen.Adjoint(func)

        if (module):
            module.register_kernel(self)

    # lookup and cache entry points based on name, called after compilation / module load
    def hook(self):

        dll = self.module.dll
        cuda = self.module.cuda

        if (dll):

            try:
                self.forward_cpu = eval("dll." + self.key + "_cpu_forward")
                self.backward_cpu = eval("dll." + self.key + "_cpu_backward")
            except:
                print(f"Could not load CPU methods for kernel {self.key}")

        if (cuda):

            try:
                self.forward_cuda = runtime.core.cuda_get_kernel(self.module.cuda, (self.key + "_cuda_kernel_forward").encode('utf-8'))
                self.backward_cuda = runtime.core.cuda_get_kernel(self.module.cuda, (self.key + "_cuda_kernel_backward").encode('utf-8'))
            except:
                print(f"Could not load CUDA methods for kernel {self.key}")


#----------------------

# decorator to register function, @func
def func(f):

    m = get_module(f.__module__)
    f = Function(func=f, key=f.__name__, namespace="", module=m, value_func=None)   # value_type not known yet, will be inferred during Adjoint.build()

    return f

# decorator to register kernel, @kernel, custom_name may be a string that creates a kernel with a different name from the actual function
def kernel(f):
    
    m = get_module(f.__module__)
    k = Kernel(func=f, key=f.__name__, module=m)

    return k


builtin_functions = {}

def add_builtin(key, input_types={}, value_type=None, value_func=None, doc="", namespace="wp::", variadic=False, group="Other", hidden=False, skip_replay=False):

    # wrap simple single-type functions with a value_func()
    if value_func == None:
        def value_func(args):
            return value_type
        
    func = Function(func=None,
                    key=key,
                    namespace=namespace,
                    input_types=input_types,
                    value_func=value_func,
                    variadic=variadic,
                    doc=doc,
                    group=group,
                    hidden=hidden,
                    skip_replay=skip_replay)

    if key in builtin_functions:
        # if key exists we add overload
        builtin_functions[key].append(func)
    else:
        # insert into dict
        builtin_functions[key] = [func]


# global dictionary of modules
user_modules = {}

def get_module(m):

    if (m not in user_modules):
        user_modules[m] = warp.context.Module(str(m))

    return user_modules[m]


#-----------------------------------------------------
# stores all functions and kernels for a Python module
# creates a hash of the function to use for checking
# build cache

class Module:

    def __init__(self, name):

        self.name = name
        self.kernels = {}
        self.functions = {}

        self.dll = None
        self.cuda = None

        self.loaded = False
        self.build_failed = False

        self.options = {"max_unroll": 16,
                        "mode": warp.config.mode}

    def register_kernel(self, kernel):

        if kernel.key in self.kernels:
            
            # if kernel is replacing an old one then assume it has changed and 
            # force a rebuild / reload of the dynamic library 
            if (self.dll):
                warp.build.unload_dll(self.dll)

            if (self.cuda):
                runtime.core.cuda_unload_module(self.cuda)
                
            self.dll = None
            self.cuda = None
            self.loaded = False

        # register new kernel
        self.kernels[kernel.key] = kernel


    def register_function(self, func):
        self.functions[func.key] = func

    def hash_module(self):
        
        h = hashlib.sha256()

        # functions source
        for func in self.functions.values():
            s = func.adj.source
            h.update(bytes(s, 'utf-8'))
            
        # kernel source
        for kernel in self.kernels.values():       
            s = kernel.adj.source
            h.update(bytes(s, 'utf-8'))

        # configuration parameters
        for k in sorted(self.options.keys()):
            s = f"{k}={self.options[k]}"
            h.update(bytes(s, 'utf-8'))
        
        # compile-time constants (global)
        h.update(constant.get_hash())

        return h.digest()

    def load(self):

        # early out to avoid repeatedly attemping to rebuild
        if self.build_failed:
            return False

        with ScopedTimer(f"Module {self.name} load"):

            enable_cpu = warp.is_cpu_available()
            enable_cuda = warp.is_cuda_available()

            module_name = "wp_" + self.name

            build_path = warp.build.kernel_bin_dir
            gen_path = warp.build.kernel_gen_dir

            hash_path = os.path.join(build_path, module_name + ".hash")
            module_path = os.path.join(build_path, module_name)

            ptx_path = module_path + ".ptx"

            if (os.name == 'nt'):
                dll_path = module_path + ".dll"
            else:
                dll_path = module_path + ".so"

            if (os.path.exists(build_path) == False):
                os.mkdir(build_path)

            # test cache
            module_hash = self.hash_module()

            build_cpu = enable_cpu
            build_cuda = enable_cuda

            if warp.config.cache_kernels and os.path.exists(hash_path):

                f = open(hash_path, 'rb')
                cache_hash = f.read()
                f.close()

                if cache_hash == module_hash:
                    
                    if enable_cpu and os.path.isfile(dll_path):
                        self.dll = warp.build.load_dll(dll_path)
                        if self.dll is not None:
                            build_cpu = False

                    if enable_cuda and os.path.isfile(ptx_path):
                        self.cuda = warp.build.load_cuda(ptx_path)
                        if self.cuda is not None:
                            build_cuda = False

                    if not build_cuda and not build_cpu:
                        if warp.config.verbose:
                            print("Warp: Using cached kernels for module {}".format(self.name))
                        self.loaded = True
                        return True

            if warp.config.verbose:
                print("Warp: Rebuilding kernels for module {}".format(self.name))

            # generate kernel source
            if build_cpu:
                cpp_path = os.path.join(gen_path, module_name + ".cpp")
                cpp_source = warp.codegen.cpu_module_header
            
            if build_cuda:
                cu_path = os.path.join(gen_path, module_name + ".cu")
                cu_source = warp.codegen.cuda_module_header

            # kernels
            entry_points = []

            # functions
            for name, func in self.functions.items():
            
                func.adj.build(builtin_functions, self.functions, self.options)
                
                if build_cpu:
                    cpp_source += warp.codegen.codegen_func(func.adj, device="cpu")

                if build_cuda:
                    cu_source += warp.codegen.codegen_func(func.adj, device="cuda")

                # complete the function return type after we have analyzed it (inferred from return statement in ast)
                def wrap(adj):
                    def value_type(args):
                        if (adj.return_var):
                            return adj.return_var.type
                        else:
                            return None

                    return value_type

                func.value_func = wrap(func.adj)


            # kernels
            for kernel in self.kernels.values():

                kernel.adj.build(builtin_functions, self.functions, self.options)

                # each kernel gets an entry point in the module
                if build_cpu:
                    entry_points.append(kernel.func.__name__ + "_cpu_forward")
                    entry_points.append(kernel.func.__name__ + "_cpu_backward")

                    cpp_source += warp.codegen.codegen_kernel(kernel, device="cpu")
                    cpp_source += warp.codegen.codegen_module(kernel, device="cpu")

                if build_cuda:
                    entry_points.append(kernel.func.__name__ + "_cuda_forward")
                    entry_points.append(kernel.func.__name__ + "_cuda_backward")

                    cu_source += warp.codegen.codegen_kernel(kernel, device="cuda")
                    cu_source += warp.codegen.codegen_module(kernel, device="cuda")


            # write cpp sources
            if build_cpu:
                cpp_file = open(cpp_path, "w")
                cpp_file.write(cpp_source)
                cpp_file.close()

            # write cuda sources
            if build_cuda:
                cu_file = open(cu_path, "w")
                cu_file.write(cu_source)
                cu_file.close()
        
            try:
                if build_cpu:
                    with ScopedTimer("Compile x86", active=warp.config.verbose):
                        warp.build.build_dll(cpp_path, None, dll_path, config=self.options["mode"])

                if build_cuda:
                    with ScopedTimer("Compile CUDA", active=warp.config.verbose):
                        warp.build.build_cuda(cu_path, ptx_path, config=self.options["mode"])

                # update cached output
                f = open(hash_path, 'wb')
                f.write(module_hash)
                f.close()

            except Exception as e:
                self.build_failed = True
                print(e)
                raise(e)

            if build_cpu:
                self.dll = warp.build.load_dll(dll_path)

            if build_cuda:
                self.cuda = warp.build.load_cuda(ptx_path)

            if enable_cpu and self.dll is None:
                raise Exception("Failed to load CPU module")

            if enable_cuda and self.cuda is None:
                raise Exception("Failed to load CUDA module")

            self.loaded = True
            return True

#-------------------------------------------
# exectution context

# a simple pooled allocator that caches allocs based 
# on size to avoid hitting the system allocator
class Allocator:

    def __init__(self, alloc_func, free_func):

        # map from sizes to array of allocs
        self.alloc_func = alloc_func
        self.free_func = free_func

        # map from size->list[allocs]
        self.pool = {}

    def __del__(self):
        self.clear()       

    def alloc(self, size_in_bytes):
        
        p = self.alloc_func(size_in_bytes)
        return p

        # if size_in_bytes in self.pool and len(self.pool[size_in_bytes]) > 0:            
        #     return self.pool[size_in_bytes].pop()
        # else:
        #     return self.alloc_func(size_in_bytes)

    def free(self, addr, size_in_bytes):

        addr = ctypes.cast(addr, ctypes.c_void_p)
        self.free_func(addr)
        return

        # if size_in_bytes not in self.pool:
        #     self.pool[size_in_bytes] = [addr,]
        # else:
        #     self.pool[size_in_bytes].append(addr)

    def print(self):
        
        total_size = 0

        for k,v in self.pool.items():
            print(f"alloc size: {k} num allocs: {len(v)}")
            total_size += k*len(v)

        print(f"total size: {total_size}")


    def clear(self):
        for s in self.pool.values():
            for a in s:
                self.free_func(a)
        
        self.pool = {}

class Runtime:

    def __init__(self):

        bin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bin")
        
        if (os.name == 'nt'):

            if (sys.version_info[0] > 3 or
                sys.version_info[0] == 3 and sys.version_info[1] >= 8):
                
                # Python >= 3.8 this method to add dll search paths
                os.add_dll_directory(bin_path)

            else:
                # Python < 3.8 we add dll directory to path
                os.environ["PATH"] = bin_path + os.pathsep + os.environ["PATH"]


            warp_lib = "warp.dll"
            self.core = warp.build.load_dll(os.path.join(bin_path, warp_lib))

        elif sys.platform == "darwin":

            warp_lib = os.path.join(bin_path, "warp.dylib")
            self.core = warp.build.load_dll(warp_lib)

        else:

            warp_lib = os.path.join(bin_path, "warp.so")
            self.core = warp.build.load_dll(warp_lib)

        # setup c-types for warp.dll
        self.core.alloc_host.restype = ctypes.c_void_p
        self.core.alloc_device.restype = ctypes.c_void_p
        
        self.core.mesh_create_host.restype = ctypes.c_uint64
        self.core.mesh_create_host.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

        self.core.mesh_create_device.restype = ctypes.c_uint64
        self.core.mesh_create_device.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

        self.core.mesh_destroy_host.argtypes = [ctypes.c_uint64]
        self.core.mesh_destroy_device.argtypes = [ctypes.c_uint64]

        self.core.mesh_refit_host.argtypes = [ctypes.c_uint64]
        self.core.mesh_refit_device.argtypes = [ctypes.c_uint64]

        self.core.hash_grid_create_host.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.core.hash_grid_create_host.restype = ctypes.c_uint64
        self.core.hash_grid_destroy_host.argtypes = [ctypes.c_uint64]
        self.core.hash_grid_update_host.argtypes = [ctypes.c_uint64, ctypes.c_float, ctypes.c_void_p, ctypes.c_int]
        self.core.hash_grid_reserve_host.argtypes = [ctypes.c_uint64, ctypes.c_int]

        self.core.hash_grid_create_device.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.core.hash_grid_create_device.restype = ctypes.c_uint64
        self.core.hash_grid_destroy_device.argtypes = [ctypes.c_uint64]
        self.core.hash_grid_update_device.argtypes = [ctypes.c_uint64, ctypes.c_float, ctypes.c_void_p, ctypes.c_int]
        self.core.hash_grid_reserve_device.argtypes = [ctypes.c_uint64, ctypes.c_int]

        self.core.volume_create_host.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        self.core.volume_create_host.restype = ctypes.c_uint64
        self.core.volume_get_buffer_info_host.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint64)]
        self.core.volume_destroy_host.argtypes = [ctypes.c_uint64]

        self.core.volume_create_device.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        self.core.volume_create_device.restype = ctypes.c_uint64
        self.core.volume_get_buffer_info_device.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint64)]
        self.core.volume_destroy_device.argtypes = [ctypes.c_uint64]

        # load CUDA entry points on supported platforms
        self.core.cuda_check_device.restype = ctypes.c_uint64
        self.core.cuda_get_context.restype = ctypes.c_void_p
        self.core.cuda_get_stream.restype = ctypes.c_void_p
        self.core.cuda_graph_end_capture.restype = ctypes.c_void_p
        self.core.cuda_get_device_name.restype = ctypes.c_char_p

        self.core.cuda_compile_program.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool, ctypes.c_char_p]
        self.core.cuda_compile_program.restype = ctypes.c_size_t

        self.core.cuda_load_module.argtypes = [ctypes.c_char_p]
        self.core.cuda_load_module.restype = ctypes.c_void_p

        self.core.cuda_unload_module.argtypes = [ctypes.c_void_p]

        self.core.cuda_get_kernel.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.core.cuda_get_kernel.restype = ctypes.c_void_p
        
        self.core.cuda_launch_kernel.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_void_p)]
        self.core.cuda_launch_kernel.restype = ctypes.c_size_t

        self.core.init.restype = ctypes.c_int
        
        error = self.core.init()

        if (error > 0):
            raise Exception("Warp Initialization failed, CUDA not found")

        # allocation functions, these are function local to 
        # force other classes to go through the allocator objects
        def alloc_host(num_bytes):
            ptr = self.core.alloc_host(num_bytes)       
            return ptr

        def free_host(ptr):
            self.core.free_host(ctypes.cast(ptr, ctypes.POINTER(ctypes.c_int)))

        def alloc_device(num_bytes):
            ptr = self.core.alloc_device(ctypes.c_size_t(num_bytes))
            return ptr

        def free_device(ptr):
            # must be careful to not call any globals here
            # since this may be called during destruction / shutdown
            # even ctypes module may no longer exist
            self.core.free_device(ptr)

        self.host_allocator = Allocator(alloc_host, free_host)
        self.device_allocator = Allocator(alloc_device, free_device)

        # save context
        self.cuda_device = self.core.cuda_get_context()
        self.cuda_stream = self.core.cuda_get_stream()

        # initialize host build env
        if (warp.config.host_compiler == None):
            warp.config.host_compiler = warp.build.find_host_compiler()

        # initialize kernel cache
        warp.build.init_kernel_cache(warp.config.kernel_cache_dir)

        # print device and version information
        print("Warp initialized:")
        print("   Version: {}".format(warp.config.version))
        print("   Using CUDA device: {}".format(self.core.cuda_get_device_name().decode()))
        if (warp.config.host_compiler):
            print("   Using CPU compiler: {}".format(warp.config.host_compiler.rstrip()))
        else:
            print("   Using CPU compiler: Not found")        
        print("   Kernel cache: {}".format(warp.config.kernel_cache_dir))

        # global tape
        self.tape = None

    def verify_device(self):

        if warp.config.verify_cuda:

            context = self.core.cuda_get_context()
            if (context != self.cuda_device):
                raise RuntimeError("Unexpected CUDA device, original {} current: {}".format(self.cuda_device, context))

            err = self.core.cuda_check_device()
            if (err != 0):
                raise RuntimeError("CUDA error detected: {}".format(err))



# global entry points 
def is_cpu_available():
    return warp.config.host_compiler != None

def is_cuda_available():
    return runtime.cuda_device != None

def is_device_available(device):
    return device in wp.get_devices()

def get_devices():
    """Returns a list of device strings supported by in this environment.
    """
    devices = []
    if (is_cpu_available()):
        devices.append("cpu")
    if (is_cuda_available()):
        devices.append("cuda")

    return devices

def get_preferred_device():
    """Returns the preferred compute device, will return "cuda" if available, "cpu" otherwise.
    """
    if is_cuda_available():
        return "cuda"
    elif is_cpu_available():
        return "cpu"
    else:
        return None


def zeros(shape: Tuple=None, dtype=float, device: str="cpu", requires_grad: bool=False, **kwargs)-> warp.array:
    """Return a zero-initialized array

    Args:
        shape: Array dimensions
        dtype: Type of each element, e.g.: warp.vec3, warp.mat33, etc
        device: Device that array will live on
        requires_grad: Whether the array will be tracked for back propagation

    Returns:
        A warp.array object representing the allocation                
    """

    if runtime == None:
        raise RuntimeError("Warp not initialized, call wp.init() before use")

    if device != "cpu" and device != "cuda":
        raise RuntimeError(f"Trying to allocate array on unknown device {device}")

    if device == "cuda" and not is_cuda_available():
        raise RuntimeError("Trying to allocate CUDA buffer without GPU support")


    # backwards compatability for case where users did wp.zeros(n, dtype=..), or wp.zeros(n=length, dtype=..)
    if isinstance(shape, int):
        shape = (shape,)
    elif "n" in kwargs:
        shape = (kwargs["n"], )
    
    # compute num els
    num_elements = 1
    for d in shape:
        num_elements *= d

    num_bytes = num_elements*warp.types.type_size_in_bytes(dtype)

    if device == "cpu":
        ptr = runtime.host_allocator.alloc(num_bytes) 
        runtime.core.memset_host(ctypes.cast(ptr,ctypes.POINTER(ctypes.c_int)), ctypes.c_int(0), ctypes.c_size_t(num_bytes))

    elif device == "cuda":
        ptr = runtime.device_allocator.alloc(num_bytes)
        runtime.core.memset_device(ctypes.cast(ptr,ctypes.POINTER(ctypes.c_int)), ctypes.c_int(0), ctypes.c_size_t(num_bytes))

    if (ptr == None and num_bytes > 0):
        raise RuntimeError("Memory allocation failed on device: {} for {} bytes".format(device, num_bytes))
    else:
        # construct array
        return warp.types.array(dtype=dtype, shape=shape, capacity=num_bytes, ptr=ptr, device=device, owner=True, requires_grad=requires_grad)

def zeros_like(src: warp.array) -> warp.array:
    """Return a zero-initialized array with the same type and dimension of another array

    Args:
        src: The template array to use for length, data type, and device

    Returns:
        A warp.array object representing the allocation
    """

    arr = zeros(shape=src.shape, dtype=src.dtype, device=src.device, requires_grad=src.requires_grad)
    return arr

def clone(src: warp.array) -> warp.array:
    """Clone an existing array, allocates a copy of the src memory

    Args:
        src: The source array to copy

    Returns:
        A warp.array object representing the allocation
    """

    dest = empty(len(src), dtype=src.dtype, device=src.device, requires_grad=src.requires_grad)
    copy(dest, src)

    return dest

def empty(shape: Tuple=None, dtype=float, device:str="cpu", requires_grad:bool=False, **kwargs) -> warp.array:
    """Returns an uninitialized array

    Args:
        n: Number of elements
        dtype: Type of each element, e.g.: `warp.vec3`, `warp.mat33`, etc
        device: Device that array will live on
        requires_grad: Whether the array will be tracked for back propagation

    Returns:
        A warp.array object representing the allocation
    """

    # todo: implement uninitialized allocation
    return zeros(shape, dtype, device, requires_grad=requires_grad, **kwargs)  

def empty_like(src: warp.array, requires_grad:bool=False) -> warp.array:
    """Return an uninitialized array with the same type and dimension of another array

    Args:
        src: The template array to use for length, data type, and device
        requires_grad: Whether the array will be tracked for back propagation

    Returns:
        A warp.array object representing the allocation
    """
    arr = empty(shape=src.shape, dtype=src.dtype, device=src.device, requires_grad=requires_grad)
    return arr


def from_numpy(arr, dtype, device="cpu", requires_grad=False):

    return warp.array(data=arr, dtype=dtype, device=device, requires_grad=requires_grad)


def launch(kernel, dim: Tuple[int], inputs:List, outputs:List=[], adj_inputs:List=[], adj_outputs:List=[], device:str="cpu", adjoint=False):
    """Launch a Warp kernel on the target device

    Kernel launches are asynchronous with respect to the calling Python thread. 

    Args:
        kernel: The name of a Warp kernel function, decorated with the ``@wp.kernel`` decorator
        dim: The number of threads to launch the kernel, can be an integer, or a Tuple of ints with max of 4 dimensions
        inputs: The input parameters to the kernel
        outputs: The output parameters (optional)
        adj_inputs: The adjoint inputs (optional)
        adj_outputs: The adjoint outputs (optional)
        device: The device to launch on
        adjoint: Whether to run forward or backward pass (typically use False)
    """

    # check device available
    if is_device_available(device) == False:
        raise RuntimeError(f"Error launching kernel, device '{device}' is not available.")

    # check kernel is a function
    if isinstance(kernel, wp.Kernel) == False:
        raise RuntimeError("Error launching kernel, can only launch functions decorated with @wp.kernel.")

    # debugging aid
    if (warp.config.print_launches):
        print(f"kernel: {kernel.key} dim: {dim} inputs: {inputs} outputs: {outputs} device: {device}")

    # delay load modules
    if (kernel.module.loaded == False):
        success = kernel.module.load()
        if (success == False):
            return

    # construct launch bounds
    bounds = warp.types.launch_bounds_t(dim)

    if (bounds.size > 0):

        # first param is the number of threads
        params = []
        params.append(bounds)

        # converts arguments to kernel's expected ctypes and packs into params
        def pack_args(args, params):

            for i, a in enumerate(args):

                arg_type = kernel.adj.args[i].type
                arg_name = kernel.adj.args[i].label

                if (isinstance(arg_type, warp.types.array)):

                    if (a is None):
                        
                        # allow for NULL arrays
                        params.append(warp.types.array_t())

                    else:

                        # check for array value
                        if (isinstance(a, warp.types.array) == False):
                            raise RuntimeError(f"Error launching kernel '{kernel.key}', argument '{arg_name}' expects an array, but passed value has type {type(a)}.")
                        
                        # check subtype
                        if (a.dtype != arg_type.dtype):
                            raise RuntimeError(f"Error launching kernel '{kernel.key}', argument '{arg_name}' expects an array with dtype={arg_type.dtype} but passed array has dtype={a.dtype}.")

                        # check dimensions
                        if (a.ndim != arg_type.ndim):
                            raise RuntimeError(f"Error launching kernel '{kernel.key}', argument '{arg_name}' expects an array with dimensions {arg_type.ndim} but the passed array has dimensions {a.ndim}.")

                        # check device
                        if (a.device != device):
                            raise RuntimeError(f"Error launching kernel '{kernel.key}', trying to launch on device='{device}', but input array for argument '{arg_name}' is on device={a.device}.")
                        
                        params.append(a.__ctype__())

                # try to convert to a value type (vec3, mat33, etc)
                elif issubclass(arg_type, ctypes.Array):

                    # force conversion to ndarray first (handles tuple / list, Gf.Vec3 case)
                    a = np.array(a)

                    # flatten to 1D array
                    v = a.flatten()
                    if (len(v) != arg_type._length_):
                        raise RuntimeError(f"Error launching kernel '{kernel.key}', parameter for argument '{arg_name}' has length {len(v)}, but expected {arg_type._length_}. Could not convert parameter to {arg_type}.")

                    # wrap the arg_type (which is an ctypes.Array) in a structure
                    # to ensure parameter is passed to the .dll by value rather than reference
                    class ValueArg(ctypes.Structure):
                        _fields_ = [ ('value', arg_type)]

                    x = ValueArg()
                    for i in range(arg_type._length_):
                        x.value[i] = v[i]

                    params.append(x)

                else:
                    try:
                        # try to pack as a scalar type
                        params.append(arg_type._type_(a))
                    except:
                        raise RuntimeError(f"Error launching kernel, unable to pack kernel parameter type {type(a)} for param {arg_name}, expected {arg_type}")


        fwd_args = inputs + outputs
        adj_args = adj_inputs + adj_outputs

        if (len(fwd_args)) != (len(kernel.adj.args)): 
            raise RuntimeError(f"Error launching kernel '{kernel.key}', passed {len(fwd_args)} arguments but kernel requires {len(kernel.adj.args)}.")

        pack_args(fwd_args, params)
        pack_args(adj_args, params)

        # late bind
        if (kernel.forward_cpu == None or kernel.forward_cuda == None):
            kernel.hook()

        # run kernel
        if device == 'cpu':

            if (adjoint):
                kernel.backward_cpu(*params)
            else:
                kernel.forward_cpu(*params)

        
        elif device == "cuda":

            kernel_args = [ctypes.c_void_p(ctypes.addressof(x)) for x in params]
            kernel_params = (ctypes.c_void_p * len(kernel_args))(*kernel_args)

            if (adjoint):
                runtime.core.cuda_launch_kernel(kernel.backward_cuda, bounds.size, kernel_params)
            else:
                runtime.core.cuda_launch_kernel(kernel.forward_cuda, bounds.size, kernel_params)

            try:
                runtime.verify_device()            
            except Exception as e:
                print(f"Error launching kernel: {kernel.key} on device {device}")
                raise e

    # record on tape if one is active
    if (runtime.tape):
        runtime.tape.record(kernel, dim, inputs, outputs, device)

def synchronize():
    """Manually synchronize the calling CPU thread with any outstanding CUDA work

    This method allows the host application code to ensure that any kernel launches
    or memory copies have completed.
    """

    runtime.core.synchronize()


def force_load():
    """Force all user-defined kernels to be compiled
    """

    for m in user_modules.values():
        if (m.loaded == False):
            m.load()

def set_module_options(options: Dict[str, Any]):
    """Set options for the current module.

    Options can be used to control runtime compilation and code-generation
    for the current module individually. Available options are listed below.

    * **mode**: The compilation mode to use, can be "debug", or "release", defaults to the value of ``warp.config.mode``.
    * **max_unroll**: The maximum fixed-size loop to unroll (default 16)

    Args:

        options: Set of key-value option pairs
    """
   
    import inspect
    m = inspect.getmodule(inspect.stack()[1][0])

    get_module(m.__name__).options.update(options)

def get_module_options() -> Dict[str, Any]:
    """Returns a list of options for the current module.
    """
    import inspect
    m = inspect.getmodule(inspect.stack()[1][0])

    return get_module(m.__name__).options


def capture_begin():
    """Begin capture of a CUDA graph

    Captures all subsequent kernel launches and memory operations on CUDA devices.
    This can be used to record large numbers of kernels and replay them with low-overhead.
    """

    if warp.config.verify_cuda == True:
        raise RuntimeError("Cannot use CUDA error verification during graph capture")

    # ensure that all modules are loaded, this is necessary
    # since cuLoadModule() is not permitted during capture
    force_load()

    runtime.core.cuda_graph_begin_capture()

def capture_end()->int:
    """Ends the capture of a CUDA graph

    Returns:
        A handle to a CUDA graph object that can be launched with :func:`~warp.capture_launch()`
    """

    graph = runtime.core.cuda_graph_end_capture()
    
    if graph == None:
        raise RuntimeError("Error occurred during CUDA graph capture. This could be due to an unintended allocation or CPU/GPU synchronization event.")
    else:
        return graph

def capture_launch(graph: int):
    """Launch a previously captured CUDA graph

    Args:
        graph: A handle to the graph as returned by :func:`~warp.capture_end`
    """

    runtime.core.cuda_graph_launch(ctypes.c_void_p(graph))


def copy(dest: warp.array, src: warp.array, dest_offset: int = 0, src_offset: int = 0, count: int = 0):
    """Copy array contents from src to dest

    Args:
        dest: Destination array, must be at least as big as source buffer
        src: Source array
        dest_offset: Element offset in the destination array
        src_offset: Element offset in the source array
        count: Number of array elements to copy (will copy all elements if set to 0)

    """

    if count <= 0:
        count = src.size

    bytes_to_copy = count * type_size_in_bytes(src.dtype)

    src_size_in_bytes = src.size * type_size_in_bytes(src.dtype)
    dst_size_in_bytes = dest.size * type_size_in_bytes(dest.dtype)

    src_offset_in_bytes = src_offset * type_size_in_bytes(src.dtype)
    dst_offset_in_bytes = dest_offset * type_size_in_bytes(dest.dtype)

    src_ptr = src.ptr + src_offset_in_bytes
    dst_ptr = dest.ptr + dst_offset_in_bytes

    if src_offset_in_bytes + bytes_to_copy > src_size_in_bytes:
        raise RuntimeError(f"Trying to copy source buffer with size ({bytes_to_copy}) from offset ({src_offset_in_bytes}) is larger than source size ({src_size_in_bytes})")

    if dst_offset_in_bytes + bytes_to_copy > dst_size_in_bytes:
        raise RuntimeError(f"Trying to copy source buffer with size ({bytes_to_copy}) to offset ({dst_offset_in_bytes}) is larger than destination size ({dst_size_in_bytes})")

    if (src.device == "cpu" and dest.device == "cuda"):
        runtime.core.memcpy_h2d(ctypes.c_void_p(dst_ptr), ctypes.c_void_p(src_ptr), ctypes.c_size_t(bytes_to_copy))

    elif (src.device == "cuda" and dest.device == "cpu"):
        runtime.core.memcpy_d2h(ctypes.c_void_p(dst_ptr), ctypes.c_void_p(src_ptr), ctypes.c_size_t(bytes_to_copy))

    elif (src.device == "cpu" and dest.device == "cpu"):
        runtime.core.memcpy_h2h(ctypes.c_void_p(dst_ptr), ctypes.c_void_p(src_ptr), ctypes.c_size_t(bytes_to_copy))

    elif (src.device == "cuda" and dest.device == "cuda"):
        runtime.core.memcpy_d2d(ctypes.c_void_p(dst_ptr), ctypes.c_void_p(src_ptr), ctypes.c_size_t(bytes_to_copy))
    
    else:
        raise RuntimeError("Unexpected source and destination combination")


def type_str(t):
    if (t == None):
        return "None"
    elif t == Any:
        return "Any"
    elif t == Callable:
        return "Callable"
    elif isinstance(t, List):
        return ", ".join(map(type_str, t))
    elif isinstance(t, array):
        return f"array[{type_str(t.dtype)}]"
    else:
        return t.__name__

def print_function(f, file):

    if f.hidden:
        return

    args = ", ".join(f"{k}: {type_str(v)}" for k,v in f.input_types.items())

    return_type = ""

    try:
        # todo: construct a default value for each of the functions args
        # so we can generate the return type for overloaded functions
        return_type = " -> " + type_str(f.value_func(None))
    except:
        pass

    print(f".. function:: {f.key}({args}){return_type}", file=file)
    print("", file=file)
    
    if (f.doc != ""):
        print(f"   {f.doc}", file=file)
        print("", file=file)

    print(file=file)
    
def print_builtins(file):

    header = ("..\n"
              "   Autogenerated File - Do not edit. Run build_docs.py to generate.\n"
              "\n"
              ".. functions:\n"
              ".. currentmodule:: warp\n"
              "\n"
              "Kernel Reference\n"
              "================")

    print(header, file=file)

    # type definitions of all functions by group
    print("Scalar Types", file=file)
    print("------------", file=file)

    for t in warp.types.scalar_types:
        print(f".. autoclass:: {t.__name__}", file=file)

    print("Vector Types", file=file)
    print("------------", file=file)

    for t in warp.types.vector_types:
        print(f".. autoclass:: {t.__name__}", file=file)


    # build dictionary of all functions by group
    groups = {}

    for k, f in builtin_functions.items():
        
        g = None

        if (isinstance(f, list)):
            # assumes all overloads have the same group
            g = f[0].group
        else:
            g = f.group

        if (g not in groups):
            groups[g] = []
        
        groups[g].append(f)

    for k, g in groups.items():
        print("\n", file=file)
        print(k, file=file)
        print("---------------", file=file)

        for f in g:            
            if isinstance(f, list):
                for x in f:
                    print_function(x, file=file)
            else:
                print_function(f, file=file)


# ensures that correct CUDA is set for the guards lifetime
# restores the previous CUDA context on exit
class ScopedCudaGuard:

    def __init__(self):
        pass

    def __enter__(self):
        runtime.core.cuda_acquire_context()

    def __exit__(self, exc_type, exc_value, traceback):
        runtime.core.cuda_restore_context()


# initialize global runtime
runtime = None

def init():
    """Initialize the Warp runtime. This function must be called before any other API call. If an error occurs an exception will be raised.
    """
    global runtime

    if (runtime == None):
        runtime = Runtime()


