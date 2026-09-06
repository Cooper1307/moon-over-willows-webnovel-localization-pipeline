import io, sys

def read(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()

def write(p, s):
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write(s)

# ---------- Chapter 37: repeated-expression + adverb-verb fixes ----------
ch37_pairs = [
    # R1: remove -ly adverb "said shyly" (shyness already shown by blush/gaze)
    ('She pulled her gaze away from Prince Yi and said shyly, "Young Master Qiao always likes to joke.',
     'She pulled her gaze away from Prince Yi. "Young Master Qiao always likes to joke.'),
    # R2: quickly stood -> stronger verb
    ('Qiao Wenxian quickly stood and returned the bow.',
     'Qiao Wenxian sprang up and returned the bow.'),
    # R3: quickly left -> stronger verb
    ('With that, he quickly left.',
     'With that, he hurried off.'),
    # R4: slowly dragging -> verb
    ('camels slowly dragging people or goods across the wide streets',
     'camels plodding along, hauling people or goods across the wide streets'),
    # R5: gradually fall asleep -> no -ly adverb
    ('Only then did he feel better and gradually fall asleep.',
     'Only then did he feel better and finally drift off to sleep.'),
    # R6: personally carried -> herself (no -ly adverb)
    ('and she personally carried over an extra quilt to cover him.',
     'and she carried over an extra quilt herself to cover him.'),
    # R7: immediately bloomed -> verb
    ('when the plum blossoms "saw" her brother, one of them immediately bloomed open.',
     'when the plum blossoms "saw" her brother, one of them suddenly burst into bloom.'),
    # R8: really love -> do love (no -ly adverb)
    ('I really love the ci you wrote.',
     'I do love the ci you wrote.'),
    # R9: properly bury -> proper burial (no -ly adverb)
    ('so he can properly bury his mother.',
     'so he can give his mother a proper burial.'),
    # R10: wanted to argue further -> kept arguing (no -ly adverb)
    ('Bai Feng was still dissatisfied and wanted to argue further, but Shen Jianchen stopped him.',
     'Bai Feng was still dissatisfied and kept arguing, but Shen Jianchen stopped him.'),
    # R11: vary "couldn't help falling into memory"
    ('Qiao Mengrong savored the words carefully and couldn\'t help falling into memory...',
     'Qiao Mengrong savored the words and found herself drifting into memory...'),
    # R12: vary "couldn't help thinking of Bai Feng"
    ('He couldn\'t help thinking of Bai Feng.',
     'Bai Feng came to mind.'),
    # R13a: remove doubled "hide behind tea" (first beat)
    ('Shen Jianchen fell silent. He couldn\'t explain, and he couldn\'t bear to hurt her, so he picked up his tea bowl and drained it, letting the hot tea hide his expression.',
     'Shen Jianchen fell silent. He couldn\'t explain, and he couldn\'t bear to hurt her, so he lifted his tea bowl and drank, using the gesture to cover his expression.'),
    # R13b: remove doubled "hide behind tea" (second beat)
    ('He hid behind the rim of his tea bowl, buying himself a moment to compose himself. Setting it down, he smiled.',
     'He took the chance to steady himself. Setting the bowl down, he smiled.'),
    # R14: remove erroneous italic on *glowing* (descriptive, not a thought)
    ('Qiao Mengrong was *glowing*—eyes bright, cheeks flushed, barely containing herself.',
     'Qiao Mengrong was glowing—eyes bright, cheeks flushed, barely containing herself.'),
]

ch37_files = [
    r'D:\MyData\projects\大三下\网文小说翻译\第二本小说\章节原文\第37章\第37章初译_对照.md',
    r'D:\MyData\projects\大三下\网文小说翻译\第二本小说\章节原文\第37章\第37章译文.md',
]

for fp in ch37_files:
    s = read(fp)
    print('===', fp.split('\\')[-1], '===')
    for old, new in ch37_pairs:
        n = s.count(old)
        if n == 0:
            print('  [WARN] not found:', repr(old[:50]))
        else:
            s = s.replace(old, new)
            print('  ok x%d :' % n, repr(old[:55]))
    write(fp, s)

# ---------- Chapter 36: name unification + polish ----------
# English name typo: Wenyuan -> Wenxian (consistent with ch37)
# Chinese name typo: 文渊 -> 文仙 (consistent with 乔文仙 / ch37)
ch36_pairs_en = [
    ('you\'ll naturally appreciate the painting',
     "you'll come to savor the painting yourself"),
    ('This one is truly in awe.',
     'Your servant is truly in awe.'),
]

ch36_dupe = r'D:\MyData\projects\大三下\网文小说翻译\第二本小说\章节原文\第36章\第36章初译_对照.md'
ch36_trans = r'D:\MyData\projects\大三下\网文小说翻译\第二本小说\章节原文\第36章\第36章译文.md'

# 对照版: English + Chinese name fixes
s = read(ch36_dupe)
print('=== 第36章初译_对照.md ===')
# English Wenyuan -> Wenxian
n = s.count('Wenyuan')
s = s.replace('Wenyuan', 'Wenxian')
print('  Wenyuan -> Wenxian x%d' % n)
# Chinese 文渊 -> 文仙
n2 = s.count('文渊')
s = s.replace('文渊', '文仙')
print('  文渊 -> 文仙 x%d' % n2)
for old, new in ch36_pairs_en:
    m = s.count(old)
    if m == 0:
        print('  [WARN] not found:', repr(old[:50]))
    else:
        s = s.replace(old, new)
        print('  ok x%d :' % m, repr(old[:55]))
write(ch36_dupe, s)

# 译文: English only
s = read(ch36_trans)
print('=== 第36章译文.md ===')
n = s.count('Wenyuan')
s = s.replace('Wenyuan', 'Wenxian')
print('  Wenyuan -> Wenxian x%d' % n)
for old, new in ch36_pairs_en:
    m = s.count(old)
    if m == 0:
        print('  [WARN] not found:', repr(old[:50]))
    else:
        s = s.replace(old, new)
        print('  ok x%d :' % m, repr(old[:55]))
write(ch36_trans, s)

print('DONE')
