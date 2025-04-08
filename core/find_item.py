import time


def find_list_item(parent, title, attempts=20):
    """
    滚动查找函数
    """
    current_attempt = 0
    item = None
    down_btn = parent.child_window(title="向下翻页", auto_id="DownPageButton", control_type="Button")
    for _ in range(attempts):
        try:
            item = parent.child_window(
                title=title,
                control_type="ListItem"
            ).wait("exists ready", timeout=0.2)
            break
        except Exception:
            down_btn.click_input()
            time.sleep(0.1)
        current_attempt += 1
    if item:
        # item.click_input()
        # print("找到目标项！")  # 保持原有输出
        return item
    else:
        print("未找到目标项")  # 保持原有输出
