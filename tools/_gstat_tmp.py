# -*- coding: utf-8 -*-
"""临时：打印 unstaged D 的路径样本与计数。用完即删。"""
import os, subprocess, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*a):
    return subprocess.run(["git", "--no-pager"] + list(a), cwd=BASE,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


s = git("status", "--porcelain")
d = [l for l in s.stdout.splitlines() if l[:1] == " " and l[1:2] == "D"]
print("unstaged D:", len(d))
for l in d[:8]:
    print("  ", l[3:].strip('"'))
c = collections.Counter(l[3:].strip('"').split("/")[1] for l in d if l[3:].strip('"').startswith("章节原文/"))
print("second-seg:", dict(list(c.items())[:5]))
