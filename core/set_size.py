import time


def set_size(item, directoin, offset):
    # 获取 Pane 的坐标
    rect = item.rectangle()
    # print(f"当前Pane坐标范围：{rect}")
    if directoin == 0:
        # 计算右下边缘点作为拖拽起点
        start_x = (rect.right - rect.left) // 2
        start_y = rect.top - 3
    elif directoin == 7:
        # 计算右下边缘点作为拖拽起点
        start_x = rect.right
        start_y = rect.bottom

    # 拖拽终点（向右拉伸 100 像素）
    end_x = start_x + offset[0]
    end_y = start_y + offset[1]

    # 执行拖拽操作
    item.drag_mouse_input(
        src=(start_x, start_y),
        dst=(end_x, end_y)
    )
    time.sleep(1)
