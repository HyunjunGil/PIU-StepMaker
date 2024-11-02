import tkinter as tk
from tkinter import messagebox

# 메인 창 생성
root = tk.Tk()
root.title("Conditional Right-Click Menu Example")
root.geometry("400x300")


# 옵션 기능 정의
def option_a():
    messagebox.showinfo("Option Selected", "You selected option A")


def option_b():
    messagebox.showinfo("Option Selected", "You selected option B")


def option_c():
    messagebox.showinfo("Option Selected", "You selected option C")


def option_d():
    messagebox.showinfo("Option Selected", "You selected option D")


def option_e():
    messagebox.showinfo("Option Selected", "You selected option E")


def option_f():
    messagebox.showinfo("Option Selected", "You selected option F")


def option_g():
    messagebox.showinfo("Option Selected", "You selected option G")


# 중앙의 검은색 사각형 정의
square_size = 100
square_x = (root.winfo_width() - square_size) // 2
square_y = (root.winfo_height() - square_size) // 2

# 메뉴 생성
menu_inside_square = tk.Menu(root, tearoff=0)
menu_inside_square.add_command(label="A", command=option_a)
menu_inside_square.add_command(label="B", command=option_b)
menu_inside_square.add_command(label="C", command=option_c)

menu_outside_square = tk.Menu(root, tearoff=0)
menu_outside_square.add_command(label="D", command=option_d)
menu_outside_square.add_command(label="E", command=option_e)
menu_outside_square.add_command(label="F", command=option_f)
menu_outside_square.add_command(label="G", command=option_g)


# 우클릭 시 조건에 따라 메뉴 표시 함수
def show_menu(event):
    # 현재 클릭 위치가 사각형 안에 있는지 확인
    if (
        square_x <= event.x <= square_x + square_size
        and square_y <= event.y <= square_y + square_size
    ):
        menu_inside_square.post(event.x_root, event.y_root)
    else:
        menu_outside_square.post(event.x_root, event.y_root)


# 검은색 정사각형 그리기
canvas = tk.Canvas(root, width=400, height=300, bg="white")
canvas.pack(fill="both", expand=True)
square = canvas.create_rectangle(
    square_x, square_y, square_x + square_size, square_y + square_size, fill="black"
)

# 우클릭 이벤트 바인딩
root.bind("<Button-3>", show_menu)

# 메인 루프 실행
root.mainloop()
