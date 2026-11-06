# FPGA KV-cache and streaming attention accelerator

Repository setup for a single-head INT8 decode-attention accelerator targeting
the Digilent Arty A7-100T: 64 dimensions, up to 512 KV-cache entries and eight
compute lanes.

The implementation already exists locally and is being organized into
reviewable commits. This initial commit contains repository configuration and
project scope. RTL, host software, tests and validation evidence will follow.

The local project includes baseline and streaming attention, fixed-point
reference models, CRC-protected UART control and a Vivado build flow. Physical
FPGA validation remains pending. No project license has been selected.
