#!/usr/bin/env bash
# Aplica o patch do laboratório: troca JNZ (75 0A) por NOP NOP (90 90)
# no endereço virtual 0x00401542 (offset de arquivo 0x942).
#
# Uso: ./apply_patch.sh unbreak_windows.exe unbreak_windows_patched.exe

set -euo pipefail

ORIGINAL="${1:-}"
PATCHED="${2:-}"
OFFSET=$((0x942))
EXPECTED_SHA256="2cfebab1adbe342ed177aa14e5044d51194b310614709af0d2495b4a741d01ce"

if [[ -z "$ORIGINAL" || -z "$PATCHED" ]]; then
    echo "Uso: $0 <executavel_original> <executavel_patchado>" >&2
    exit 1
fi

if [[ ! -f "$ORIGINAL" ]]; then
    echo "Erro: arquivo '$ORIGINAL' não encontrado." >&2
    exit 1
fi

# 1. Confere se é o binário esperado
ACTUAL_SHA256="$(sha256sum "$ORIGINAL" | cut -d' ' -f1)"
if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
    echo "Erro: SHA-256 diferente do esperado." >&2
    echo "  esperado: $EXPECTED_SHA256" >&2
    echo "  obtido:   $ACTUAL_SHA256" >&2
    exit 1
fi

# 2. Copia o original (que fica intocado) e confere os bytes antes de mexer
cp "$ORIGINAL" "$PATCHED"
BEFORE="$(xxd -s "$OFFSET" -l 2 -p "$PATCHED")"
if [[ "$BEFORE" != "750a" ]]; then
    echo "Erro: bytes em 0x942 são '$BEFORE', esperado '750a'. Abortando." >&2
    rm -f "$PATCHED"
    exit 1
fi

echo "Antes:"
xxd -s "$OFFSET" -l 4 "$PATCHED"

# 3. Aplica o patch (JNZ -> NOP NOP)
printf '\x90\x90' | dd of="$PATCHED" bs=1 seek="$OFFSET" count=2 conv=notrunc status=none

echo "Depois:"
xxd -s "$OFFSET" -l 4 "$PATCHED"

echo
echo "SHA-256 do patchado:"
sha256sum "$PATCHED"