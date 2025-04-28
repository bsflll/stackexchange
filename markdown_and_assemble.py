import os
import json
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import html
from markdownify import markdownify as md

def html_to_markdown_clean(html_text):
    """Convert HTML content to Markdown while cleaning <a> inside <pre> and removing fake emails."""
    soup = BeautifulSoup(html_text, 'html.parser')

    # Clean <pre> contents: remove <a> links completely
    for pre in soup.find_all('pre'):
        for a_tag in pre.find_all('a'):
            a_tag.decompose()

    markdown_parts = []

    body = soup.find('div', class_='s-prose') or soup
    for elem in body.children:
        if elem.name == 'p':
            markdown_parts.append(elem.get_text())
            markdown_parts.append('\n\n')
        elif elem.name == 'pre':
            code_block = elem.get_text()
            code_block = re.sub(r'\[email protected\]', '', code_block)
            markdown_parts.append('```\n')
            markdown_parts.append(code_block)
            markdown_parts.append('\n```\n')

    return ''.join(markdown_parts)

def process_text_field(text):
    """Clean a text field from HTML to Markdown."""
    if not text:
        return text
    text = BeautifulSoup(text, 'html.parser').get_text()
    text = text.replace('\\n', '  \n')
    return text

def recursive_process(obj):
    """Recursively process any dict or list to clean 'content' and 'text' fields."""
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            if key == 'content' and isinstance(value, str):
                new_obj[key] = html_to_markdown_clean(value).replace('\\n', '  \n')
            elif key == 'text' and isinstance(value, str):
                new_obj[key] = process_text_field(value)
            else:
                new_obj[key] = recursive_process(value)
        return new_obj
    elif isinstance(obj, list):
        return [recursive_process(item) for item in obj]
    else:
        return obj

def process_single_file(input_folder, output_folder, filename):
    """Process a single JSON file."""
    input_path = os.path.join(input_folder, filename)
    output_filename = filename.replace('.json', '_markdown.json')
    output_path = os.path.join(output_folder, output_filename)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Recursively process entire JSON tree
        data = recursive_process(data)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Failed to process {filename}: {e}")
        return False

def process_all_json(input_folder, output_folder, max_workers=8):
    """Convert all JSON files inside input_folder and save to output_folder using multithreading."""
    os.makedirs(output_folder, exist_ok=True)

    filenames = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_file, input_folder, output_folder, filename): filename for filename in filenames}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing JSON files"):
            future.result()


def merge_all_json(input_folder, output_file):
    """Merge all *_markdown.json files inside input_folder into one dataset."""
    merged_data = {
        "data": {
            "dataset": []
        }
    }

    filenames = [f for f in os.listdir(input_folder) if f.endswith('_markdown.json')]
    filenames.sort()  # optional: sort files for consistency

    for filename in tqdm(filenames, desc="Merging JSON files"):
        input_path = os.path.join(input_folder, filename)

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            merged_data["data"]["dataset"].append(data)

        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    # Save the final merged JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully merged {len(merged_data['data']['dataset'])} items into {output_file}")


if __name__ == "__main__":
    input_folder = 'reverseengineering'
    output_folder = 'reverseengineering_markdown'
    # process_all_json(input_folder, output_folder)
    merge_all_json(output_folder, 'reverseengineering_markdown.json')