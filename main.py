import pygame, pygame_gui, sys, time, numpy as np

from constants import *
from block_logic import *
from pygame import Surface

from stepmaker import *


pygame.init()

screen_width, screen_height = SCREEN_WIDTH, SCREEN_HEIGHT

stepmaker = StepMaker(
    pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
)


running = True

clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60) / 1000.0
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:
            stepmaker.resize_screen(event.size)
        elif event.type in [
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ]:
            stepmaker.process_mouse_event(event)
        elif event.type in [pygame.KEYUP, pygame.KEYDOWN]:
            stepmaker.process_keyboard_event(event)
        elif event.type in [
            pygame_gui.UI_BUTTON_PRESSED,
            pygame_gui.UI_TEXT_ENTRY_CHANGED,
            pygame_gui.UI_TEXT_ENTRY_FINISHED,
        ]:
            stepmaker.process_ui_element_event(event)

        stepmaker.process_ui_manager_event(event)
    stepmaker.process_hold_key()
    stepmaker.update_scr_y()
    stepmaker.ui_manager.manager.update(time_delta)

    stepmaker.update_ui_elements()

    stepmaker.draw()
