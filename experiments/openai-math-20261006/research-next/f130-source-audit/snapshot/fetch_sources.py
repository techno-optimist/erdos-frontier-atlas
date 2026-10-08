"""Bounded public-source snapshot; no Lake, compilation, cache, or model operation."""
import hashlib
import json
from pathlib import Path
import re
import urllib.request

COMMIT = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
BASE = 'https://raw.githubusercontent.com/OpenAI/math/' + COMMIT + '/'
HERE = Path(__file__).resolve().parent
PER_FILE = 1024 * 1024
TOTAL = 8 * 1024 * 1024
MAX_FILES = 128
START = [
    'lean/docs/130.md', 'lean/ComparatorChallenges/UniformFourier.lean',
    'lean/ComparatorChallenges/UniformFourier.json', 'lean/ComparatorChallenges/README.md',
    'lean/OAI/Computability/FourierTransform/Main.lean', 'lean/README.md',
    'lean/lean-toolchain', 'lean/lakefile.lean', 'lean/lake-manifest.json',
]


def main():
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    pending = list(START); done = {}; total = 0
    while pending:
        name = pending.pop(0)
        if name in done:
            continue
        if len(done) >= MAX_FILES:
            raise ValueError('bounded source count exceeded')
        with opener.open(BASE + name, timeout=30) as response:
            if response.status != 200:
                raise ValueError('public HTTP source failed')
            raw = response.read(PER_FILE + 1)
        total += len(raw)
        if len(raw) > PER_FILE or total > TOTAL:
            raise ValueError('bounded source bytes exceeded')
        target = HERE / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(raw)
        imports = []
        if name.endswith('.lean'):
            imports = re.findall(r'^import\s+([^\s]+)', raw.decode(), re.M)
            # Fetch only source modules in this repository, never dependencies.
            for module in imports:
                if module.startswith('OAI.'):
                    pending.append('lean/' + module.replace('.', '/') + '.lean')
        done[name] = dict(url=BASE+name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), imports=imports)
    result = dict(schema='uniform-fourier-source-snapshot/v1', repository='https://github.com/OpenAI/math',
                  commit=COMMIT, files=done, total_bytes=total,
                  dependency_packages_fetched=False, lean_build_executed=False,
                  note='Import scan follows line-leading OAI imports only; Lean environment/kernel audit is unrun.')
    raw = (json.dumps(result, sort_keys=True, indent=2)+'\n').encode()
    with (HERE/'source-manifest.json').open('xb') as stream:
        stream.write(raw)
    print(json.dumps(dict(files=len(done),bytes=total,manifest_sha256=hashlib.sha256(raw).hexdigest())))


if __name__ == '__main__':
    main()
