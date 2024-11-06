import pygame
import sys

# Pygame 초기화
pygame.init()

# 화면 크기 설정
width, height = 400, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Toggle Color with Ctrl + C")

# 색상 정의
black = (0, 0, 0)
blue = (0, 0, 255)

# 정사각형 설정
square_size = 100
square_pos = (width // 2 - square_size // 2, height // 2 - square_size // 2)
square_color = black

# 토글 플래그 초기화
toggle = False
# key_pressed = False  # 키가 눌린 상태를 추적

# 메인 루프
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 키 상태 확인
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LCTRL] and keys[pygame.K_c]:
        # if not key_pressed:  # 키가 새로 눌렸을 때만 토글
        toggle = not toggle
        square_color = blue if toggle else black
        # key_pressed = True
    # else:
    #     key_pressed = False  # 키를 떼면 다시 초기화

    # 화면 지우기
    screen.fill((255, 255, 255))  # 배경색을 흰색으로 설정

    # 정사각형 그리기
    pygame.draw.rect(
        screen, square_color, (square_pos[0], square_pos[1], square_size, square_size)
    )

    # 화면 업데이트
    pygame.display.flip()
