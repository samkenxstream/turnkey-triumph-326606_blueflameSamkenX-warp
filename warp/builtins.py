# Copyright (c) 2022 NVIDIA CORPORATION.  All rights reserved.
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from . context import add_builtin

from warp.types import *

from typing import Tuple
from typing import List
from typing import Dict
from typing import Any
from typing import Callable

#---------------------------------
# Scalar Math

add_builtin("min", input_types={"x": int, "y": int}, value_type=int, doc="Return the minimum of two integers.", group="Scalar Math")
add_builtin("min", input_types={"x": float, "y": float}, value_type=float, doc="Return the minimum of two floats.", group="Scalar Math")

add_builtin("max", input_types={"x": int, "y": int}, value_type=int, doc="Return the maximum of two integers.", group="Scalar Math")
add_builtin("max", input_types={"x": float, "y": float}, value_type=float, doc="Return the maximum of two floats.", group="Scalar Math")

add_builtin("clamp", input_types={"x": int, "a": int, "b": int}, value_type=int, doc="Clamp the value of x to the range [a, b].", group="Scalar Math")
add_builtin("clamp", input_types={"x": float, "a": float, "b": float}, value_type=float, doc="Clamp the value of x to the range [a, b].", group="Scalar Math")

add_builtin("abs", input_types={"x": int}, value_type=int, doc="Return the absolute value of x.", group="Scalar Math")
add_builtin("abs", input_types={"x": float}, value_type=float, doc="Return the absolute value of x.", group="Scalar Math")
add_builtin("sign", input_types={"x": int}, value_type=int, doc="Return -1 if x < 0, return 1 otherwise.", group="Scalar Math")
add_builtin("sign", input_types={"x": float}, value_type=float, doc="Return -1.0 if x < 0.0, return 1.0 otherwise.", group="Scalar Math")

add_builtin("step", input_types={"x": float}, value_type=float, doc="Return 1.0 if x < 0.0, return 0.0 otherwise.", group="Scalar Math")
add_builtin("nonzero", input_types={"x": float}, value_type=float, doc="Return 1.0 if x is not equal to zero, return 0.0 otherwise.", group="Scalar Math")
add_builtin("sin", input_types={"x": float}, value_type=float, doc="Return the sine of x in radians.", group="Scalar Math")
add_builtin("cos", input_types={"x": float}, value_type=float, doc="Return the cosine of x in radians.", group="Scalar Math")
add_builtin("acos", input_types={"x": float}, value_type=float, doc="Return arccos of x in radians. Inputs are automatically clamped to [-1.0, 1.0].", group="Scalar Math")
add_builtin("asin", input_types={"x": float}, value_type=float, doc="Return arcsin of x in radians. Inputs are automatically clamped to [-1.0, 1.0].", group="Scalar Math")
add_builtin("sqrt", input_types={"x": float}, value_type=float, doc="Return the sqrt of x, where x is positive.", group="Scalar Math")
add_builtin("tan", input_types={"x": float}, value_type=float, doc="Return tangent of x in radians.", group="Scalar Math")
add_builtin("atan", input_types={"x": float}, value_type=float, doc="Return arctan of x.", group="Scalar Math")
add_builtin("atan2", input_types={"y": float, "x": float}, value_type=float, doc="Return atan2 of x.", group="Scalar Math")
add_builtin("sinh", input_types={"x": float}, value_type=float, doc="Return the sinh of x.", group="Scalar Math")
add_builtin("cosh", input_types={"x": float}, value_type=float, doc="Return the cosh of x.", group="Scalar Math")
add_builtin("tanh", input_types={"x": float}, value_type=float, doc="Return the tanh of x.", group="Scalar Math")

add_builtin("log", input_types={"x": float}, value_type=float, doc="Return the natural log (base-e) of x, where x is positive.", group="Scalar Math")
add_builtin("exp", input_types={"x": float}, value_type=float, doc="Return base-e exponential, e^x.", group="Scalar Math")
add_builtin("pow", input_types={"x": float, "y": float}, value_type=float, doc="Return the result of x raised to power of y.", group="Scalar Math")

add_builtin("round", input_types={"x": float}, value_type=float, group="Scalar Math",
    doc="""Calculate the nearest integer value, rounding halfway cases away from zero.
   This is the most intuitive form of rounding in the colloquial sense, but can be slower than other options like ``warp.rint()``.
   Differs from ``numpy.round()``, which behaves the same way as ``numpy.rint()``.""")

add_builtin("rint", input_types={"x": float}, value_type=float, group="Scalar Math",
    doc="""Calculate the nearest integer value, rounding halfway cases to nearest even integer.
   It is generally faster than ``warp.round()``.
   Equivalent to ``numpy.rint()``.""")

add_builtin("trunc", input_types={"x": float}, value_type=float, group="Scalar Math",
    doc="""Calculate the nearest integer that is closer to zero than x.
   In other words, it discards the fractional part of x.
   It is similar to casting ``float(int(x))``, but preserves the negative sign when x is in the range [-0.0, -1.0).
   Equivalent to ``numpy.trunc()`` and ``numpy.fix()``.""")

add_builtin("floor", input_types={"x": float}, value_type=float, group="Scalar Math",
    doc="""Calculate the largest integer that is less than or equal to x.""")

add_builtin("ceil", input_types={"x": float}, value_type=float, group="Scalar Math",
    doc="""Calculate the smallest integer that is greater than or equal to x.""")

#---------------------------------
# Vector Math

add_builtin("dot", input_types={"x": vec2, "y": vec2}, value_type=float, group="Vector Math",
    doc="Compute the dot product between two 2d vectors.")
add_builtin("dot", input_types={"x": vec3, "y": vec3}, value_type=float, group="Vector Math",
    doc="Compute the dot product between two 3d vectors.")
add_builtin("dot", input_types={"x": vec4, "y": vec4}, value_type=float, group="Vector Math",
    doc="Compute the dot product between two 4d vectors.")
add_builtin("dot", input_types={"x": quat, "y": quat}, value_type=float, group="Vector Math",
    doc="Compute the dot product between two quaternions.")

add_builtin("outer", input_types={"x": vec2, "y": vec2}, value_type=mat22, group="Vector Math",
    doc="Compute the outer product x*y^T for two vec2 objects.")
add_builtin("outer", input_types={"x": vec3, "y": vec3}, value_type=mat33, group="Vector Math",
    doc="Compute the outer product x*y^T for two vec3 objects.")

