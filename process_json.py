import json
from markdown_and_assemble import convert_html_to_markdown

def process_json_file(input_file, output_file):
    """
    读取JSON文件，转换其中的content字段为Markdown格式，并保存到新文件
    :param input_file: 输入JSON文件路径
    :param output_file: 输出JSON文件路径
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换content字段
    if 'content' in data:
        data['content'] = convert_html_to_markdown(data['content'])
    
    # 处理answers_data中的content字段
    if 'answers_data' in data:
        for answer in data['answers_data']:
            if 'content' in answer:
                answer['content'] = convert_html_to_markdown(answer['content'])
    
    # 处理comments中的text字段
    if 'comments' in data:
        for comment in data['comments']:
            if 'text' in comment:
                comment['text'] = convert_html_to_markdown(comment['text'])
    
    # 保存到新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

import os
import glob

def batch_process_json(input_dir, output_dir):
    """
    批量处理目录下的所有JSON文件
    :param input_dir: 输入目录路径
    :param output_dir: 输出目录路径
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    from tqdm import tqdm
    json_files = list(glob.glob(os.path.join(input_dir, '*.json')))
    
    for input_file in tqdm(json_files, desc="处理JSON文件"):
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_text.json")
        process_json_file(input_file, output_file)
        # print(f"转换完成: {filename} -> {os.path.basename(output_file)}")

if __name__ == "__main__":
    # 单个文件处理模式
    # input_file = '25786.json'
    # output_file = '25786_md.json'
    # process_json_file(input_file, output_file)
    # print(f"转换完成，结果已保存到 {output_file}")
    
    # 批量处理模式
    input_dir = 'reverseengineering'
    output_dir = 'reverseengineering_text'
    batch_process_json(input_dir, output_dir)
    print(f"批量转换完成，结果已保存到 {output_dir} 目录")