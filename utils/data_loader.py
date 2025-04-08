from pathlib import Path
import yaml
from typing import List, Dict

def load_independent_cases(root="tests/cases"):
    """加载所有独立用例"""
    cases = []
    base_path = Path(__file__).parent.parent / root

    # 递归遍历所有YAML文件
    for yaml_file in base_path.rglob("*.yaml"):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            case_data = yaml.safe_load(f)
            case_data['_meta'] = {
                'path': str(yaml_file.relative_to(base_path))
            }
            cases.append(case_data)

    return cases

def get_case_structure(root="tests/cases") -> Dict[str, List[str]]:
    """获取用例模块和用例名称的结构"""
    case_structure = {}
    base_path = Path(__file__).parent.parent / root

    for yaml_file in base_path.rglob("*.yaml"):
        module = yaml_file.parent.relative_to(base_path).as_posix()
        case_name = yaml_file.stem

        if module not in case_structure:
            case_structure[module] = []
        case_structure[module].append(case_name)

    return case_structure

def generate_selected_cases(selected_cases: Dict[str, List[str]], root="tests/cases") -> List[Dict]:
    """生成选中用例的数据"""
    cases = []
    base_path = Path(__file__).parent.parent / root

    for module, case_names in selected_cases.items():
        module_path = base_path / module
        for case_name in case_names:
            yaml_file = module_path / f"{case_name}.yaml"
            with open(yaml_file, 'r', encoding='utf-8') as f:
                case_data = yaml.safe_load(f)
                case_data['_meta'] = {
                    'path': str(yaml_file.relative_to(base_path))
                }
                cases.append(case_data)

    return cases

def read_yaml(path):
    with open(path, mode="r", encoding="utf-8") as f:
        dict_value = yaml.load(f, yaml.FullLoader)
        return dict_value

def write_yaml(path, data):
    with open(path, mode="a+", encoding="utf-8") as f:
        yaml.dump(data, stream=f, allow_unicode=True)