add_builtin("cross", input_types={"x": vec3, "y": vec3}, value_type=vec3, group="Vector Math",
    doc="Compute the cross product of two 3d vectors.")
add_builtin("skew", input_types={"x": vec3}, value_type=mat33, group="Vector Math",
    doc="Compute the skew symmetric matrix for a 3d vector.")

add_builtin("length", input_types={"x": vec2}, value_type=float, group="Vector Math",
    doc="Compute the length of a 2d vector.")
add_builtin("length", input_types={"x": vec3}, value_type=float, group="Vector Math",
    doc="Compute the length of a 3d vector.")
add_builtin("length", input_types={"x": vec4}, value_type=float, group="Vector Math",
    doc="Compute the length of a 4d vector.")
add_builtin("normalize", input_types={"x": vec2}, value_type=vec2, group="Vector Math",
    doc="Compute the normalized value of x, if length(x) is 0 then the zero vector is returned.")
add_builtin("normalize", input_types={"x": vec3}, value_type=vec3, group="Vector Math",
    doc="Compute the normalized value of x, if length(x) is 0 then the zero vector is returned.")
add_builtin("normalize", input_types={"x": vec4}, value_type=vec4, group="Vector Math",
    doc="Compute the normalized value of x, if length(x) is 0 then the zero vector is returned.")
add_builtin("normalize", input_types={"x": quat}, value_type=quat, group="Vector Math",
    doc="Compute the normalized value of x, if length(x) is 0 then the zero quat is returned.")

add_builtin("transpose", input_types={"m": mat22}, value_type=mat22, group="Vector Math",
    doc="Return the transpose of the matrix m")
add_builtin("transpose", input_types={"m": mat33}, value_type=mat33, group="Vector Math",
    doc="Return the transpose of the matrix m")
add_builtin("transpose", input_types={"m": mat44}, value_type=mat44, group="Vector Math",
    doc="Return the transpose of the matrix m")
add_builtin("transpose", input_types={"m": spatial_matrix}, value_type=spatial_matrix, group="Vector Math",
    doc="Return the transpose of the matrix m")

add_builtin("inverse", input_types={"m": mat22}, value_type=mat22, group="Vector Math",
    doc="Return the inverse of the matrix m")
add_builtin("inverse", input_types={"m": mat33}, value_type=mat33, group="Vector Math",
    doc="Return the inverse of the matrix m")
add_builtin("inverse", input_types={"m": mat44}, value_type=mat44, group="Vector Math",
    doc="Return the inverse of the matrix m")

add_builtin("determinant", input_types={"m": mat22}, value_type=float, group="Vector Math",
    doc="Return the determinant of the matrix m")
add_builtin("determinant", input_types={"m": mat33}, value_type=float, group="Vector Math",
    doc="Return the determinant of the matrix m")
add_builtin("determinant", input_types={"m": mat44}, value_type=float, group="Vector Math",
    doc="Return the determinant of the matrix m")

add_builtin("diag", input_types={"d": vec2}, value_type=mat22, group="Vector Math",
    doc="Returns a matrix with the components of the vector d on the diagonal")
add_builtin("diag", input_types={"d": vec3}, value_type=mat33, group="Vector Math",
    doc="Returns a matrix with the components of the vector d on the diagonal")
add_builtin("diag", input_types={"d": vec4}, value_type=mat44, group="Vector Math",
    doc="Returns a matrix with the components of the vector d on the diagonal")

add_builtin("cw_mul", input_types={"x": vec2, "y": vec2}, value_type=vec2, group="Vector Math",
     doc="Component wise multiply of two 2d vectors.") 
add_builtin("cw_mul", input_types={"x": vec3, "y": vec3}, value_type=vec3, group="Vector Math",
     doc="Component wise multiply of two 3d vectors.") 
add_builtin("cw_mul", input_types={"x": vec4, "y": vec4}, value_type=vec4, group="Vector Math",
     doc="Component wise multiply of two 4d vectors.") 
add_builtin("cw_div", input_types={"x": vec2, "y": vec2}, value_type=vec2, group="Vector Math",
    doc="Component wise division of two 2d vectors.")
add_builtin("cw_div", input_types={"x": vec3, "y": vec3}, value_type=vec3, group="Vector Math",
    doc="Component wise division of two 3d vectors.")
add_builtin("cw_div", input_types={"x": vec4, "y": vec4}, value_type=vec3, group="Vector Math",
    doc="Component wise division of two 4d vectors.")

# type construtors for compute types (int, float)
for t in scalar_types:
    add_builtin("int", input_types={"x": t}, value_type=int, doc="Construct an 32-bit signed integer variable, larger precision types will be truncated.", hidden=True, group="Scalar Math")
    add_builtin("float", input_types={"x": t}, value_type=float, doc="Construct a 32-bit floating point variable, larger precision types will be truncated.", hidden=True, group="Scalar Math")

# type construtors for storage types 
for t in scalar_types:
    add_builtin(t.__name__, input_types={"x": int}, value_type=t, doc="", hidden=True, group="Scalar Math")
    add_builtin(t.__name__, input_types={"x": float}, value_type=t, doc="", hidden=True, group="Scalar Math")

add_builtin("vec2", input_types={}, value_type=vec2, doc="Construct a zero-initialized 2d vector.", group="Vector Math")
add_builtin("vec2", input_types={"x": float, "y": float }, value_type=vec2, doc="Construct a 2d vector with compontents x, y.", group="Vector Math")
add_builtin("vec2", input_types={"s": float}, value_type=vec2, doc="Construct a 2d vector with all components set to s.", group="Vector Math")

add_builtin("vec3", input_types={}, value_type=vec3, doc="Construct a zero-initialized 3d vector.", group="Vector Math")
add_builtin("vec3", input_types={"x": float, "y": float, "z": float}, value_type=vec3, doc="Construct a 3d vector with compontents x, y, z.", group="Vector Math")
add_builtin("vec3", input_types={"s": float}, value_type=vec3, doc="Construct a 3d vector with all components set to s.", group="Vector Math")

add_builtin("vec4", input_types={}, value_type=vec4, doc="Construct a zero-initialized 4d vector.", group="Vector Math")
add_builtin("vec4", input_types={"x": float, "y": float, "z": float, "w": float}, value_type=vec4, doc="Construct a 4d vector with compontents x, y, z, w.", group="Vector Math")
add_builtin("vec4", input_types={"s": float}, value_type=vec4, doc="Construct a 4d vector with all components set to s.", group="Vector Math")

