#!/usr/bin/env python3
# Ch38 cross-chapter audit fixes: Chinglish/literal -> natural, faithful; micro dialogue-tag variety
import io

pairs = [
    # 1. Chinglish: 让人不由产生畏惧 -> natural
    ("his muscles well-developed, inspiring fear in onlookers.",
     "his muscles well-developed, a build that made onlookers wary."),
    # 2. Chinglish: 双手奉上 (literal "with both hands") -> willing surrender
    ("Then the bamboo forest will be handed over with both hands!",
     "Then the bamboo forest will be handed over gladly!"),
    # 3. 东家长东家短 (gossip) + 竹民 -> folk; 见我...说 -> greet...gossip
    ("The bamboo people see me and talk about this and that",
     "The bamboo folk greet me and gossip about this and that"),
    # 4. 拳头厉害 -> more vivid idiom
    ("the Young Miss's fists are formidable",
     "the Young Miss's fists pack a punch"),
    # 5. de-dup "run for nothing" / "run for free" (near-repeat in 2 lines)
    ("I won't let you run for nothing.",
     "I won't let you make the trip for nothing."),
    # 6. 受姑爷的气 -> bullying (气 in context = abuse)
    ("Why suffer your husband's temper at the Lin Manor?",
     "Why suffer your husband's bullying at the Lin Manor?"),
    # 7. dialogue-tag variety: rhetorical question -> asked
    ('Inside the bamboo house, Nanny Wei said,',
     'Inside the bamboo house, Nanny Wei asked,'),
    # 8. dialogue-tag variety: continued -> went on
    ('After laughing, Nanny Wei continued,',
     'After laughing, Nanny Wei went on,'),
]

files = ["第38章初译_对照.md", "第38章译文.md"]
for fn in files:
    with io.open(fn, encoding="utf-8") as fh:
        txt = fh.read()
    for old, new in pairs:
        c = txt.count(old)
        if c != 1:
            raise SystemExit(f"[FAIL] {fn}: expected 1 of >>{old[:45]}<< but found {c}")
        txt = txt.replace(old, new)
    with io.open(fn, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print("OK", fn)
print("ALL APPLIED")
