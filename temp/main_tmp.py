import pygame
import sys
import time

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Merge Cells in Grid with Movable Square")

# 색상 및 격자 속성 설정
white = (255, 255, 255)
black = (0, 0, 0)
light_gray = (200, 200, 200)  # 연한 회색
dark_gray = (169, 169, 169)  # 어두운 회색
cell_size = 50  # 각 격자의 크기 (정사각형)
cols = 7  # 열의 개수
rows = 100  # 예시로 100개의 행을 생성 (N값을 의미하며, 커질 수 있음)

# 선택 상태 변수
start_select_pos = None
current_select_pos = None
shift_mode = False
selected_rects = set()

# 스크롤 관련 변수
scroll_y = 0  # 스크롤 위치
scroll_speed = 20  # 마우스 휠 스크롤 속도

# 정사각형의 초기 위치
square_x = 3 * cell_size  # 1행 3열 (0부터 시작하므로 3)
square_y = 0  # 1행 (0행)

# 전체 격자 높이
grid_height = rows * cell_size

# 정사각형 이동 속도 제어 변수
delay = 500  # 0.5초 간격

# 키 누름 시간 기록을 위한 딕셔너리
square_keys = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_UP: 0, pygame.K_DOWN: 0}

# 이미지 로드 및 설정 (3열부터 7열까지의 5개의 이미지)
images = [pygame.image.load(f"{i}.png").convert_alpha() for i in range(3, 8)]
image_rects = {}  # 이미지가 출력될 위치를 저장하는 딕셔너리

# 이벤트가 스크롤인지, 방향키인지 확인
is_scroll = False

# 게임 루프
running = True
while running:
    # 이벤트 처리
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 방향키와 WASD키 눌림 시간 기록 및 이동 처리
        elif event.type == pygame.KEYDOWN:
            is_scroll = False
            # 검은 테두리 정사각형 (방향키)
            if event.key in square_keys:
                if square_keys[event.key] == 0:  # 처음 누를 때 시간 기록
                    square_keys[event.key] = current_time

                # 초기 이동
                if event.key == pygame.K_LEFT:
                    square_x = max(square_x - cell_size, 2 * cell_size)
                elif event.key == pygame.K_RIGHT:
                    square_x = min(square_x + cell_size, 6 * cell_size)
                elif event.key == pygame.K_UP:
                    square_y = max(square_y - cell_size, 0)
                elif event.key == pygame.K_DOWN:
                    square_y = min(square_y + cell_size, (rows - 1) * cell_size)

            elif event.key == pygame.K_ESCAPE:
                square_x = -cell_size  # 화면 밖으로 이동시켜서 사라지게 함

            elif event.key == pygame.K_SPACE:
                # 현재 선택된 격자가 3~7열 사이에 있는 경우
                selected_col = square_x // cell_size
                if 2 <= selected_col <= 6:
                    # 선택된 열에 맞는 이미지 인덱스
                    image_index = selected_col - 2
                    # 이미지가 이미 있는 경우 제거, 없는 경우 추가
                    if (square_x, square_y) in image_rects:
                        del image_rects[(square_x, square_y)]
                    else:
                        image_rects[(square_x, square_y)] = images[image_index]

        # 키를 뗄 때 시간 초기화
        elif event.type == pygame.KEYUP:
            if event.key in square_keys:
                square_keys[event.key] = 0

        # 마우스 휠 스크롤 처리
        elif event.type == pygame.MOUSEBUTTONDOWN:
            is_scroll = True
            if event.button == 4:  # 마우스 휠 업
                scroll_y = max(scroll_y - scroll_speed, 0)
            elif event.button == 5:  # 마우스 휠 다운
                scroll_y = min(scroll_y + scroll_speed, grid_height - screen_height)
            elif event.button == 1:  # 왼쪽 마우스 클릭
                mouse_x, mouse_y = event.pos
                grid_x = mouse_x // cell_size
                grid_y = (mouse_y + scroll_y) // cell_size

                # 클릭한 격자가 3열 이상인지 확인
                if 2 <= grid_x < cols:
                    # 정사각형이 존재하는 경우
                    if (
                        square_x // cell_size == grid_x
                        and square_y // cell_size == grid_y
                    ):
                        # 정사각형을 해당 격자로 이동
                        square_x = grid_x * cell_size
                        square_y = grid_y * cell_size
                    else:
                        # 빈 검은색 정사각형 생성
                        square_x = grid_x * cell_size
                        square_y = grid_y * cell_size

    # 방향키로 검은 테두리 정사각형 연속 이동
    keys = pygame.key.get_pressed()
    for key, start_time in square_keys.items():
        if keys[key] and start_time != 0 and current_time - start_time > delay:
            if key == pygame.K_LEFT:
                square_x = max(square_x - cell_size, 2 * cell_size)
            elif key == pygame.K_RIGHT:
                square_x = min(square_x + cell_size, 6 * cell_size)
            elif key == pygame.K_UP:
                square_y = max(square_y - cell_size, 0)
            elif key == pygame.K_DOWN:
                square_y = min(square_y + cell_size, (rows - 1) * cell_size)

    # 화면을 흰색으로 채우기
    screen.fill(white)

    # 격자 그리기
    for row in range(rows):
        for col in range(cols):
            # 1열만 그리기
            if col == 0 and row % 8 == 0:
                # 병합된 큰 사각형 그리기
                x = col * cell_size
                y = row * cell_size - scroll_y
                width = cell_size * 2  # 두 열 병합
                height = cell_size * 8  # 여덟 행 병합

                # 화면에 표시될 때만 그리기
                if -cell_size * 8 < y < screen_height:
                    pygame.draw.rect(screen, black, (x, y, width, height), 2)

            # 나머지 셀 그리기 (병합되지 않은 셀들)
            elif col > 1:
                x = col * cell_size
                y = row * cell_size - scroll_y

                # 화면에 표시될 때만 그리기
                if -cell_size < y < screen_height:
                    pygame.draw.rect(
                        screen, light_gray, (x, y, cell_size, cell_size), 1
                    )

    # 정사각형 그리기 (경계선만 검은색, 내부는 비어있음)
    pygame.draw.rect(
        screen, black, (square_x, square_y - scroll_y, cell_size, cell_size), 2
    )

    # 화면이 정사각형을 따라 움직이도록 설정
    if not is_scroll and square_y - scroll_y < 0:
        scroll_y = square_y  # 화면이 위로 스크롤
    elif not is_scroll and square_y - scroll_y > screen_height - cell_size:
        scroll_y = square_y - (screen_height - cell_size)  # 화면이 아래로 스크롤

    # 이미지 출력
    for (x, y), image in image_rects.items():
        screen.blit(image, (x, y - scroll_y))

    # 화면 업데이트
    pygame.display.flip()

    # 프레임 속도 설정
    pygame.time.Clock().tick(30)
