import re, sys, os, io

BASE = r"D:\MyData\projects\大三下\网文小说翻译\第二本小说\章节原文"

def is_cjk_line(s):
    cjk = len(re.findall(r'[\u4e00-\u9fff]', s))
    return cjk > 0 and cjk * 3 > len(s.strip()) * 0.3

def eng_lines(path):
    out = []
    with io.open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            t = line.rstrip('\n')
            s = t.strip()
            if not s or s == '---':
                continue
            if re.search(r'[\u4e00-\u9fff]', s):
                continue
            out.append((i, t))
    return out

TAGS = r'\b(said|continued|told|called|replied|objected|answered|asked|added|cut in|interrupted|responded|remarked|urged|explained|declared|exclaimed|shouted)\b'

KEEP_LY = set("""only family really perfectly truly entirely miraculously fortunately unfortunately
surely certainly likely lonely lovely friendly early holy silly ugly deadly costly orderly
elderly worldly heavenly ghastly kindly homely daily weekly monthly yearly nightly timely""".split())

def analyze(ch):
    folder = os.path.join(BASE, "第%d章" % ch)
    for fn in os.listdir(folder):
        if fn.endswith("初译_对照.md"):
            path = os.path.join(folder, fn)
            break
    lines = eng_lines(path)
    print("=" * 70)
    print("CHAPTER %d  file=%s  english-paras=%d" % (ch, fn, len(lines)))
    print("=" * 70)

    tagc = {}
    for ln, t in lines:
        for m in re.finditer(TAGS, t, re.I):
            w = m.group(1).lower()
            tagc[w] = tagc.get(w, 0) + 1
    print("-- TAG COUNTS:", sorted(tagc.items(), key=lambda x: -x[1]))

    print("\n-- LINES WITH SPEECH TAGS --")
    for ln, t in lines:
        if re.search(TAGS, t, re.I):
            print("L%-5d %s" % (ln, t))

    print("\n-- -LY ADVERBS (candidates) --")
    for ln, t in lines:
        found = [w for w in re.findall(r'\b(\w+ly)\b', t, re.I) if w.lower() not in KEEP_LY]
        if found:
            print("L%-5d [%s] %s" % (ln, ",".join(found), t))

    print("\n-- OPENERS (first 4 words of each para) --")
    for ln, t in lines:
        print("L%-5d %s" % (ln, " ".join(t.split()[:4])))

for ch in [int(x) for x in sys.argv[1:]]:
    analyze(ch)