add_builtin("mat22", input_types={"c0": vec2, "c1": vec2 }, value_type=mat22, doc="Construct a 2x2 matrix from column vectors c0, c1.", group="Vector Math")
add_builtin("mat22", input_types={"m00": float, "m01": float, "m10": float, "m11": float}, value_type=mat22, doc="Construct a 2x2 matrix from components.", group="Vector Math")

add_builtin("mat33", input_types={"c0": vec3, "c1": vec3, "c2": vec3 }, value_type=mat33, doc="Construct a 3x3 matrix from column vectors c0, c1, c2.", group="Vector Math")
add_builtin("mat33", input_types={"m00": float, "m01": float, "m02": float,
                                  "m10": float, "m11": float, "m12": float,
                                  "m20": float, "m21": float, "m22": float}, value_type=mat33, doc="Construct a 3x3 matrix from components.", group="Vector Math")

add_builtin("mat44", input_types={"c0": vec4, "c1": vec4, "c2": vec4, "c3": vec4 }, value_type=mat44, doc="Construct a 4x4 matrix from column vectors c0, c1, c2, c4.", group="Vector Math")
add_builtin("mat44", input_types={"m00": float, "m01": float, "m02": float, "m03": float,
                                  "m10": float, "m11": float, "m12": float, "m13": float,
                                  "m20": float, "m21": float, "m22": float, "m23": float,
                                  "m30": float, "m31": float, "m32": float, "m33": float}, value_type=mat44, doc="Construct a 4x4 matrix from components.", group="Vector Math")

add_builtin("mat44", input_types={"pos": vec3, "rot": quat, "scale": vec3}, value_type=mat44, 
    doc="""Construct a 4x4 transformation matrix that applies the transformations as Translation(pos)*Rotation(rot)*Scale(scale) when applied to column vectors, i.e.: y = (TRS)*x""", group="Vector Math")

add_builtin("svd3", input_types={"A": mat33, "U":mat33, "sigma":vec3, "V":mat33}, value_type=None, group="Vector Math",
    doc="""Compute the SVD of a 3x3 matrix. The singular values are returned in sigma, 
   while the left and right basis vectors are returned in U and V.""")

#---------------------------------
# Quaternion Math

add_builtin("quat", input_types={}, value_type=quat, group="Quaternion Math", 
    doc="""Construct a zero-initialized quaternion, quaternions are laid out as
   [ix, iy, iz, r], where ix, iy, iz are the imaginary part, and r the real part.""")
add_builtin("quat", input_types={"x": float, "y": float, "z": float, "w": float}, value_type=quat, group="Quaternion Math",
    doc="Construct a quarternion from its components x, y, z are the imaginary parts, w is the real part.")
add_builtin("quat", input_types={"i": vec3, "r": float}, value_type=quat, group="Quaternion Math",
    doc="Construct a quaternion from it's imaginary components i, and real part r")
add_builtin("quat_identity", input_types={}, value_type=quat, group="Quaternion Math",
    doc="Construct an identity quaternion with zero imaginary part and real part of 1.0")
add_builtin("quat_from_axis_angle", input_types={"axis": vec3, "angle": float}, value_type=quat, group="Quaternion Math",
    doc="Construct a quaternion representing a rotation of angle radians around the given axis.")
add_builtin("quat_from_matrix", input_types={"m": mat33}, value_type=quat, group="Quaternion Math",
    doc="Construct a quaternion from a 3x3 matrix.")
add_builtin("quat_inverse", input_types={"q": quat}, value_type=quat, group="Quaternion Math",
    doc="Compute quaternion conjugate.")
add_builtin("quat_rotate", input_types={"q": quat, "p": vec3}, value_type=vec3, group="Quaternion Math",
    doc="Rotate a vector by a quaternion.")
add_builtin("quat_rotate_inv", input_types={"q": quat, "p": vec3}, value_type=vec3, group="Quaternion Math",
    doc="Rotate a vector the inverse of a quaternion.")
add_builtin("quat_to_matrix", input_types={"q": quat}, value_type=mat33, group="Quaternion Math",
    doc="Convert a quaternion to a 3x3 rotation matrix.")

#---------------------------------
# Transformations 

add_builtin("transform", input_types={"p": vec3, "q": quat}, value_type=transform, group="Transformations",
    doc="Construct a rigid body transformation with translation part p and rotation q.")
add_builtin("transform_identity", input_types={}, value_type=transform, group="Transformations",
    doc="Construct an identity transform with zero translation and identity rotation.")
add_builtin("transform_get_translation", input_types={"t": transform}, value_type=vec3, group="Transformations",
    doc="Return the translational part of a transform.")
add_builtin("transform_get_rotation", input_types={"t": transform}, value_type=quat, group="Transformations",
    doc="Return the rotational part of a transform.")
add_builtin("transform_multiply", input_types={"a": transform, "b": transform}, value_type=transform, group="Transformations",
    doc="Multiply two rigid body transformations together.")
add_builtin("transform_point", input_types={"t": transform, "p": vec3}, value_type=vec3, group="Transformations",
    doc="Apply the transform to a point p treating the homogenous coordinate as w=1 (translation and rotation).")
add_builtin("transform_point", input_types={"m": mat44, "p": vec3}, value_type=vec3, group="Vector Math",
    doc="""Apply the transform to a point ``p`` treating the homogenous coordinate as w=1. The transformation is applied treating ``p`` as a column vector, e.g.: ``y = M*p``
   note this is in contrast to some libraries, notably USD, which applies transforms to row vectors, ``y^T = p^T*M^T``. If the transform is coming from a library that uses row-vectors
   then users should transpose the tranformation matrix before calling this method.""")
add_builtin("transform_vector", input_types={"t": transform, "v": vec3}, value_type=vec3, group="Transformations",
    doc="Apply the transform to a vector v treating the homogenous coordinate as w=0 (rotation only).")
add_builtin("transform_vector", input_types={"m": mat44, "v": vec3}, value_type=vec3, group="Vector Math",
    doc="""Apply the transform to a vector ``v`` treating the homogenous coordinate as w=0. The transformation is applied treating ``v`` as a column vector, e.g.: ``y = M*v``
   note this is in contrast to some libraries, notably USD, which applies transforms to row vectors, ``y^T = v^T*M^T``. If the transform is coming from a library that uses row-vectors
   then users should transpose the tranformation matrix before calling this method.""")
