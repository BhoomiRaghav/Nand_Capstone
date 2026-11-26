# Capstone Hack Computer

This folder contains the Part A computer integration, Part B two-pass assembler,
and Part C keyboard-controlled screen box.

## Run the assembler

```sh
python3 assembler.py Box.asm
```

The command creates `Box.hack` and `symbols.txt`.  The assembler accepts any
Hack `.asm` file and reports source errors as `Line N: ...` rather than showing a
Python traceback.  It also prints a warning if a label is defined more than once.

## Built-in chips used in Part A

`CPU.hdl`, `Memory.hdl`, and `Computer.hdl` use the supplied Hardware Simulator
implementations of `ALU`, `ARegister`, `DRegister`, `PC`, `RAM16K`, `Screen`,
`Keyboard`, and `ROM32K`.  This is intentional integration of the verified
course primitives; no unverified older lab implementation is required.

## Box configuration

`Box.asm` currently demonstrates **K = 0**.  Set the two row-start calculations
and the number of consecutive screen words written per row for the assigned K:

| K | start increment | words per row | row increment |
|---:|---:|---:|---:|
| K | `32 * K` | `(K mod 4) + 1` | `32` after the final word |

For example, K = 5 starts at `SCREEN + 160`, writes two consecutive words per
row, and advances to the next screen row. Both the draw and clear loops must
use the same values.
# Nand_Capstone
