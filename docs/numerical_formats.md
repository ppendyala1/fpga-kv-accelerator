# Numerical contract, version 1

Head dimension is fixed at 64; lanes divide 64. Capacity defaults to 512.
Q and K are signed INT8 with real scale 1/16; V and output have scale 1/16.
Thus the real attention score is integer dot / 2048. Accumulation is signed
32 bits (64 * 16384 fits). Scores are signed Q24.8: arithmetic dot >> 3,
rounding toward negative infinity. No pre-dot saturation occurs.

exp(x), x <= 0, is unsigned Q1.16 (17 bits, unity = 65536).
Index = min(256, ((-x_Q8)+8)>>4); table[i] = floor(exp(-i/16)*65536+0.5).
Differences >= 4096 return zero. LUT entries become zero before the cutoff.
The LUT is generated and checked into RTL; no runtime real arithmetic.

Running maximum uses signed 32-bit score units. Normalization l is unsigned
32 bits Q16; weighted u is signed 40 bits Q16 in V integer units.
Every rescale rounds via (product + 32768) arithmetic >> 16; signed ties
round toward positive infinity. The model uses unbounded integers; RTL retains
the exact product bits needed, splitting weighted products before rounding.
Conservative bounds, allowing one rounding unit per token, are
l <= 512*(65536+1) and |u| <= 512*(128*65536+1), within these widths.
First token sets alpha=0, beta=65536, without a sentinel subtraction.
Final output divides |u|+floor(l/2) by l, reapplies sign (ties away from zero),
and saturates to [-128,127]. A shared restoring divider handles normalization.

Baseline uses a score buffer and global maximum, then accumulates weights.
Streaming rescales at every new maximum. Both follow this contract, but their
outputs need not be equal because recurrence rounding and LUT composition
are not associative. Each must match its own bit-accurate model exactly.

Accuracy characterization uses deterministic full INT8 and normal(0,24)
inputs, lengths 1..512, reporting integer-output MAE/max error versus NumPy.
Exact RTL/model agreement is mandatory; floating-point error is measured,
not hidden behind an arbitrary universal tolerance. Input quantization error
is separate from hardware arithmetic error. No accuracy guarantee is made
for an untested model distribution.

Measured characterization (`python -m scripts.accuracy --trials 1000`, seed
2026, lengths sampled from 1/8/16/32/64/128/256/512) produced these errors in
integer output units; divide by 16 for real V units:

| Inputs | Mode | Mean absolute error | Worst absolute error |
|---|---|---:|---:|
| normal(0,24), clipped/rounded INT8 | streaming | 0.2213 | 1.0019 |
| normal(0,24), clipped/rounded INT8 | baseline | 0.2192 | 0.9903 |
| uniform full INT8 | streaming | 0.1479 | 2.1681 |
| uniform full INT8 | baseline | 0.1475 | 2.1681 |

These are 1,000 vectors per distribution, each containing 64 output elements.
They measure arithmetic error relative to attention on already-quantized
operands. They are neither an unquantized-model accuracy study nor a worst-case
error proof. Exact values and worst-case reproduction indices are in
results/accuracy.json. LUT exponent error and score truncation are included.
