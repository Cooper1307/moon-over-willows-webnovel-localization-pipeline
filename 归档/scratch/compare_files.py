import re
import difflib

def extract_english(content):
    # This is a heuristic based on the observed structure
    # Most English lines are either:
    # 1. Start with Chapter [Number]:
    # 2. Are paragraphs following a Chinese paragraph
    # 3. Are translator's notes in brackets [TN: ...]
    # 4. Are blockquotes >
    
    # Actually, a better way is to identify Chinese characters and exclude those lines.
    # But some lines might be empty.
    
    lines = content.split('\n')
    english_lines = []
    
    # We want to keep:
    # - Lines without Chinese characters (except maybe in [TN: ...] if any, but usually they are English)
    # - Blank lines (to keep paragraph structure)
    
    chinese_char_re = re.compile(r'[\u4e00-\u9fff]')
    
    for line in lines:
        if chinese_char_re.search(line):
            # If it contains Chinese, it might be a bilingual line or a purely Chinese line.
            # In our files, it seems Chinese and English are in separate paragraphs or the English follows the Chinese in the same paragraph if it's short?
            # Looking at the files, they are separate paragraphs.
            continue
        english_lines.append(line)
        
    # Clean up multiple empty lines at the start/end
    full_text = '\n'.join(english_lines).strip()
    return full_text

def compare_files(bilingual_path, pure_path):
    with open(bilingual_path, 'r', encoding='utf-8') as f:
        bilingual_content = f.read()
    with open(pure_path, 'r', encoding='utf-8') as f:
        pure_content = f.read().strip()
        
    extracted_english = extract_english(bilingual_content)
    
    if extracted_english == pure_content:
        return "Complete Match", None
    else:
        diff = difflib.unified_diff(extracted_english.splitlines(), pure_content.splitlines(), lineterm='')
        return "Mismatch", '\n'.join(diff)

# Paths
ch4_bi = r'c:\Users\Lenovo\Downloads\大三下\网文小说翻译\第二本小说\章节原文\第4章\第4章初译_对照.md'
ch4_pure = r'c:\Users\Lenovo\Downloads\大三下\网文小说翻译\第二本小说\章节原文\第4章\第4章纯英译稿.md'
ch5_bi = r'c:\Users\Lenovo\Downloads\大三下\网文小说翻译\第二本小说\章节原文\第5章\第5章初译_对照.md'
ch5_pure = r'c:\Users\Lenovo\Downloads\大三下\网文小说翻译\第二本小说\章节原文\第5章\第5章纯英译稿.md'

print("Comparing Chapter 4...")
status4, diff4 = compare_files(ch4_bi, ch4_pure)
print(f"Status: {status4}")
if diff4:
    print("Diff:")
    print(diff4)

print("\nComparing Chapter 5...")
status5, diff5 = compare_files(ch5_bi, ch5_pure)
print(f"Status: {status5}")
if diff5:
    print("Diff:")
    print(diff5)
