import pygame
import sys

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Two Movable Squares with Continuous Movement")

# 색상과 정사각형 속성
white = (255, 255, 255)
blue = (0, 0, 255)
black = (0, 0, 0)
square_size = 50
speed = 5
delay = 500  # 2초 (2000 밀리초) 이상 누를 경우 연속 이동

# 정사각형 초기 위치
blue_square_x, blue_square_y = 100, 100  # 파란색 정사각형 위치
border_square_x, border_square_y = 300, 300  # 검은색 테두리 정사각형 위치

# 키 누름 시간 기록을 위한 딕셔너리
blue_square_keys = {pygame.K_a: 0, pygame.K_d: 0, pygame.K_w: 0, pygame.K_s: 0}
border_square_keys = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_UP: 0, pygame.K_DOWN: 0}

# 게임 루프
running = True
while running:
    # 현재 시간 확인
    current_time = pygame.time.get_ticks()

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 방향키와 WASD키 눌림 시간 기록 및 이동 처리
        if event.type == pygame.KEYDOWN:
            # 검은 테두리 정사각형 (방향키)
            if event.key in border_square_keys:
                if border_square_keys[event.key] == 0:  # 처음 누를 때 시간 기록
                    border_square_keys[event.key] = current_time

                # 초기 이동
                if event.key == pygame.K_LEFT:
                    border_square_x -= speed
                elif event.key == pygame.K_RIGHT:
                    border_square_x += speed
                elif event.key == pygame.K_UP:
                    border_square_y -= speed
                elif event.key == pygame.K_DOWN:
                    border_square_y += speed

            # 파란색 정사각형 (WASD 키)
            elif event.key in blue_square_keys:
                if blue_square_keys[event.key] == 0:  # 처음 누를 때 시간 기록
                    blue_square_keys[event.key] = current_time

                # 초기 이동
                if event.key == pygame.K_a:
                    blue_square_x -= speed
                elif event.key == pygame.K_d:
                    blue_square_x += speed
                elif event.key == pygame.K_w:
                    blue_square_y -= speed
                elif event.key == pygame.K_s:
                    blue_square_y += speed

        # 키를 뗄 때 시간 초기화
        if event.type == pygame.KEYUP:
            if event.key in border_square_keys:
                border_square_keys[event.key] = 0
            elif event.key in blue_square_keys:
                blue_square_keys[event.key] = 0

    # 방향키로 검은 테두리 정사각형 연속 이동
    keys = pygame.key.get_pressed()
    for key, start_time in border_square_keys.items():
        if keys[key] and start_time != 0 and current_time - start_time > delay:
            if key == pygame.K_LEFT:
                border_square_x -= speed
            elif key == pygame.K_RIGHT:
                border_square_x += speed
            elif key == pygame.K_UP:
                border_square_y -= speed
            elif key == pygame.K_DOWN:
                border_square_y += speed

    # WASD로 파란색 정사각형 연속 이동
    for key, start_time in blue_square_keys.items():
        if keys[key] and start_time != 0 and current_time - start_time > delay:
            if key == pygame.K_a:
                blue_square_x -= speed
            elif key == pygame.K_d:
                blue_square_x += speed
            elif key == pygame.K_w:
                blue_square_y -= speed
            elif key == pygame.K_s:
                blue_square_y += speed

    # 화면을 흰색으로 채우기
    screen.fill(white)
    
    # 파란색 정사각형 그리기
    pygame.draw.rect(screen, blue, (blue_square_x, blue_square_y, square_size, square_size))

    # 검은 테두리 정사각형 그리기 (채우지 않고 테두리만)
    pygame.draw.rect(screen, black, (border_square_x, border_square_y, square_size, square_size), 3)

    # 화면 업데이트
    pygame.display.flip()

    # 프레임 속도 설정
    pygame.time.Clock().tick(30)
