import sys
import json
import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

# 添加项目根目录到sys.path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import get_case_structure, generate_selected_cases

class TestRunnerModel:
    def __init__(self):
        self.selected_cases: Dict[str, List[str]] = defaultdict(list)  # 存储选中的用例 {module: [case_name1, case_name2, ...]}
        self.case_structure: Dict[str, Set[str]] = {}  # 缓存用例结构
        self.config_path = Path(__file__).parent.parent / "configs" / "test_selection.json"
        self.load_saved_selection()

    def load_case_structure(self):
        """加载用例结构并缓存"""
        try:
            self.case_structure = get_case_structure()
            return self.case_structure
        except Exception as e:
            logging.error(f"加载用例结构失败: {str(e)}", exc_info=True)
            return {}

    def update_selected_cases(self, module: str, case_name: str, is_selected: bool):
        """更新选中的用例"""
        if not module:
            logging.warning("更新选中用例时模块名为空")
            return

        if is_selected:
            if case_name not in self.selected_cases[module]:
                self.selected_cases[module].append(case_name)
        else:
            if case_name in self.selected_cases[module]:
                self.selected_cases[module].remove(case_name)
                if not self.selected_cases[module]:
                    del self.selected_cases[module]

        # 保存选择状态
        self.save_selection()

    def select_all_cases(self, case_structure):
        """选择所有用例"""
        self.selected_cases = defaultdict(list)
        for module, cases in case_structure.items():
            self.selected_cases[module] = list(cases)
        self.save_selection()

    def deselect_all_cases(self):
        """取消选择所有用例"""
        self.selected_cases.clear()
        self.save_selection()

    def get_selected_cases(self):
        """获取选中的用例"""
        try:
            return generate_selected_cases(dict(self.selected_cases))
        except Exception as e:
            logging.error(f"生成选中用例失败: {str(e)}", exc_info=True)
            return []

    def save_selection(self):
        """保存选择状态到文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(dict(self.selected_cases), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存选择状态失败: {str(e)}", exc_info=True)

    def load_saved_selection(self):
        """从文件加载选择状态"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_selection = json.load(f)
                    # 转换为defaultdict
                    self.selected_cases = defaultdict(list)
                    for module, cases in saved_selection.items():
                        self.selected_cases[module] = cases
                    logging.info("已加载保存的测试用例选择状态")
        except Exception as e:
            logging.error(f"加载选择状态失败: {str(e)}", exc_info=True)
            self.selected_cases = defaultdict(list)