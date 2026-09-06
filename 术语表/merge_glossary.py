#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并五章术语表并去重，输出为Trados可识别的格式
"""

import re
import csv
from pathlib import Path
from collections import OrderedDict

def parse_markdown_table(file_path):
    """解析Markdown文件中的术语表格"""
    terms = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有表格
    lines = content.split('\n')
    in_table = False
    headers = []
    
    for line in lines:
        line = line.strip()
        
        # 检测表格开始
        if line.startswith('|') and '中文' in line and '建议英文' in line:
            in_table = True
            # 解析表头
            headers = [h.strip() for h in line.split('|')[1:-1]]
            continue
        
        # 跳过分隔行
        if in_table and line.startswith('|---'):
            continue
        
        # 解析表格行
        if in_table and line.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) >= 2:
                chinese = cells[0].strip()
                english = cells[1].strip()
                
                # 清理markdown格式
                chinese = clean_markdown(chinese)
                english = clean_markdown(english)
                
                # 跳过空行或表头重复
                if chinese and english and chinese != '中文':
                    terms.append({
                        'chinese': chinese,
                        'english': english
                    })
        elif in_table and not line.startswith('|'):
            # 表格结束
            in_table = False
    
    return terms

def clean_markdown(text):
    """清理Markdown格式标记"""
    # 移除粗体
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # 移除斜体
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # 移除代码块
    text = re.sub(r'`(.+?)`', r'\1', text)
    # 移除方括号标记如[已有]、[新增]等
    text = re.sub(r'\[.+?\]', '', text)
    # 清理多余空格
    text = ' '.join(text.split())
    return text.strip()

def merge_glossaries(all_terms):
    """合并术语表并去重"""
    merged = OrderedDict()
    
    for term in all_terms:
        chinese = term['chinese']
        english = term['english']
        
        if chinese in merged:
            # 如果已存在，检查翻译是否相同
            existing_english = merged[chinese]
            if existing_english != english:
                # 翻译不同，用分号合并（保留所有版本）
                merged[chinese] = f"{existing_english}; {english}"
        else:
            merged[chinese] = english
    
    return merged

def export_to_csv(merged_terms, output_path):
    """导出为CSV格式（UTF-8 with BOM）"""
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Source', 'Target'])  # Trados标准列名
        for chinese, english in merged_terms.items():
            writer.writerow([chinese, english])

def export_to_tab_delimited(merged_terms, output_path):
    """导出为Tab分隔的文本文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Source\tTarget\n")  # 表头
        for chinese, english in merged_terms.items():
            f.write(f"{chinese}\t{english}\n")

def main():
    # 定义章节路径
    base_dir = Path(r"d:\MyData\projects\01-活跃项目\02_网文创作\网文小说合集\第二本小说\章节原文")
    chapters = ['第1章', '第2章', '第3章', '第4章', '第5章']
    
    # 收集所有章节的术语
    all_terms = []
    for chapter in chapters:
        file_path = base_dir / chapter / f"{chapter}术语与人设.md"
        if file_path.exists():
            print(f"正在处理: {chapter}")
            terms = parse_markdown_table(file_path)
            print(f"  提取到 {len(terms)} 个术语")
            all_terms.extend(terms)
        else:
            print(f"文件不存在: {file_path}")
    
    print(f"\n总计提取: {len(all_terms)} 个术语条目")
    
    # 合并去重
    merged_terms = merge_glossaries(all_terms)
    print(f"去重合并后: {len(merged_terms)} 个唯一术语")
    
    # 导出为CSV格式（推荐用于Trados）
    csv_output = base_dir.parent / "术语表_Trados_CSV.csv"
    export_to_csv(merged_terms, csv_output)
    print(f"\n已导出CSV格式: {csv_output}")
    
    # 导出为Tab分隔格式
    txt_output = base_dir.parent / "术语表_Trados_Tab.txt"
    export_to_tab_delimited(merged_terms, txt_output)
    print(f"已导出Tab分隔格式: {txt_output}")
    
    print("\n完成！")
    print("\n使用说明:")
    print("1. CSV格式: 在Trados中选择 File > Import > CSV，选择生成的CSV文件")
    print("2. Tab分隔格式: 在Trados中选择 File > Import > Tab-delimited，选择生成的TXT文件")
    print("3. 导入时确保选择UTF-8编码")

if __name__ == '__main__':
    main()
