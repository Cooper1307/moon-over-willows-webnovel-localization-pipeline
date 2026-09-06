base = "D:/MyData/projects/大三下/网文小说翻译/第二本小说/章节原文/第38章"
f1 = base + "/第38章初译_对照.md"
f2 = base + "/第38章译文.md"

reps = [
    ("it was originally yours.", "it was yours to begin with.", 1),
    ("saw Xia Guo standing respectfully outside.",
     "saw Xia Guo standing outside with deference.", 1),
    ("and I really want to learn.", "and I'm keen to learn.", 1),
    ("this queen won't move out immediately.", "this queen won't move out at once.", 1),
]

for fn in (f1, f2):
    with open(fn, encoding="utf-8") as fh:
        txt = fh.read()
    for old, new, exp in reps:
        c = txt.count(old)
        if c != exp:
            print("[WARN] %s: expected %d of >>%s<< but found %d" % (fn, exp, old, c))
        txt = txt.replace(old, new)
    with open(fn, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print("OK wrote " + fn)
