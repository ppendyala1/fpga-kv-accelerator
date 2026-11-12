import numpy as np
import pytest
from models.attention import inputs, quantize


@pytest.mark.parametrize('n', [1, 512])
def test_valid_boundaries(n):
    q=np.full(64,-128,dtype=np.int8)
    k=np.full((n,64),127,dtype=np.int8)
    result=inputs(q,k,k)
    assert all(a.dtype==np.int64 for a in result)
    assert np.array_equal(result[0],q)
    assert np.array_equal(result[1],k)


@pytest.mark.parametrize('n', [0, 513])
def test_cache_bounds(n):
    with pytest.raises(ValueError):
        inputs(np.zeros(64),np.zeros((n,64)),np.zeros((n,64)))


@pytest.mark.parametrize('value', [-129, 128, 0.25, np.nan, np.inf, -np.inf])
@pytest.mark.parametrize('operand', [0, 1, 2])
def test_invalid_operand_values(value,operand):
    operands=[np.zeros(64),np.zeros((1,64)),np.zeros((1,64))]
    operands[operand].flat[0]=value
    with pytest.raises(ValueError):
        inputs(*operands)


def test_unsigned_values_cannot_wrap_into_int8_range():
    huge=np.full(64,np.iinfo(np.uint64).max,dtype=np.uint64)
    with pytest.raises(ValueError):
        inputs(huge,np.zeros((1,64)),np.zeros((1,64)))


@pytest.mark.parametrize('q,k,v', [
    (np.zeros(63),np.zeros((1,64)),np.zeros((1,64))),
    (np.zeros(64),np.zeros(64),np.zeros((1,64))),
    (np.zeros(64),np.zeros((1,64)),np.zeros((2,64))),
])
def test_shapes(q,k,v):
    with pytest.raises(ValueError):
        inputs(q,k,v)


def test_quantization_scale_ties_and_saturation():
    real=np.array([-1e308,-8,-1/32,0,1/32,1/16,127/16,1e308])
    with np.errstate(over='raise',invalid='raise'):
        result=quantize(real)
    assert result.dtype==np.int8
    assert result.tolist()==[-128,-128,0,0,1,1,127,127]


@pytest.mark.parametrize('value', [np.nan,np.inf,-np.inf,1j,'not a number'])
def test_quantization_rejects_nonreal_or_nonfinite_values(value):
    with pytest.raises(ValueError):
        quantize([value])
