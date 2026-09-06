# -*- coding: utf-8 -*-
"""Apply exact-string English edits to 对照.md (and 译文.md if present).
Usage: python __apply.py <chapter-number>   with EDITS defined in edits_<ch>.py
"""
import io, os, sys, importlib

BASE = r"D:\MyData\projects\大三下\网文小说翻译\第二本小说\章节原文"


def targets(ch):
    folder = os.path.join(BASE, "第%d章" % ch)
    out = []
    for suffix in ("初译_对照.md", "译文.md"):
        p = os.path.join(folder, "第%d章%s" % (ch, suffix))
        if os.path.exists(p):
            out.append(p)
    return out


def run(ch, edits, dry=False):
    files = targets(ch)
    print("CHAPTER %d -> %s" % (ch, [os.path.basename(f) for f in files]))
    texts = {}
    for f in files:
        with io.open(f, encoding='utf-8') as fh:
            texts[f] = fh.read()

    ok = True
    for idx, (old, new) in enumerate(edits, 1):
        hits = {f: texts[f].count(old) for f in files}
        total = sum(hits.values())
        if total == 0:
            print("  [MISS %02d] not found: %r" % (idx, old[:70]))
            ok = False
            continue
        for f in files:
            if hits[f] > 1:
                print("  [WARN %02d] %d hits in %s: %r" % (idx, hits[f], os.path.basename(f), old[:60]))
            if hits[f]:
                texts[f] = texts[f].replace(old, new)
        print("  [OK   %02d] %s -> %s" % (idx, {os.path.basename(k): v for k, v in hits.items()}, new[:60]))

    if not ok:
        print("ABORT: some edits did not match.")
        return False
    if dry:
        print("DRY RUN, nothing written.")
        return True
    for f in files:
        with io.open(f, 'w', encoding='utf-8', newline='') as fh:
            fh.write(texts[f])
    print("WROTE %d files." % len(files))
    return True


if __name__ == '__main__':
    ch = int(sys.argv[1])
    dry = '--dry' in sys.argv
    mod = importlib.import_module('edits_%d' % ch)
    run(ch, mod.EDITS, dry)