add_builtin("transform_inverse", input_types={"t": transform}, value_type=transform, group="Transformations",
    doc="Compute the inverse of the transform.")
#---------------------------------
# Spatial Math 

add_builtin("spatial_vector", input_types={}, value_type=spatial_vector, group="Spatial Math",
    doc="Construct a zero-initialized 6d screw vector. Screw vectors may be used to represent rigid body wrenches and twists (velocites).")
add_builtin("spatial_vector", input_types={"a": float, "b": float, "c": float, "d": float, "e": float, "f": float}, value_type=spatial_vector, group="Spatial Math",
    doc="Construct a 6d screw vector from it's components.")
add_builtin("spatial_vector", input_types={"w": vec3, "v": vec3}, value_type=spatial_vector, group="Spatial Math",
    doc="Construct a 6d screw vector from two 3d vectors.")
add_builtin("spatial_vector", input_types={"s": float}, value_type=spatial_vector, group="Spatial Math",
    doc="Construct a 6d screw vector with all components set to s")

add_builtin("spatial_matrix", input_types={}, value_type=spatial_matrix, group="Spatial Math",
    doc="Construct a 6x6 zero-initialized spatial inertia matrix")
add_builtin("spatial_adjoint", input_types={"r": mat33, "s": mat33}, value_type=spatial_matrix, group="Spatial Math",
    doc="Construct a 6x6 spatial inertial matrix from two 3x3 diagonal blocks.")

add_builtin("spatial_dot", input_types={"a": spatial_vector, "b": spatial_vector}, value_type=float, group="Spatial Math",
    doc="Compute the dot product of two 6d screw vectors.")
add_builtin("spatial_cross", input_types={"a": spatial_vector, "b": spatial_vector}, value_type=spatial_vector, group="Spatial Math",
    doc="Compute the cross-product of two 6d screw vectors.")
add_builtin("spatial_cross_dual", input_types={"a": spatial_vector, "b": spatial_vector}, value_type=spatial_vector, group="Spatial Math",
    doc="Compute the dual cross-product of two 6d screw vectors.")

add_builtin("spatial_top", input_types={"a": spatial_vector}, value_type=vec3, group="Spatial Math",
    doc="Return the top (first) part of a 6d screw vector.")
add_builtin("spatial_bottom", input_types={"a": spatial_vector}, value_type=vec3, group="Spatial Math",
    doc="Return the bottom (second) part of a 6d screw vector.")

add_builtin("spatial_jacobian",
     input_types={"S": array(dtype=spatial_vector), 
                  "joint_parents": array(dtype=int),
                  "joint_qd_start": array(dtype=int),
                  "joint_start": int,
                  "joint_count": int,
                  "J_start": int,
                  "J_out": array(dtype=float)}, value_type=None, doc="", group="Spatial Math")

add_builtin("spatial_mass", input_types={"I_s": array(dtype=spatial_matrix), "joint_start": int, "joint_count": int, "M_start": int, "M": array(dtype=float)}, value_type=None, doc="", group="Spatial Math")

#---------------------------------
# Linear Algebra

add_builtin("dense_gemm", 
    input_types={"m": int, 
                 "n": int, 
                 "p": int, 
                 "t1": int, 
                 "t2": int, 
                 "A": array(dtype=float), 
                 "B": array(dtype=float), 
                 "C": array(dtype=float) }, value_type=None, doc="", group="Utility", hidden=True)

add_builtin("dense_gemm_batched", 
    input_types={"m": array(dtype=int), 
                 "n": array(dtype=int), 
                 "p": array(dtype=int), 
                 "t1": int, 
                 "t2": int, 
                 "A_start": array(dtype=int), 
                 "B_start": array(dtype=int), 
                 "C_start": array(dtype=int), 
                 "A": array(dtype=float), 
                 "B": array(dtype=float), 
                 "C": array(dtype=float)}, value_type=None, doc="", group="Utility", hidden=True)


add_builtin("dense_chol",
    input_types={"n": int, 
                 "A": array(dtype=float), 
                 "regularization": float, 
                 "L": array(dtype=float)}, value_type=None, doc="WIP", group="Utility", hidden=True)

add_builtin("dense_chol_batched",
    input_types={"A_start": array(dtype=int),
                 "A_dim": array(dtype=int),
                 "A": array(dtype=float),
                 "regularization": float,
                 "L": array(dtype=float)}, value_type=None, doc="WIP", group="Utility", hidden=True)

add_builtin("dense_subs", 
    input_types={"n": int, 
                 "L": array(dtype=float), 
                 "b": array(dtype=float), 
                 "x": array(dtype=float)}, value_type=None, doc="WIP", group="Utility", hidden=True)

add_builtin("dense_solve", 
    input_types={"n": int, 
                 "A": array(dtype=float), 
                 "L": array(dtype=float), 
                 "b": array(dtype=float), 
                 "x": array(dtype=float)}, value_type=None, doc="WIP", group="Utility", hidden=True)

add_builtin("dense_solve_batched",
    input_types={"b_start": array(dtype=int), 
                 "A_start": array(dtype=int),
                 "A_dim": array(dtype=int),
                 "A": array(dtype=float),
                 "L": array(dtype=float),
                 "b": array(dtype=float),
                 "x": array(dtype=float)}, value_type=None, doc="WIP", group="Utility", hidden=True)


add_builtin("mlp", input_types={"weights": array(dtype=float, ndim=2), "bias": array(dtype=float, ndim=1), "activation": Callable, "index": int, "x": array(dtype=float, ndim=2), "out": array(dtype=float, ndim=2)}, value_type=None, skip_replay=True, 
    doc="""Evaluate a multi-layer perceptron (MLP) layer in the form: ``out = act(weights*x + bias)``. 

   :param weights: A layer's network weights with dimensions ``(m, n)``.
   :param bias: An array with dimensions ``(n)``.
   :param activation: A ``wp.func`` function that takes a single scalar float as input and returns a scalar float as output
   :param index: The batch item to process, typically each thread will process 1 item in the batch, in this case index should be ``wp.tid()``
   :param x: The feature matrix with dimensions ``(n, b)``
   :param out: The network output with dimensions ``(m, b)``

   :note: Feature and output matrices are transposed compared to some other frameworks such as PyTorch. All matrices are assumed to be stored in flattened row-major memory layout (NumPy default).""", group="Utility")


#---------------------------------
# Geometry

