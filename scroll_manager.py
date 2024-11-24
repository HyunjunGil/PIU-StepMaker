from state import State
from constants import *


class ScrollManager:
    def update_scrollbar_info(state: State):
        screen_height, max_y = (
            state.screen_height - 2 * SCROLLBAR_BUTTON_HEIGHT,
            state.max_y,
        )
        state.scrollbar_h = max(
            MIN_SCROLL_BAR_HEIGHT,
            min(screen_height, (screen_height * screen_height) // max_y),
        )
