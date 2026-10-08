# Lean formalizations

This directory contains Lean formalizations of some results in this repository.
They are organized in a single large library, so we recommend compiling only small portions at a time.

See the [Comparator README](ComparatorChallenges/README.md) for more information about how to verify the results.

## Technical note: mmap

Compiling the entire library may fail if Linux's `vm.max_map_count` is too low.
One workaround is to build Lean with the CMake option `-DMMAP=OFF`; it may also be necessary to set the environment variable `GLIBC_TUNABLES` to `glibc.malloc.mmap_max=0:glibc.malloc.arena_max=1` when running Lean or Lake.
