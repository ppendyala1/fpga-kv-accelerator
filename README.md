# FPGA KV-cache accelerator

A single-head INT8 attention accelerator for the **Digilent Arty A7-100T**.
It stores up to 512 key/value vectors, each with 64 dimensions, and supports
both score-buffered baseline and streaming attention.

**Status:** RTL verification and 100 MHz routed timing pass. A bitstream has
been generated. **Physical FPGA testing is still pending.**

Repository upload is in progress. Some commands and linked files below will
become available in later commits.

## Try the software model

Run from the project folder; no FPGA or Docker is needed:

```powershell
python -m pip install -r requirements.txt
python -m host.demo --tokens 32
python -m pytest -q
```

The demo checks the software backend against the fixed-point model. It does
not measure FPGA performance. See [verification](docs/verification.md) for RTL
simulation and [hardware setup](docs/hardware.md) for testing a real board.

## Build the FPGA bitstream

With Vivado 2022.2 installed on Windows:

```powershell
powershell -File scripts/build.ps1
```

The output is `build/vivado/top.bit`. Follow the [hardware guide](docs/hardware.md)
to check timing, program the board, and run the serial demo.

## Project layout

| Folder | Contents |
|---|---|
| `rtl/` | Cache, attention datapath, controller, and UART |
| `models/`, `host/` | Numerical references and Python driver |
| `tb/`, `tests/` | RTL testbenches and Python tests |
| `scripts/`, `constraints/` | Simulation/build tools and board constraints |
| `docs/` | Architecture, numerical formats, protocol, and setup |
| `results/` | Summaries, metrics, and compressed raw evidence |

## Results and design details

[Validation status](results/status.md) and [benchmarks](results/benchmark.md)
separate RTL simulation, calculated latency/bandwidth, and Vivado reports.
**There are no physical-board performance measurements yet.** Original logs
and reports are in `results/evidence.zip`, verified by `results/manifest.json`.

Read the [architecture](docs/architecture.md), [numerical specification](docs/numerical_formats.md),
[UART protocol](docs/protocol.md), and [limitations](docs/limitations.md) for details.
