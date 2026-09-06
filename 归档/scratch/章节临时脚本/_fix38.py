import io

base = "D:/MyData/projects/大三下/网文小说翻译/第二本小说/章节原文/第38章"
f1 = base + "/第38章初译_对照.md"
f2 = base + "/第38章译文.md"

reps = [
    ("sat down quite naturally.", "took her seat with easy familiarity.", 1),
    ("Nanny Wei's words made Qianli Xun feel incredibly comfortable.",
     "Nanny Wei's words put Qianli Xun entirely at ease.", 1),
    ("Nanny Wei realized she had truly changed. It was good that she had changed—no more being bullied like before.",
     "Nanny Wei realized she had changed. It was just as well—no more being bullied like before.", 1),
    ("Hearing you say that, I'm deeply relieved.",
     "Hearing you say that brings me great relief.", 1),
    ("Xia Guo obediently went outside and stood beside the maids and servants Nanny Wei had brought.",
     "Xia Guo did as she was told and went outside to stand beside the maids and servants Nanny Wei had brought.", 1),
    ("I'm truly happy for you.", "I couldn't be happier for you.", 1),
    ("Kuqiao, listening nearby, was very pleased.",
     "Kuqiao, listening nearby, was delighted.", 1),
    ("The Zhu family could freely use it and collect rent, but the land root remained with the previous owner.",
     "The Zhu family was free to use it and collect rent, but the land root remained with the previous owner.", 1),
    ("After their chat, Nanny Wei looked around the bamboo house and was very satisfied, praising Kuqiao profusely.",
     "After their chat, Nanny Wei looked around the bamboo house and, well pleased, showered Kuqiao with praise.", 1),
    ("Her mindset and ideas were truly in sync with her own.",
     "Her outlook and way of thinking resonated with Qianli Xun's own.", 1),
    ('Xia Guo answered honestly, "Don\'t worry, Nanny. I\'ll keep it firmly in mind."',
     'Xia Guo gave an honest reply. "Don\'t worry, Nanny. I\'ll keep it firmly in mind."', 1),
    ("She stepped forward to examine her carefully",
     "She stepped forward to scrutinize her", 1),
    ("From his stride, he seemed quite skilled.",
     "From his stride, he looked like a trained fighter.", 1),
    ("Qianli Xun examined the expert carefully.",
     "Qianli Xun scrutinized the expert.", 1),
    ("Leave immediately!", "Leave at once!", 1),
    ("move out of the bamboo forest immediately.",
     "move out of the bamboo forest at once.", 1),
    ("would surely have been skilled", "would have been skilled", 1),
    ("you truly lack contractual spirit.", "you lack any real contractual spirit.", 1),
    ("it really damages your image.", "it does your image no favors.", 1),
    ("A sense of warmth arose naturally, and she understood",
     "A sense of warmth welled up inside her, and she understood", 1),
]

for fn in (f1, f2):
    with open(fn, encoding="utf-8") as fh:
        txt = fh.read()
    for old, new, exp in reps:
        c = txt.count(old)
        if c != exp:
            print("[WARN] %s: expected %d of >>%s<< but found %d" % (fn, exp, old[:40], c))
        txt = txt.replace(old, new)
    oldf = "young lady from a distinguished family"
    newf = "young lady of a distinguished family"
    c = txt.count(oldf)
    if c != 2:
        print("[WARN] %s: expected 2 of >>%s<< but found %d" % (fn, oldf, c))
    txt = txt.replace(oldf, newf)
    with open(fn, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print("OK wrote " + fn)
