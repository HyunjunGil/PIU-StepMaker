import pygame
import sys

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Image with Motion Trail")

# 색상 설정
white = (255, 255, 255)

# 이미지 불러오기
image = pygame.image.load("3.png")
image_rect = image.get_rect()
image_rect.topleft = (screen_width // 2, screen_height // 2)  # 초기 위치 중앙

# 이동 속도
move_speed = 1

# 게임 루프
running = True
while running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        image_rect.x -= move_speed
    if keys[pygame.K_RIGHT]:
        image_rect.x += move_speed
    if keys[pygame.K_UP]:
        image_rect.y -= move_speed
    if keys[pygame.K_DOWN]:
        image_rect.y += move_speed

    # 흰색 배경 채우기 (잔상이 남도록 매번 배경을 덮지 않습니다)
    # screen.fill(white)  # 이 줄을 주석 처리해 잔상이 남도록 함

    # 이미지 그리기
    screen.blit(image, image_rect)

    # 화면 업데이트
    pygame.display.flip()

    # 프레임 속도 설정
    pygame.time.Clock().tick(30)
