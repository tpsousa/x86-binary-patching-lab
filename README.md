# x86 Binary Patching Lab

Laboratório de engenharia reversa e *binary patching* em um executável PE32 (x86, 32 bits), feito para a disciplina **COCC0263 – Arquitetura de Computadores** (UFMA, 2026.2).

O objetivo: descobrir como o programa `unbreak_windows.exe` valida a senha, chegar na senha por análise estática e dinâmica e, por fim, burlar a verificação alterando bytes do binário.

> **Aviso:** projeto estritamente educacional, feito sobre um executável de exercício fornecido pelo professor.

## Resumo dos resultados

| Item | Resultado |
|---|---|
| Alvo | `unbreak_windows.exe` (PE32, console, Intel 80386) |
| Função de validação | `_main` em `0x00401460` |
| Mecanismo | Senha escondida em uma string maior, lida de 6 em 6 posições (`6*i + 7`) |
| Senha reconstruída | `Cascabulho` (ver nota na seção 5.4 do relatório) |
| Achado extra | `gets()` sem limite de tamanho, vulnerável a buffer overflow |
| Patch | `JNZ` em `0x00401542` (offset `0x942`): `75 0A` → `90 90` (NOP NOP) |
| Efeito | O programa aceita qualquer entrada e gera o *White-Code* |

## Etapas do laboratório

1. **Preparação do ambiente**: VM Ubuntu 24.04 isolada (Multipass), Wine 32 bits, Ghidra 12.2, winedbg.
2. **Etapa A – Reconhecimento**: identificação do tipo de arquivo, hash de referência e primeira execução.
3. **Etapa B – Análise estática (Ghidra)**: localização da `_main` e leitura do pseudocódigo.
4. **Etapa C – Depuração dinâmica (winedbg)**: confirmação no assembly e leitura direta da memória.
5. **Etapa D – Verificação distribuída**: a validação está concentrada em um único laço.
6. **Etapa E – Binary patching**: neutralização do salto condicional com `dd`/`xxd`.
7. **Etapa F – Integridade**: comparação de SHA-256, CheckSum do PE e assinatura Authenticode.
8. **Etapa G – Validação final**: comparação do binário original e do patchado.

## Integridade: o que foi observado

| Mecanismo | Original | Patchado |
|---|---|---|
| SHA-256 | `2cfebab1adbe342ed177aa14e5044d51194b310614709af0d2495b4a741d01ce` | `46cb92e3b4cc7a04e079507673c70146d8bc6b15a2dc8ffe7156f93e8537d145` |
| CheckSum do PE | Válido (`0x151a1`) | Inválido (armazenado `0x151a1`, calculado `0xd7bd`) |
| Authenticode | Sem assinatura | Sem assinatura |

Com só 2 bytes alterados o SHA-256 mudou por completo (efeito avalanche), enquanto o CheckSum do PE ficou desatualizado sem impedir a execução.

## Estrutura do repositório

```
.
├── README.md
├── relatorio/
│   └── relatorio.pdf        # relatório completo do laboratório
├── scripts/                 # (opcional) comandos usados no laboratório
├── resultados/              # hashes e saídas calculadas
└── .gitignore
```

O executável original **não** está versionado aqui, por ser material fornecido pelo professor. Para reproduzir, use o seu próprio `unbreak_windows.exe` e confira se o SHA-256 bate com o hash de referência acima.

## Como reproduzir

```bash
# 1. Ambiente (Ubuntu 24.04)
sudo dpkg --add-architecture i386
sudo apt install -y wine32:i386 wine xxd binutils python3-pefile osslsigncode

# 2. Conferir o binário
file unbreak_windows.exe
sha256sum unbreak_windows.exe

# 3. Copiar e aplicar o patch (JNZ -> NOP NOP em 0x942)
cp unbreak_windows.exe unbreak_windows_patched.exe
printf '\x90\x90' | dd of=unbreak_windows_patched.exe bs=1 seek=$((0x942)) count=2 conv=notrunc

# 4. Testar
echo "qualquercoisa" | wine unbreak_windows_patched.exe
```

## Ferramentas

Ghidra 12.2 · winedbg · Wine (wine32:i386) · Python 3 + pefile · osslsigncode · sha256sum, xxd, dd, binutils · Multipass

## Autor

**Thiago Pereira Sousa**: Ciência da Computação, UFMA.