add_builtin("mesh_query_point", input_types={"id": uint64, "point": vec3, "max_dist": float, "inside": float, "face": int, "bary_u": float, "bary_v": float}, value_type=bool, group="Geometry",
    doc="""Computes the closest point on the mesh with identifier `id` to the given point in space. Returns ``True`` if a point < ``max_dist`` is found.

   :param id: The mesh identifier
   :param point: The point in space to query
   :param max_dist: Mesh faces above this distance will not be considered by the query
   :param inside: Returns a value < 0 if query point is inside the mesh, >=0 otherwise. Note that mesh must be watertight for this to be robust
   :param face: Returns the index of the closest face
   :param bary_u: Returns the barycentric u coordinate of the closest point
   :param bary_v: Retruns the barycentric v coordinate of the closest point""")

add_builtin("mesh_query_ray", input_types={"id": uint64, "start": vec3, "dir": vec3, "max_t": float, "t": float, "bary_u": float, "bary_v": float, "sign": float, "normal": vec3, "face": int}, value_type=bool, group="Geometry",
    doc="""Computes the closest ray hit on the mesh with identifier `id`, returns ``True`` if a point < ``max_t`` is found.

   :param id: The mesh identifier
   :param start: The start point of the ray
   :param dir: The ray direction (should be normalized)
   :param max_t: The maximum distance along the ray to check for intersections
   :param t: Returns the distance of the closest hit along the ray
   :param bary_u: Returns the barycentric u coordinate of the closest hit
   :param bary_v: Returns the barycentric v coordinate of the closest hit
   :param sign: Returns a value > 0 if the hit ray hit front of the face, returns < 0 otherwise
   :param normal: Returns the face normal
   :param face: Returns the index of the hit face""")

add_builtin("mesh_query_aabb", input_types={"id": uint64, "lower": vec3, "upper": vec3}, value_type=mesh_query_aabb_t, group="Geometry",
    doc="""Construct an axis-aligned bounding box query against a mesh object. This query can be used to iterate over all triangles
   inside a volume. Returns an object that is used to track state during mesh traversal.
    
   :param id: The mesh identifier
   :param lower: The lower bound of the bounding box in mesh space
   :param upper: The upper bound of the bounding box in mesh space""")

add_builtin("mesh_query_aabb_next", input_types={"query": mesh_query_aabb_t, "index": int}, value_type=bool, group="Geometry",
    doc="""Move to the next triangle overlapping the query bounding box. The index of the current face is stored in ``index``, returns ``False``
   if there are no more overlapping triangles.""")

add_builtin("mesh_eval_position", input_types={"id": uint64, "face": int, "bary_u": float, "bary_v": float}, value_type=vec3, group="Geometry",
    doc="""Evaluates the position on the mesh given a face index, and barycentric coordinates.""")

add_builtin("mesh_eval_velocity", input_types={"id": uint64, "face": int, "bary_u": float, "bary_v": float}, value_type=vec3, group="Geometry",
    doc="""Evaluates the velocity on the mesh given a face index, and barycentric coordinates.""")

add_builtin("hash_grid_query", input_types={"id": uint64, "point": vec3, "max_dist": float}, value_type=hash_grid_query_t, group="Geometry",
    doc="""Construct a point query against a hash grid. This query can be used to iterate over all neighboring points withing a 
   fixed radius from the query point. Returns an object that is used to track state during neighbor traversal.""")

add_builtin("hash_grid_query_next", input_types={"query": hash_grid_query_t, "index": int}, value_type=bool, group="Geometry",
    doc="""Move to the next point in the hash grid query. The index of the current neighbor is stored in ``index``, returns ``False``
   if there are no more neighbors.""")

add_builtin("hash_grid_point_id", input_types={"id": uint64, "index": int}, value_type=int, group="Geometry",
    doc="""Return the index of a point in the grid, this can be used to re-order threads such that grid 
   traversal occurs in a spatially coherent order.""")

add_builtin("intersect_tri_tri", input_types={"v0": vec3, "v1": vec3, "v2": vec3, "u0": vec3, "u1": vec3, "u2": vec3}, value_type=int, group="Geometry", 
    doc="Tests for intersection between two triangles (v0, v1, v2) and (u0, u1, u2) using Möller's method. Returns > 0 if triangles intersect.")

#---------------------------------
# Ranges

add_builtin("range", input_types={"end": int}, value_type=range_t, group="Utility", hidden=True)
add_builtin("range", input_types={"start": int, "end": int}, value_type=range_t, group="Utility", hidden=True)
add_builtin("range", input_types={"start": int, "end": int, "step": int}, value_type=range_t, group="Utility", hidden=True)

#---------------------------------
# Iterators

add_builtin("iter_next", input_types={"range": range_t}, value_type=int, group="Utility", hidden=True)
add_builtin("iter_next", input_types={"query": hash_grid_query_t}, value_type=int, group="Utility", hidden=True)
add_builtin("iter_next", input_types={"query": mesh_query_aabb_t}, value_type=int, group="Utility", hidden=True)

#---------------------------------
# Volumes 

add_builtin("volume_sample_f", input_types={"id": uint64, "uvw": vec3, "sampling_mode": int}, value_type=float, group="Volumes",
    doc="""Sample the volume given by ``id`` at the volume local-space point ``uvw``. Interpolation should be ``wp.Volume.CLOSEST``, or ``wp.Volume.LINEAR.``""")

add_builtin("volume_lookup_f", input_types={"id": uint64, "i": int, "j": int, "k": int}, value_type=float, group="Volumes",
    doc="""Returns the value of voxel with coordinates ``i``, ``j``, ``k``, if the voxel at this index does not exist this function returns the background value""")

add_builtin("volume_sample_v", input_types={"id": uint64, "uvw": vec3, "sampling_mode": int}, value_type=vec3, group="Volumes",
    doc="""Sample the vector volume given by ``id`` at the volume local-space point ``uvw``. Interpolation should be ``wp.Volume.CLOSEST``, or ``wp.Volume.LINEAR.``""")

add_builtin("volume_lookup_v", input_types={"id": uint64, "i": int, "j": int, "k": int}, value_type=vec3, group="Volumes",
    doc="""Returns the vector value of voxel with coordinates ``i``, ``j``, ``k``, if the voxel at this index does not exist this function returns the background value""")

add_builtin("volume_sample_i", input_types={"id": uint64, "uvw": vec3}, value_type=int, group="Volumes",
    doc="""Sample the int32 volume given by ``id`` at the volume local-space point ``uvw``. """)

