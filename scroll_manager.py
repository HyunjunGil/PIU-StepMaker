from state import State
from constants import *


class ScrollManager:
    def update_scrollbar_info(state: State):
        screen_width, screen_height, max_y = (
            state.screen_width,
            state.screen_height - 2 * SCROLLBAR_BUTTON_HEIGHT,
            state.max_y,
        )
        state.scrollbar_h = max(
            MIN_SCROLL_BAR_HEIGHT,
            min(screen_height, (screen_height * screen_height) // max_y),
        )

        # if state.SCROLLBAR_CLICKED:
        #     _, mouse_y = pygame.mouse.get_pos()
        #     scrollbar_y = min(
        #         max(state.scr_y_init + (mouse_y - state.scr_mouse_init), 0),
        #         screen_height - state.scr_h,
        #     )
        #     scr_y = (scrollbar_y * max_y) // (screen_height - state.scr_h)
        # else:
        #     scrollbar_y = ((screen_height - state.scr_h) * scr_y) // max_y
