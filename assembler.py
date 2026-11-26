#!/usr/bin/env python3
"""Two-pass assembler for the Hack platform.

Usage: python3 assembler.py Program.asm [-o Program.hack]
It also writes symbols.txt next to the output file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
    **{f"R{i}": i for i in range(16)},
}
DEST = {"": "000", "M": "001", "D": "010", "MD": "011", "A": "100",
        "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}
COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100",
    "A": "0110000", "!D": "0001101", "!A": "0110001", "-D": "0001111",
    "-A": "0110011", "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011", "A-D": "0000111",
    "D&A": "0000000", "D|A": "0010101", "M": "1110000", "!M": "1110001",
    "-M": "1110011", "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
    "D-M": "1010011", "M-D": "1000111", "D&M": "1000000", "D|M": "1010101",
}


class AssemblyError(Exception):
    pass


def cleaned_lines(path: Path):
    """Yield (original line number, instruction) after comments/blanks vanish."""
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        code = raw.split("//", 1)[0].strip().replace(" ", "").replace("\t", "")
        if code:
            yield number, code


def valid_symbol(symbol: str) -> bool:
    return bool(symbol) and (symbol[0].isalpha() or symbol[0] in "_.$:") and all(
        c.isalnum() or c in "_.$:" for c in symbol
    )


def first_pass(lines):
    symbols = dict(PREDEFINED)
    rom = 0
    warnings = []
    for line_no, code in lines:
        if code.startswith("(") or code.endswith(")"):
            if not (code.startswith("(") and code.endswith(")")):
                raise AssemblyError(f"Line {line_no}: invalid label")
            label = code[1:-1]
            if not valid_symbol(label):
                raise AssemblyError(f"Line {line_no}: invalid label '{label}'")
            if label in symbols:
                warnings.append(f"Line {line_no}: warning: label '{label}' is already defined")
            else:
                symbols[label] = rom
        else:
            rom += 1
    return symbols, warnings


def encode_c(code: str, line_no: int) -> str:
    if code.count("=") > 1 or code.count(";") > 1:
        raise AssemblyError(f"Line {line_no}: invalid instruction")
    left, sep, jump = code.partition(";")
    dest, eq, comp = left.partition("=")
    if not eq:
        comp, dest = left, ""
    if not comp or comp not in COMP or dest not in DEST or jump not in JUMP:
        raise AssemblyError(f"Line {line_no}: invalid instruction '{code}'")
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def second_pass(lines, symbols):
    output, next_ram = [], 16
    for line_no, code in lines:
        if code.startswith("(") and code.endswith(")"):
            continue
        if code.startswith("@"):
            operand = code[1:]
            if operand.isdecimal():
                value = int(operand)
                if value > 32767:
                    raise AssemblyError(f"Line {line_no}: address out of range")
            elif valid_symbol(operand):
                if operand not in symbols:
                    symbols[operand] = next_ram
                    next_ram += 1
                value = symbols[operand]
            else:
                raise AssemblyError(f"Line {line_no}: invalid A-instruction '{code}'")
            output.append(f"{value:016b}")
        else:
            output.append(encode_c(code, line_no))
    return output


def assemble(source: Path, destination: Path) -> None:
    lines = list(cleaned_lines(source))
    symbols, warnings = first_pass(lines)
    machine = second_pass(lines, symbols)
    destination.write_text("\n".join(machine) + ("\n" if machine else ""), encoding="utf-8")
    (destination.parent / "symbols.txt").write_text(
        "\n".join(f"{name} {value}" for name, value in sorted(symbols.items())) + "\n",
        encoding="utf-8",
    )
    for warning in warnings:
        print(warning, file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble a Hack .asm file")
    parser.add_argument("source", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.source.with_suffix(".hack")
    try:
        assemble(args.source, output)
    except (OSError, AssemblyError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