add_builtin("volume_lookup_i", input_types={"id": uint64, "i": int, "j": int, "k": int}, value_type=int, group="Volumes",
    doc="""Returns the int32 value of voxel with coordinates ``i``, ``j``, ``k``, if the voxel at this index does not exist this function returns the background value""")

add_builtin("volume_index_to_world", input_types={"id": uint64, "uvw": vec3}, value_type=vec3, group="Volumes",
    doc="""Transform a point defined in volume index space to world space given the volume's intrinsic affine transformation.""")
add_builtin("volume_world_to_index", input_types={"id": uint64, "xyz": vec3}, value_type=vec3, group="Volumes",
    doc="""Transform a point defined in volume world space to the volume's index space, given the volume's intrinsic affine transformation.""")
add_builtin("volume_index_to_world_dir", input_types={"id": uint64, "uvw": vec3}, value_type=vec3, group="Volumes",
    doc="""Transform a direction defined in volume index space to world space given the volume's intrinsic affine transformation.""")
add_builtin("volume_world_to_index_dir", input_types={"id": uint64, "xyz": vec3}, value_type=vec3, group="Volumes",
    doc="""Transform a direction defined in volume world space to the volume's index space, given the volume's intrinsic affine transformation.""")


#---------------------------------
# Random 

add_builtin("rand_init", input_types={"seed": int}, value_type=uint32, group="Random", 
    doc="Initialize a new random number generator given a user-defined seed. Returns a 32-bit integer representing the RNG state.")

add_builtin("rand_init", input_types={"seed": int, "offset": int}, value_type=uint32, group="Random", 
    doc="""Initialize a new random number generator given a user-defined seed and an offset. 
   This alternative constructor can be useful in parallel programs, where a kernel as a whole should share a seed,
   but each thread should generate uncorrelated values. In this case usage should be ``r = rand_init(seed, tid)``""")

add_builtin("randi", input_types={"state": uint32}, value_type=int, group="Random", 
    doc="Return a random integer between [0, 2^32)")
add_builtin("randi", input_types={"state": uint32, "min": int, "max": int}, value_type=int, group="Random", 
    doc="Return a random integer between [min, max)")
add_builtin("randf", input_types={"state": uint32}, value_type=float, group="Random", 
    doc="Return a random float between [0.0, 1.0)")
add_builtin("randf", input_types={"state": uint32, "min": float, "max": float}, value_type=float, group="Random", 
    doc="Return a random float between [min, max)")
add_builtin("randn", input_types={"state": uint32}, value_type=float, group="Random", 
    doc="Sample a normal distribution")

add_builtin("noise", input_types={"state": uint32, "x": float}, value_type=float, group="Random",
    doc="Non-periodic Perlin-style noise in 1d.")
add_builtin("noise", input_types={"state": uint32, "xy": vec2}, value_type=float, group="Random",
    doc="Non-periodic Perlin-style noise in 2d.")
add_builtin("noise", input_types={"state": uint32, "xyz": vec3}, value_type=float, group="Random",
    doc="Non-periodic Perlin-style noise in 3d.")
add_builtin("noise", input_types={"state": uint32, "xyzt": vec4}, value_type=float, group="Random",
    doc="Non-periodic Perlin-style noise in 4d.")

add_builtin("pnoise", input_types={"state": uint32, "x": float, "px": int}, value_type=float, group="Random",
    doc="Periodic Perlin-style noise in 1d.")
add_builtin("pnoise", input_types={"state": uint32, "xy": vec2, "px": int, "py": int}, value_type=float, group="Random",
    doc="Periodic Perlin-style noise in 2d.")
add_builtin("pnoise", input_types={"state": uint32, "xyz": vec3, "px": int, "py": int, "pz": int}, value_type=float, group="Random",
    doc="Periodic Perlin-style noise in 3d.")
add_builtin("pnoise", input_types={"state": uint32, "xyzt": vec4, "px": int, "py": int, "pz": int, "pt": int}, value_type=float, group="Random",
    doc="Periodic Perlin-style noise in 4d.")

add_builtin("curlnoise", input_types={"state": uint32, "xy": vec2}, value_type=vec2, group="Random",
    doc="Divergence-free vector field based on the gradient of a Perlin noise function.")
add_builtin("curlnoise", input_types={"state": uint32, "xyz": vec3}, value_type=vec3, group="Random",
    doc="Divergence-free vector field based on the curl of three Perlin noise functions.")
add_builtin("curlnoise", input_types={"state": uint32, "xyzt": vec4}, value_type=vec3, group="Random",
    doc="Divergence-free vector field based on the curl of three Perlin noise functions.")

# note printf calls directly to global CRT printf (no wp:: namespace prefix)
add_builtin("printf", input_types={}, namespace="", variadic=True, group="Utility",
    doc="Allows printing formatted strings, using C-style format specifiers.")

add_builtin("print", input_types={"value": Any}, doc="Print variable to stdout", group="Utility")

# helpers
add_builtin("tid", input_types={}, value_type=int, group="Utility",
    doc="""Return the current thread index. Note that this is the *global* index of the thread in the range [0, dim) 
   where dim is the parameter passed to kernel launch.""")

add_builtin("tid", input_types={}, value_type=[int, int], group="Utility",
    doc="""Return the current thread indices for a 2d kernel launch. Use ``i,j = wp.tid()`` syntax to retrieve the coordinates inside the kernel thread grid.""")

add_builtin("tid", input_types={}, value_type=[int, int, int], group="Utility",
    doc="""Return the current thread indices for a 3d kernel launch. Use ``i,j,k = wp.tid()`` syntax to retrieve the coordinates inside the kernel thread grid.""")

add_builtin("tid", input_types={}, value_type=[int, int, int, int], group="Utility",
    doc="""Return the current thread indices for a 4d kernel launch. Use ``i,j,k,l = wp.tid()`` syntax to retrieve the coordinates inside the kernel thread grid.""")


add_builtin("copy", variadic=True, hidden=True, group="Utility")
add_builtin("select", input_types={"cond": bool, "arg1": Any, "arg2": Any}, value_func=lambda args: args[1].type, doc="Select between two arguments, if cond is false then return ``arg1``, otherwise return ``arg2``", group="Utility")

