#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从"第X章初译_对照.md"文件中提取英文译文，生成纯译文版本。

使用方法：
    python extract_translation.py [输入文件路径] [输出文件路径]
    
    如果不指定参数，脚本会提示输入文件路径。

示例：
    python extract_translation.py "章节原文/第28章/第28章初译_对照.md" "章节原文/第28章/第28章译文.md"
"""

import re
import sys
from pathlib import Path


def is_english_line(line: str) -> bool:
    """
    判断一行是否为英文内容。
    
    规则：
    1. 以英文字母开头
    2. 或者包含英文单词（至少3个字母的单词）
    3. 排除纯数字、纯符号、中文开头的行
    """
    stripped = line.strip()
    if not stripped:
        return False
    
    # 排除分隔符
    if stripped == '---':
        return False
    
    # 排除中文开头的行（包括中文标点）
    if re.match(r'^[\u4e00-\u9fff]', stripped):
        return False
    
    # 检查是否包含英文字母
    if not re.search(r'[a-zA-Z]', stripped):
        return False
    
    # 检查是否有至少一个英文单词（3个字母以上）
    if re.search(r'\b[a-zA-Z]{3,}\b', stripped):
        return True
    
    # 如果以英文字母开头且包含英文标点，也认为是英文
    if re.match(r'^[A-Za-z]', stripped) and re.search(r'[.,!?;:\'"]', stripped):
        return True
    
    return False


def extract_translation(input_path: Path, output_path: Path) -> bool:
    """
    从对照文件中提取英文译文并保存到输出文件。
    
    Args:
        input_path: 输入的对照文件路径
        output_path: 输出的纯译文文件路径
    
    Returns:
        bool: 是否成功提取
    """
    if not input_path.exists():
        print(f"错误：文件不存在 - {input_path}")
        return False
    
    # 读取文件内容
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 提取英文内容
    english_lines = []
    prev_was_english = False
    
    for line in lines:
        # 保留英文标题行（# Chapter X: ...）
        if line.strip().startswith('# Chapter'):
            english_lines.append(line)
            english_lines.append('\n')
            prev_was_english = False
            continue
        
        # 判断是否为英文行
        if is_english_line(line):
            english_lines.append(line)
            prev_was_english = True
        elif prev_was_english and line.strip() == '':
            # 英文段落后的空行保留
            english_lines.append(line)
            prev_was_english = False
        else:
            prev_was_english = False
    
    # 清理末尾多余空行
    while english_lines and english_lines[-1].strip() == '':
        english_lines.pop()
    
    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(english_lines)
    
    print(f"成功提取译文：{output_path}")
    return True


def main():
    """主函数"""
    if len(sys.argv) >= 3:
        # 从命令行参数获取路径
        input_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])
    elif len(sys.argv) == 2:
        # 只提供了输入路径，自动生成输出路径
        input_path = Path(sys.argv[1])
        # 将"第X章初译_对照.md"转换为"第X章译文.md"
        output_name = input_path.name.replace('初译_对照', '译文')
        output_path = input_path.parent / output_name
    else:
        # 交互式输入
        print("=" * 60)
        print("对照文件英文译文提取工具")
        print("=" * 60)
        input_str = input("请输入对照文件路径（如：章节原文/第28章/第28章初译_对照.md）：").strip()
        input_path = Path(input_str)
        
        if not input_path.exists():
            print(f"错误：文件不存在 - {input_path}")
            sys.exit(1)
        
        # 自动生成输出路径
        output_name = input_path.name.replace('初译_对照', '译文')
        output_path = input_path.parent / output_name
    
    # 执行提取
    success = extract_translation(input_path, output_path)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
