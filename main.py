import pygame, pygame_gui, sys, time, numpy as np

from typing import List, Tuple
from constants import *
from file_manager import load_ucs_file, save_ucs_file
from block_logic import *
from pygame import Surface

from refactoring import *


pygame.init()

screen_width, screen_height = SCREEN_WIDTH, SCREEN_HEIGHT

stepmaker = StepMaker(
    pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
)

stepmaker.load_initial_ucs_file("sample.ucs")

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
            stepmaker.resize_screen(event)
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            stepmaker.process_mouse_event(event)
        elif event.type == pygame.KEYDOWN:
            stepmaker.process_keyboard_event(event)
        elif event.type in [
            pygame_gui.UI_BUTTON_PRESSED,
            pygame_gui.UI_TEXT_ENTRY_CHANGED,
            pygame_gui.UI_TEXT_ENTRY_FINISHED,
        ]:
            stepmaker.process_ui_element_event(event)

        stepmaker.process_ui_manager_event(event)
    stepmaker.ui_manger.manager.update(time_delta)

    stepmaker.draw()
