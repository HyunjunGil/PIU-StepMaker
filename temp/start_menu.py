import pygame
import sys

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Menu")

# 색상 설정
background_color = (255, 255, 255)
text_color = (0, 0, 0)
button_color = (200, 200, 200)
button_hover_color = (170, 170, 170)

# 폰트 설정
title_font = pygame.font.Font(None, 100)  # 큰 폰트 (TEST GAME)
button_font = pygame.font.Font(None, 40)  # 작은 폰트 (New Game, Load)

# 텍스트 렌더링
title_text = title_font.render("TEST GAME", True, text_color)
title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))

new_game_text = button_font.render("New Game", True, text_color)
new_game_rect = new_game_text.get_rect(center=(screen_width // 2, screen_height // 2))

load_text = button_font.render("Load", True, text_color)
load_rect = load_text.get_rect(center=(screen_width // 2, screen_height // 2 + 60))

# 게임 루프
running = True
while running:
    # 마우스 위치 얻기
    mouse_pos = pygame.mouse.get_pos()

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if new_game_rect.collidepoint(mouse_pos):
                print("New Game 버튼이 클릭되었습니다.")
            elif load_rect.collidepoint(mouse_pos):
                print("Load 버튼이 클릭되었습니다.")

    # 배경 색상 채우기
    screen.fill(background_color)

    # 제목 텍스트 그리기
    screen.blit(title_text, title_rect)

    # 버튼 그리기 (마우스 오버 효과 추가)
    if new_game_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, button_hover_color, new_game_rect.inflate(20, 10))
    else:
        pygame.draw.rect(screen, button_color, new_game_rect.inflate(20, 10))
    screen.blit(new_game_text, new_game_rect)

    if load_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, button_hover_color, load_rect.inflate(20, 10))
    else:
        pygame.draw.rect(screen, button_color, load_rect.inflate(20, 10))
    screen.blit(load_text, load_rect)

    # 화면 업데이트
    pygame.display.flip()

    # 프레임 속도 설정
    pygame.time.Clock().tick(30)
