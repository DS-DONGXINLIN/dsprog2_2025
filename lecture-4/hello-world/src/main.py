import flet as ft


def main(page: ft.Page):
    # 计数器文本
    counter = ft.Text("0", size=50, data=0)

    # 加 1
    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()

    # 减 1
    def decrement_click(e):
        counter.data -= 1
        counter.value = str(counter.data)
        counter.update()

    # 重置为 0
    def reset_click(e):
        counter.data = 0
        counter.value = "0"
        counter.update()

    # 右下角的 + 按钮（和原来一样）
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=increment_click,
    )

    # 页面内容：中间是数字，左下是 −，中下是 Reset
    page.add(
        ft.SafeArea(
            ft.Stack(
                [
                    # 中央的计数器
                    ft.Container(
                        counter,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),

                    # 左下角的 − 按钮
                    ft.Container(
                        ft.FloatingActionButton(
                            icon=ft.Icons.REMOVE,
                            on_click=decrement_click,
                        ),
                        alignment=ft.alignment.bottom_left,
                        padding=20,
                    ),

                    # 底部中央的 Reset 按钮
                    ft.Container(
                        ft.FloatingActionButton(
                            icon=ft.Icons.REPLAY,
                            on_click=reset_click,
                        ),
                    
                    ),
                ],
                expand=True,
            ),
            expand=True,
        )
    )


ft.app(main)