# does argument checking and type progagation for load()
def load_value_func(args):

    if (type(args[0].type) != array):
        raise RuntimeError("load() argument 0 must be an array")

    num_indices = len(args[1:])
    num_dims = args[0].type.ndim

    if num_indices < num_dims:
        raise RuntimeError("Num indices < num dimensions for array load, this is a codegen error, should have generated a view instead")

    if num_indices > num_dims:
        raise RuntimeError(f"Num indices > num dimensions for array load, received {num_indices}, but array only has {num_dims}")

    # check index types
    for a in args[1:]:
        if type_is_int(a.type) == False:
            raise RuntimeError(f"load() index arguments must be of integer type, got index of type {a.type}")

    return args[0].type.dtype

# does argument checking and type progagation for view()
def view_value_func(args):
    if (type(args[0].type) != array):
        raise RuntimeError("view() argument 0 must be an array")

    # check array dim big enough to support view
    num_indices = len(args[1:])
    num_dims = args[0].type.ndim

    if num_indices >= num_dims:
        raise RuntimeError(f"Trying to create an array view with {num_indices} indices, but array only has {num_dims} dimensions.")

    # check index types
    for a in args[1:]:
        if type_is_int(a.type) == False:
            raise RuntimeError(f"view() index arguments must be of integer type, got index of type {a.type}")

    # create an array view with leading dimensions removed
    import copy
    view_type = copy.copy(args[0].type)
    view_type.ndim -= num_indices
    
    return view_type

# does argument checking and type progagation for store()
def store_value_func(args):
    # check target type
    if (type(args[0].type) != array):
        raise RuntimeError("store() argument 0 must be an array")
    
    num_indices = len(args[1:-1])
    num_dims = args[0].type.ndim

    # if this happens we should have generated a view instead of a load during code gen
    if num_indices < num_dims:
        raise RuntimeError("Num indices < num dimensions for array store")

    if num_indices > num_dims:
        raise RuntimeError(f"Num indices > num dimensions for array store, received {num_indices}, but array only has {num_dims}")

    # check index types
    for a in args[1:-1]:
        if type_is_int(a.type) == False:
            raise RuntimeError(f"store() index arguments must be of integer type, got index of type {a.type}")

    # check value type
    if (args[-1].type != args[0].type.dtype):
        raise RuntimeError(f"store() value argument type ({args[2].type}) must be of the same type as the array ({args[0].type.dtype})")

    return None


add_builtin("load", variadic=True, hidden=True, value_func=load_value_func, group="Utility")
add_builtin("view", variadic=True, hidden=True, value_func=view_value_func, group="Utility")
add_builtin("store", variadic=True, hidden=True, value_func=store_value_func, skip_replay=True, group="Utility")

def atomic_op_value_type(args):

    # check target type
    if (type(args[0].type) != array):
        raise RuntimeError("atomic() operation argument 0 must be an array")
    
    num_indices = len(args[1:-1])
    num_dims = args[0].type.ndim

    # if this happens we should have generated a view instead of a load during code gen
    if num_indices < num_dims:
        raise RuntimeError("Num indices < num dimensions for atomic array operation")

    if num_indices > num_dims:
        raise RuntimeError(f"Num indices > num dimensions for atomic array operation, received {num_indices}, but array only has {num_dims}")

    # check index types
    for a in args[1:-1]:
        if type_is_int(a.type) == False:
            raise RuntimeError(f"atomic() operation index arguments must be of integer type, got index of type {a.type}")

    if (args[-1].type != args[0].type.dtype):
        raise RuntimeError(f"atomic() value argument ({args[-1].type}) must be of the same type as the array ({args[0].type.dtype})")

    return args[0].type.dtype


add_builtin("atomic_add", input_types={"a": array(dtype=Any), "i": int, "value": Any}, value_func=atomic_op_value_type, doc="Atomically add ``value`` onto the array at location given by index.", group="Utility", skip_replay=True)
add_builtin("atomic_add", input_types={"a": array(dtype=Any), "i": int, "j": int, "value": Any}, value_func=atomic_op_value_type, doc="Atomically add ``value`` onto the array at location given by indices.", group="Utility", skip_replay=True)
add_builtin("atomic_add", input_types={"a": array(dtype=Any), "i": int, "j": int, "k": int, "value": Any}, value_func=atomic_op_value_type, doc="Atomically add ``value`` onto the array at location given by indices.", group="Utility", skip_replay=True)
add_builtin("atomic_add", input_types={"a": array(dtype=Any), "i": int, "j": int, "k": int, "l": int, "value": Any}, value_type=atomic_op_value_type, doc="Atomically add ``value`` onto the array at location given by indices.", group="Utility", skip_replay=True)

add_builtin("atomic_sub", input_types={"a": array(dtype=Any), "i": int, "value": Any}, value_func=atomic_op_value_type, doc="Atomically subtract ``value`` onto the array at location given by index.", group="Utility", skip_replay=True)
add_builtin("atomic_sub", input_types={"a": array(dtype=Any), "i": int, "j": int, "value": Any}, value_func=atomic_op_value_type, doc="Atomically subtract ``value`` onto the array at location given by indices.", group="Utility", skip_replay=True)
add_builtin("atomic_sub", input_types={"a": array(dtype=Any), "i": int, "j": int, "k":int, "value": Any}, value_func=atomic_op_value_type, doc="Atomically subtract ``value`` onto the array at location given by indices.", group="Utility", skip_replay=True)
add_builtin("atomic_sub", input_types={"a": array(dtype=Any), "i": int, "j": int, "k":int, "l": int, "value": Any}, value_func=atomic_op_value_type, doc="Atomically subtract ``value`` onto the array at location given by indices.", group="Utility", skip_replay=True)


# used to index into builtin types, i.e.: y = vec3[1]
add_builtin("index", variadic=True, hidden=True, value_type=float, group="Utility")

for t in scalar_types + vector_types:
    add_builtin("expect_eq", input_types={"arg1": t, "arg2": t}, value_type=None, doc="Prints an error to stdout if arg1 and arg2 are not equal", group="Utility")

# fuzzy compare for float values
add_builtin("expect_near", input_types={"arg1": float, "arg2": float, "tolerance": float}, value_type=None, doc="Prints an error to stdout if arg1 and arg2 are not closer than tolerance in magnitude", group="Utility")
add_builtin("expect_near", input_types={"arg1": vec3, "arg2": vec3, "tolerance": float}, value_type=None, doc="Prints an error to stdout if any element of arg1 and arg2 are not closer than tolerance in magnitude", group="Utility")

#---------------------------------
# Operators

