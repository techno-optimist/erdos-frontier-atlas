# Complete A030979 prefix through 3^24

**Not a solution of #376.** Infinitude remains open. Live page remains OPEN.

Independent 0-1 base-3 search (every n < 3^24 with base-3 digits in {0,1} is visited). Hits, in order:

```
0, 1, 10, 756, 757, 3160, 3186, 3187, 3250,
7560, 7561, 7651, 20007, 59548377, 59548401,
45773612811, 45775397187
```

That is exactly the OEIS A030979 prefix through those two ~4.58e10 terms. No extras below 3^24 = 282,429,536,481. Next OEIS term 237,617,431,723,407 is larger than this cutoff.

Among them, base-11 digits all ≤5 (coprime also to 11) only at **0, 1, 3160** — consistent with Graham’s remark that 3160 is probably the last such k.

CI replays D=20 (complete through 3^20 > 59,548,401). The D=24 run is recorded here, not in the default test.

Replay:

```sh
python3 -I -B -m unittest discover -s experiments/astra-376-20260911 -p 'test_*.py' -v
```
