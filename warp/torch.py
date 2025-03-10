# Copyright (c) 2022 NVIDIA CORPORATION.  All rights reserved.
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import warp
import torch
import numpy


# wrap a torch tensor to a wp array, data is not copied
def from_torch(t, dtype=warp.types.float32):
    # ensure tensors are contiguous
    assert(t.is_contiguous())

    # placeholder for warp.types.float16
    assert dtype == warp.types.float32 or dtype == warp.types.float32, "Warp arrays can be constructed as wp.float32 only"

    if (t.dtype != torch.float32 and t.dtype != torch.int32):
        raise RuntimeError("Error aliasing Torch tensor to Warp array. Torch tensor must be float32 or int32 type")

    a = warp.types.array(
        ptr=t.data_ptr(),
        dtype=dtype,
        shape=t.shape,
        copy=False,
        owner=False,
        requires_grad=True,
        device=t.device.type)

    # save a reference to the source tensor, otherwise it will be deallocated
    a.tensor = t
    
    return a


def to_torch(a):
    if a.device == "cpu":
        # Torch has an issue wrapping CPU objects 
        # that support the __array_interface__ protocol
        # in this case we need to workaround by going
        # to an ndarray first, see https://pearu.github.io/array_interface_pytorch.html
        return torch.as_tensor(numpy.asarray(a))

    elif a.device == "cuda":
        # Torch does support the __cuda_array_interface__
        # correctly, but we must be sure to maintain a reference
        # to the owning object to prevent memory allocs going out of scope
        return torch.as_tensor(a, device="cuda")
    
    else:
        raise RuntimeError("Unsupported device")



