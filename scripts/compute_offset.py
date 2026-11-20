#!/usr/bin/env python3
"""Converte um endereço virtual (VA) de um PE em offset dentro do arquivo.

Uso:
    python3 compute_offset.py unbreak_windows.exe 0x00401542
"""
import sys

import pefile


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Uso: {sys.argv[0]} <arquivo.exe> <endereco_virtual_hex>", file=sys.stderr)
        return 1

    path, va_str = sys.argv[1], sys.argv[2]
    va = int(va_str, 16)

    pe = pefile.PE(path)
    image_base = pe.OPTIONAL_HEADER.ImageBase
    rva = va - image_base
    offset = pe.get_offset_from_rva(rva)

    print(f"ImageBase:       {hex(image_base)}")
    print(f"VA:              {hex(va)}")
    print(f"RVA:             {hex(rva)}")
    print(f"Offset no arquivo: {hex(offset)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())