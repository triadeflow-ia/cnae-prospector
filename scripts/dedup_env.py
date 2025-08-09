#!/usr/bin/env python3
import pathlib

def dedup_env(path: str = '.env') -> None:
    p = pathlib.Path(path)
    if not p.exists():
        print('.env não encontrado')
        return

    lines = p.read_text(encoding='utf-8', errors='ignore').splitlines()
    kv = {}

    for line in lines:
        s = line.strip()
        if not s or s.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        kv[key] = value

    out = '\n'.join(f'{k}={v}' for k, v in kv.items()) + '\n'
    p.write_text(out, encoding='utf-8')
    print('env deduplicado')

if __name__ == '__main__':
    dedup_env()


