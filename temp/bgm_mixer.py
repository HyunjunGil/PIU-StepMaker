import tkinter as tk
from tkinter import ttk
import pygame
from mutagen.mp3 import MP3

# Pygame 초기화
pygame.init()
pygame.mixer.init()

# 음악 파일 로드 및 길이 가져오기
music_file = "your_music_file.mp3"  # 원하는 음악 파일로 변경
pygame.mixer.music.load(music_file)

# 파일 길이 계산 (초)
audio = MP3(music_file)
music_length = int(audio.info.length)

# 음악 재생 상태 변수
is_playing = False


# 음악 재생 시간 업데이트 함수
def update_scroll_position():
    if is_playing:
        position = pygame.mixer.music.get_pos() // 1000  # 현재 재생 위치 (초)
        scrollbar.set(position)
    root.after(20, update_scroll_position)  # 20ms마다 업데이트


# 스페이스바로 재생/일시정지 토글
def toggle_play(event=None):
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False
    else:
        if pygame.mixer.music.get_pos() > 0:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play()
        is_playing = True


# 스크롤바 이동 후 마우스 릴리스 시 음악 위치 설정
def set_music_position(event=None):
    global is_playing
    pos_in_seconds = int(float(scrollbar.get()))
    pygame.mixer.music.play(0, pos_in_seconds)
    is_playing = True


# Tkinter 윈도우 생성
root = tk.Tk()
root.title("Music Player with Smooth Scroll Control")

# 스크롤바 생성
scrollbar = ttk.Scale(root, from_=0, to=music_length, orient="horizontal", length=400)
scrollbar.pack(pady=20)

# 마우스 릴리스 이벤트 바인딩 (스크롤바 이동 후 위치 설정)
scrollbar.bind("<ButtonRelease-1>", set_music_position)

# 스페이스바 바인딩
root.bind("<space>", toggle_play)

# 음악 재생 시간 업데이트 시작
update_scroll_position()

# Tkinter GUI 실행
root.mainloop()

# 종료 시 Pygame 정리
pygame.quit()
