#ifndef CODEX_FOPEN_BINARY_SHIM_H
#define CODEX_FOPEN_BINARY_SHIM_H

#include <stdio.h>
#include <string.h>

/*
 * The upstream drat-trim source opens proofs with mode "r".  On the Windows
 * CRT that treats byte 0x1a as end-of-file, so a valid binary DRAT can be
 * truncated.  This compile-time shim changes read-only opens to "rb" while
 * leaving every other mode untouched; no checker logic is changed.
 */
static FILE *codex_fopen_binary(const char *path, const char *mode) {
    return fopen(path, strcmp(mode, "r") == 0 ? "rb" : mode);
}

#define fopen codex_fopen_binary

#endif