add_builtin("add", input_types={"x": int, "y": int}, value_type=int, doc="", group="Operators")
add_builtin("add", input_types={"x": float, "y": float}, value_type=float, doc="", group="Operators")
add_builtin("add", input_types={"x": vec2, "y": vec2}, value_type=vec2, doc="", group="Operators")
add_builtin("add", input_types={"x": vec3, "y": vec3}, value_type=vec3, doc="", group="Operators")
add_builtin("add", input_types={"x": vec4, "y": vec4}, value_type=vec4, doc="", group="Operators")
add_builtin("add", input_types={"x": quat, "y": quat}, value_type=quat, doc="", group="Operators")
add_builtin("add", input_types={"x": mat22, "y": mat22}, value_type=mat22, doc="", group="Operators")
add_builtin("add", input_types={"x": mat33, "y": mat33}, value_type=mat33, doc="", group="Operators")
add_builtin("add", input_types={"x": mat44, "y": mat44}, value_type=mat44, doc="", group="Operators")
add_builtin("add", input_types={"x": spatial_vector, "y": spatial_vector}, value_type=spatial_vector, doc="", group="Operators")
add_builtin("add", input_types={"x": spatial_matrix, "y": spatial_matrix}, value_type=spatial_matrix, doc="", group="Operators")

add_builtin("sub", input_types={"x": int, "y": int}, value_type=int, doc="", group="Operators")
add_builtin("sub", input_types={"x": float, "y": float}, value_type=float, doc="", group="Operators")
add_builtin("sub", input_types={"x": vec2, "y": vec2}, value_type=vec2, doc="", group="Operators")
add_builtin("sub", input_types={"x": vec3, "y": vec3}, value_type=vec3, doc="", group="Operators")
add_builtin("sub", input_types={"x": vec4, "y": vec4}, value_type=vec4, doc="", group="Operators")
add_builtin("sub", input_types={"x": mat22, "y": mat22}, value_type=mat22, doc="", group="Operators")
add_builtin("sub", input_types={"x": mat33, "y": mat33}, value_type=mat33, doc="", group="Operators")
add_builtin("sub", input_types={"x": mat44, "y": mat44}, value_type=mat44, doc="", group="Operators")
add_builtin("sub", input_types={"x": spatial_vector, "y": spatial_vector}, value_type=spatial_vector, doc="", group="Operators")
add_builtin("sub", input_types={"x": spatial_matrix, "y": spatial_matrix}, value_type=spatial_matrix, doc="", group="Operators")

add_builtin("mul", input_types={"x": int, "y": int}, value_type=int, doc="", group="Operators")
add_builtin("mul", input_types={"x": float, "y": float}, value_type=float, doc="", group="Operators")
add_builtin("mul", input_types={"x": float, "y": vec2}, value_type=vec2, doc="", group="Operators")
add_builtin("mul", input_types={"x": float, "y": vec3}, value_type=vec3, doc="", group="Operators")
add_builtin("mul", input_types={"x": float, "y": vec4}, value_type=vec4, doc="", group="Operators")
add_builtin("mul", input_types={"x": float, "y": quat}, value_type=quat, doc="", group="Operators")
add_builtin("mul", input_types={"x": vec2, "y": float}, value_type=vec2, doc="", group="Operators")
add_builtin("mul", input_types={"x": vec3, "y": float}, value_type=vec3, doc="", group="Operators")
add_builtin("mul", input_types={"x": vec4, "y": float}, value_type=vec4, doc="", group="Operators")
add_builtin("mul", input_types={"x": quat, "y": float}, value_type=quat, doc="", group="Operators")
add_builtin("mul", input_types={"x": quat, "y": quat}, value_type=quat, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat22, "y": float}, value_type=mat22, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat22, "y": vec2}, value_type=vec2, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat22, "y": mat22}, value_type=mat22, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat33, "y": float}, value_type=mat33, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat33, "y": vec3}, value_type=vec3, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat33, "y": mat33}, value_type=mat33, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat44, "y": float}, value_type=mat44, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat44, "y": vec4}, value_type=vec4, doc="", group="Operators")
add_builtin("mul", input_types={"x": mat44, "y": mat44}, value_type=mat44, doc="", group="Operators")
add_builtin("mul", input_types={"x": spatial_vector, "y": float}, value_type=spatial_vector, doc="", group="Operators")
add_builtin("mul", input_types={"x": spatial_matrix, "y": spatial_matrix}, value_type=spatial_matrix, doc="", group="Operators")
add_builtin("mul", input_types={"x": spatial_matrix, "y": spatial_vector}, value_type=spatial_vector, doc="", group="Operators")
add_builtin("mul", input_types={"x": transform, "y": transform}, value_type=transform, doc="", group="Operators")

add_builtin("mod", input_types={"x": int, "y": int}, value_type=int, doc="", group="Operators")
add_builtin("mod", input_types={"x": float, "y": float}, value_type=float, doc="", group="operators")

add_builtin("div", input_types={"x": int, "y": int}, value_type=int, doc="", group="Operators")
add_builtin("div", input_types={"x": float, "y": float}, value_type=float, doc="", group="Operators")
add_builtin("div", input_types={"x": vec2, "y": float}, value_type=vec2, doc="", group="Operators")
add_builtin("div", input_types={"x": vec3, "y": float}, value_type=vec3, doc="", group="Operators")
add_builtin("div", input_types={"x": vec4, "y": float}, value_type=vec4, doc="", group="Operators")

add_builtin("floordiv", input_types={"x": int, "y": int}, value_type=int, doc="", group="Operators")
add_builtin("floordiv", input_types={"x": float, "y": float}, value_type=float, doc="", group="Operators")

add_builtin("neg", input_types={"x": int}, value_type=int, doc="", group="Operators")
add_builtin("neg", input_types={"x": float}, value_type=float, doc="", group="Operators")
add_builtin("neg", input_types={"x": vec2}, value_type=vec2, doc="", group="Operators")
add_builtin("neg", input_types={"x": vec3}, value_type=vec3, doc="", group="Operators")
add_builtin("neg", input_types={"x": vec4}, value_type=vec4, doc="", group="Operators")
add_builtin("neg", input_types={"x": quat}, value_type=quat, doc="", group="Operators")
add_builtin("neg", input_types={"x": mat33}, value_type=mat33, doc="", group="Operators")
add_builtin("neg", input_types={"x": mat44}, value_type=mat44, doc="", group="Operators")

add_builtin("unot", input_types={"b": bool}, value_type=bool, doc="", group="Operators")
