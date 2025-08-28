from pathlib import Path
import re

def copy_file_with_variables(src_path: Path, dst_path: Path, variables: dict):
    '''変数展開を行ってファイルをコピーします。'''
    with open(src_path, 'r') as f:
        content = f.read()
    for key, value in variables.items():
        content = content.replace(f'{{{{:{key}:}}}}', value)
    m = re.search(r'{{:.*:}}', content)
    if m:
        raise ValueError(f'{src_path}は未知の変数が含まれています: {m.group(0)}')
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_path, 'w') as f:
        f.write(content)

def copy_dir_with_variables(src_path: Path, dst_path: Path, variables: dict):
    '''変数展開を行ってフォルダーをコピーします。'''
    if not dst_path.is_dir():
        dst_path.mkdir(parents=True, exist_ok=True)
    for i in src_path.glob('*'):
        if i.is_file():
            copy_file_with_variables(i, dst_path / i.name, variables)
        elif i.is_dir():
            copy_dir_with_variables(i, dst_path / i.name, variables)

def replace_text_of_file(path: Path, replace_dict: dict[str, str]):
    '''replace_dictのkeyを正規表現としてファイルのテキストを置換します。'''
    with open(path, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        for key, value in replace_dict.items():
            line = re.sub(key, value, line)
        lines[i] = line
    with open(path, 'w') as f:
        f.writelines(lines)
