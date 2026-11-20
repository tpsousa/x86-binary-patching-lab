#!/usr/bin/env python3
"""Compara SHA-256 e CheckSum do cabeçalho PE de um ou mais executáveis.

Uso:
    python3 check_integrity.py original/unbreak_windows.exe trabalho/unbreak_windows_patched.exe

Para a assinatura Authenticode, use também:
    osslsigncode verify <arquivo.exe>
"""
import hashlib
import sys

import pefile


def sha256_of(path: str) -> str:
    
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <arquivo.exe> [outro.exe ...]", file=sys.stderr)
        return 1

    for path in sys.argv[1:]:
        pe = pefile.PE(path)
        stored = pe.OPTIONAL_HEADER.CheckSum
        computed = pe.generate_checksum()
        valid = "Sim" if stored == computed else "Não"

        print(path)
        print(f"  SHA-256:             {sha256_of(path)}")
        print(f"  CheckSum armazenado: {hex(stored)}")
        print(f"  CheckSum calculado:  {hex(computed)}")
        print(f"  CheckSum válido?     {valid}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())