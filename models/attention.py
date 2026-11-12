"""Attention operand validation and quantization."""

import numpy as np

def inputs(q, k, v):
    arrays=[np.asarray(a) for a in (q,k,v)]
    q,k,v = arrays
    if q.shape != (64,) or k.ndim != 2 or k.shape[1:] != (64,) or v.shape != k.shape:
        raise ValueError('expected q[64], k[n,64], v[n,64]')
    if any(a.dtype.kind not in 'biuf' for a in arrays):
        raise ValueError('operands must be finite integers')
    if not 1 <= len(k) <= 512 or any(np.any((a < -128) | (a > 127)) for a in (q,k,v)):
        raise ValueError('empty/full cache or INT8 range violation')
    if any(not np.all(np.isfinite(a)) or np.any(a!=np.floor(a)) for a in arrays):
        raise ValueError('operands must be finite integers')
    return tuple(a.astype(np.int64) for a in arrays)

def quantize(real):
    """Quantize finite real values at scale 1/16; ties round toward +infinity."""
    real=np.asarray(real)
    if real.dtype.kind not in 'biuf' or not np.all(np.isfinite(real)):
        raise ValueError('quantization inputs must be finite real numbers')
    scaled=np.clip(real,-8,127/16)*16
    return np.floor(scaled+0.5).astype(np.int8)
