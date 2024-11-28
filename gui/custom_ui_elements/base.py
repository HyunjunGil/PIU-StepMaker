import pygame_gui, pygame
from typing import List, Tuple, Dict, Union

type UIElement = Union[UIButton, UITextEntryLine, UIPanel, UITextBox, UILabel]

from constants import *
from pygame_gui.elements import UIButton, UITextEntryLine, UIPanel, UITextBox, UILabel
from manager.history_manager import HistoryManager
from manager.state_manager import State


class ElementBase:

    def __init__(self, element: UIElement):
        self.e = element

    def is_enable(self):
        return self.e.is_enabled

    def enable(self):
        self.e.enable()

    def disable(self):
        self.e.disable()

    def focus(self):
        if type(self.e) == pygame_gui.elements.UITextEntryLine:
            self.e.focus()

    def unfocus(self):
        if type(self.e) == pygame_gui.elements.UITextEntryLine:
            self.e.unfocus()

    def get_text(self):
        return self.e.get_text()

    def condition(self, state: State, event: pygame.Event):
        if type(self.e) == pygame_gui.elements.UIButton:
            return (
                event.type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element == self.e
            )
        elif type(self.e) == pygame_gui.elements.UITextEntryLine:
            return (
                event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED
                and event.ui_element == self.e
            )
        else:
            return False

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, "ElementBase"],
    ):
        raise Exception("Action for ElementBase is not implemented")


def get_block_info_texts(ui_elements: Dict[str, ElementBase]) -> List[str]:
    info = []
    for k in [
        BI_BPM_TEXTBOX,
        BI_BM_TEXTBOX,
        BI_BS_TEXTBOX,
        BI_DL_TEXBOX,
        BI_MS_TEXTBOX,
        BI_BT_TEXTBOX,
        BI_SP_TEXTBOX,
    ]:
        info.append(ui_elements[k].get_text())
    return info
