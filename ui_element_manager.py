import pygame, pygame_gui

from abc import *
from typing import List, Tuple, Dict
from enum import Enum

from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_text_entry_line import UITextEntryLine
from state import State
from constants import *
from block_logic import *

from file_manager import save_ucs_file, load_ucs_file


class ElementBase:

    def __init__(
        self,
        element: pygame_gui.elements.UIButton | pygame_gui.elements.UITextEntryLine,
    ):
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
            raise Exception("Invalid type of self.e : ${}".format(type(self.e)))

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, "ElementBase"]
    ):
        raise Exception("Action for ElementBase is not implemented")


# TODO : Seperate files for each buttons


# UI_INDEX : 0
class PlayButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (BASIC_ACTION_WIDTH * 0, BASIC_ACTION_AREA_Y), BASIC_ACTION_SIZE
                ),
                text="Play",
                manager=manager,
            ),
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        pass


# UI_INDEX : 1
class SaveButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (BASIC_ACTION_WIDTH * 1, BASIC_ACTION_AREA_Y), BASIC_ACTION_SIZE
                ),
                text="Save",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        save_ucs_file(state)


# UI_INDEX : 2
class LoadButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (
                        BASIC_ACTION_WIDTH * 2,
                        BASIC_ACTION_AREA_Y,
                    ),
                    BASIC_ACTION_SIZE,
                ),
                text="Load",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        load_ucs_file(state.ucs_file_path, state)


# UI_INDEX : 3
class UndoButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (
                        BASIC_ACTION_WIDTH * 3,
                        BASIC_ACTION_AREA_Y,
                    ),
                    BASIC_ACTION_SIZE,
                ),
                text="Undo",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        print("Press Undo Button")


# UI_INDEX : 4
class RedoButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (
                        BASIC_ACTION_WIDTH * 4,
                        BASIC_ACTION_AREA_Y,
                    ),
                    BASIC_ACTION_SIZE,
                ),
                text="Redo",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        print("Press Redo Button")


def _get_block_info_texts(ui_elements: Dict[str, ElementBase]) -> List[str]:
    info = []
    for k in [
        "005_BI_BPM",
        "006_BI_B/M",
        "007_BI_S/B",
        "008_BI_Delay",
        "009_BI_Measures",
        "010_BI_Beats",
        "011_BI_Splits",
    ]:
        info.append(ui_elements[k].get_text())
    return info


def _str_to_num(x: str):
    try:
        return int(x)
    except:
        return round(float(x), 4)


def _num_to_str(x: int | float):
    return str(x)


def _enable_apply_button(info: List[int | float], new_info: List[int | float]) -> bool:
    assert len(info) == len(
        new_info
    ), "len(info) != len(new_info) in _enable_apply_button"
    for v, nv in zip(info, new_info):
        if nv == "":
            return False
        elif v != nv:
            return True
    return False


# Block Information Text Box
class BlockInformationText(ElementBase):
    def __init__(self, element: UITextEntryLine):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return (
            event.type
            in [pygame_gui.UI_TEXT_ENTRY_FINISHED, pygame_gui.UI_TEXT_ENTRY_CHANGED]
            and event.ui_element == self.e
        )

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            new_info = _get_block_info_texts(ui_elements)

            step_data, block_info = state.get_step_info()
            y_to_ln = state.y_to_ln
            info = block_info[step_data[y_to_ln[state.y_cur]][STEP_DATA_BI_IDX]]
            info = [_num_to_str(x) for x in info]
            if _enable_apply_button(info, new_info):
                ui_elements["012_BI_Apply"].enable()
                state.APPLY_ENABLED = True
            else:
                ui_elements["012_BI_Apply"].disable()
                state.APPLY_ENABLED = False
            self.e.redraw()
        else:
            pygame.event.post(
                pygame.event.Event(
                    pygame_gui.UI_BUTTON_PRESSED,
                    {
                        "user_type": pygame_gui.UI_BUTTON_PRESSED,
                        "ui_element": ui_elements["012_BI_Apply"].e,
                        # "ui_object_id": button.most_specific_combined_id,
                    },
                )
            )


# UI_INDEX : 5
class BPMTexbox(BlockInformationText):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(
                    (BI_x1, BLOCK_INFO_AREA_Y + BI_y0),
                    (BI_w1, BI_h),
                ),
                object_id="BI_bpm",
                manager=manager,
            )
        )
        self.e.set_allowed_characters([f"{i}" for i in range(10)] + ["."])

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        return super().action(state, event, ui_elements)


# UI_INDEX : 6
class BeatPerMeasureTextbox(BlockInformationText):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(
                    (BI_x1, BLOCK_INFO_AREA_Y + BI_y1), (BI_w1, BI_h)
                ),
                object_id="BI_bm",
                manager=manager,
            )
        )
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        return super().action(state, event, ui_elements)


# UI_INDEX : 7
class SplitPerBeatTextbox(BlockInformationText):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(
                    (BI_x1, BLOCK_INFO_AREA_Y + BI_y2), (BI_w1, BI_h)
                ),
                object_id="BI_sb",
                manager=manager,
            )
        )
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        return super().action(state, event, ui_elements)


# UI_INDEX : 8
class DelayTexbox(BlockInformationText):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(
                    (BI_x1, BLOCK_INFO_AREA_Y + BI_y3), (BI_w1, BI_h)
                ),
                object_id="BI_delay",
                manager=manager,
            )
        )
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        return super().action(state, event, ui_elements)


# UI_INDEX : 9
class MeasuresTexbox(BlockInformationText):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(
                    (BI_x3, BLOCK_INFO_AREA_Y + BI_y0), (BI_w3, BI_h)
                ),
                object_id="BI_mesures",
                manager=manager,
            )
        )
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        return super().action(state, event, ui_elements)


# UI_INDEX : 10
class BeatsTexbox(BlockInformationText):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(
                    (BI_x3, BLOCK_INFO_AREA_Y + BI_y1), (BI_w3, BI_h)
                ),
                object_id="BI_beats",
                manager=manager,
            )
        )
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        return super().action(state, event, ui_elements)


# UI_INDEX : 11
class SplitsTexbox(BlockInformationText):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(
                    (BI_x3, BLOCK_INFO_AREA_Y + BI_y2), (BI_w3, BI_h)
                ),
                object_id="BI_splits",
                manager=manager,
            )
        )
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        return super().action(state, event, ui_elements)


# UI_INDEX : 12
class ApplyButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (
                        OPTION_WIDTH - BLOCK_BUTTON_SIZE[0] - BLOCK_INFO_GAP,
                        BLOCK_INFO_AREA_Y
                        + BLOCK_INFO_AREA_HEIGHT
                        - BLOCK_BUTTON_SIZE[1]
                        - BLOCK_INFO_GAP,
                    ),
                    BLOCK_BUTTON_SIZE,
                ),
                text="Apply",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        new_info = [_str_to_num(x) for x in _get_block_info_texts(ui_elements)]
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln = y_to_ln[state.y_cur]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        step_data, block_info = modify_block(step_data, block_info, new_info, block_idx)
        state.step_data = step_data
        state.block_info = block_info
        state.update_y_info()
        state.y_cur = state.ln_to_y[state.y_to_ln[state.y_cur]]
        state.y_base = state.ln_to_y[state.y_to_ln[state.y_base]]
        if state.focus_idx == 12:
            state.focus_idx = -1

        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True


# UI_INDEX : 13
class BlockAddAboveButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((BO_x0, BO_y0), BLOCK_OPER_BUTTON_SIZE),
                text="Add ^",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln = y_to_ln[state.y_cur]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        ln_from, ln_to = state.get_block_range(state.y_cur)

        cols = state.get_cols()
        for i in range(cols):
            col = STEP_DATA_OFFSET + i
            if step_data[ln_from][col] in [3, 4]:
                # Unable to do operation since there are long note between block
                print(
                    "Unable to operate BLOCK_ADD_ABOVE : There are long note between current block and previous block"
                )
                return

        state.step_data, state.block_info = add_block_up(
            step_data, block_info, block_idx
        )
        state.update_y_info()
        state.y_cur = state.ln_to_y[state.y_to_ln[state.y_cur]]
        state.y_base = state.ln_to_y[state.y_to_ln[state.y_base]]

        state.focus_idx = 13


# UI_INDEX : 14
class BlockAddBelowButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((BO_x1, BO_y0), BLOCK_OPER_BUTTON_SIZE),
                text="Add v",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln = y_to_ln[state.y_cur]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        ln_from, ln_to = state.get_block_range(state.y_cur)

        cols = state.get_cols()
        for i in range(cols):
            col = STEP_DATA_OFFSET + i
            if step_data[ln_to][col] in [2, 3]:
                # Unable to do operation since there are long note between block
                print(
                    "Unable to operate BLOCK_ADD_BELOW : There are long note between current block and previous block"
                )
                return

        state.step_data, state.block_info = add_block_down(
            step_data, block_info, block_idx
        )
        state.update_y_info()
        state.y_cur = state.ln_to_y[state.y_to_ln[state.y_cur]]
        state.y_base = state.ln_to_y[state.y_to_ln[state.y_base]]

        state.focus_idx = 14


# UI_INDEX : 15
class BlockSplitButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((BO_x2, BO_y0), BLOCK_OPER_BUTTON_SIZE),
                text="Split",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln = y_to_ln[state.y_cur]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        state.step_data, state.block_info = split_block(
            step_data, block_info, block_idx, ln
        )
        state.update_y_info()
        state.y_cur = state.ln_to_y[state.y_to_ln[state.y_cur]]
        state.y_base = state.ln_to_y[state.y_to_ln[state.y_base]]

        state.focus_idx = 15
        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True


# UI_INDEX : 16
class BlockDeleteButton(ElementBase):
    def __init__(self, manager: pygame_gui.UIManager):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((BO_x3, BO_y0), BLOCK_OPER_BUTTON_SIZE),
                text="Delete",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        if len(block_info) == 1:
            print("Cannot delete last block")
            return
        ln = y_to_ln[state.y_cur]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        state.step_data, state.block_info = delete_block(
            step_data, block_info, block_idx
        )
        state.update_y_info()

        state.y_cur = state.y_base = state.ln_to_y[
            state.y_to_ln[min(state.max_y - 1, state.y_cur)]
        ]
        state.focus_idx = 16
        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True


# UI_INDEX : 17
class ScrollUpButton(ElementBase):
    def __init__(
        self, manager: pygame_gui.UIManager, loc: Tuple[int, int], size: Tuple[int, int]
    ):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(loc, size),
                text="^",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        state.scr_y = max(state.scr_y - SCROLL_SPEED, 0)

    def set_location(self, loc: Tuple[int, int]):
        self.e.get_abs_rect().topleft = loc


# UI_INDEX : 18
class ScrollDownButton(ElementBase):
    def __init__(
        self, manager: pygame_gui.UIManager, loc: Tuple[int, int], size: Tuple[int, int]
    ):
        super().__init__(
            pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(loc, size),
                text="v",
                manager=manager,
            )
        )

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self, state: State, event: pygame.Event, ui_elements: Dict[str, ElementBase]
    ):
        state.scr_y = min(state.scr_y + SCROLL_SPEED, state.max_y)

    def set_location(self, loc: Tuple[int, int]):
        self.e.get_abs_rect().bottomleft = loc


class UIElementManager:
    def __init__(self, manager: pygame_gui.UIManager):
        self.manager = manager
        self.ui_elements: Dict[str, ElementBase] = {
            "000_Play": PlayButton(manager),
            "001_Save": SaveButton(manager),
            "002_Load": LoadButton(manager),
            "003_Undo": UndoButton(manager),
            "004_Redo": RedoButton(manager),
            "005_BI_BPM": BPMTexbox(manager),
            "006_BI_B/M": BeatPerMeasureTextbox(manager),
            "007_BI_S/B": SplitPerBeatTextbox(manager),
            "008_BI_Delay": DelayTexbox(manager),
            "009_BI_Measures": MeasuresTexbox(manager),
            "010_BI_Beats": BeatsTexbox(manager),
            "011_BI_Splits": SplitsTexbox(manager),
            "012_BI_Apply": ApplyButton(manager),
            "013_BlockAddAbove": BlockAddAboveButton(manager),
            "014_BlockAddBelow": BlockAddBelowButton(manager),
            "015_BlockSplit": BlockSplitButton(manager),
            "016_BlockDelete": BlockDeleteButton(manager),
            "017_ScrollUp": ScrollUpButton(manager, (0, 0), (SCROLL_BAR_WIDTH, 30)),
            "018_ScrollDown": ScrollDownButton(manager, (0, 0), (SCROLL_BAR_WIDTH, 30)),
        }

    def get_ui_elements(self):
        return self.ui_elements

    def draw(self, state: State, screen: pygame.Surface):
        self.ui_elements["017_ScrollUp"].set_location((state.scrollbar_x_start, 0))
        self.ui_elements["018_ScrollDown"].set_location(
            (state.scrollbar_x_start, state.screen_height)
        )
        self.manager.draw_ui(screen)

    def process_event(self, state: State, event: pygame.Event):
        for k, element in self.ui_elements.items():
            if element.condition(state, event):
                element.action(state, event, self.ui_elements)
                break

    def check_textbox_clicked(self, state: State, event: pygame.Event):
        for i, (k, element) in enumerate(self.ui_elements.items()):
            if type(
                element.e
            ) == pygame_gui.elements.UITextEntryLine and element.e.get_abs_rect().collidepoint(
                event.pos
            ):
                state.LATTICE_CLICKED, state.SCROLLBAR_CLICKED = False, False
                state.focus_idx = i
                break

    def update_block_information_textbox(self, state: State):
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln = y_to_ln[state.y_cur]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        info = block_info[block_idx]
        [bpm, bm, sb, delay, measures, beats, splits] = info

        self.ui_elements["005_BI_BPM"].e.set_text(str(bpm))
        self.ui_elements["005_BI_BPM"].e.redraw()

        self.ui_elements["006_BI_B/M"].e.set_text(str(bm))
        self.ui_elements["006_BI_B/M"].e.redraw()

        self.ui_elements["007_BI_S/B"].e.set_text(str(sb))
        self.ui_elements["007_BI_S/B"].e.redraw()

        self.ui_elements["008_BI_Delay"].e.set_text(str(delay))
        self.ui_elements["008_BI_Delay"].e.redraw()

        self.ui_elements["009_BI_Measures"].e.set_text(str(measures))
        self.ui_elements["009_BI_Measures"].e.redraw()

        self.ui_elements["010_BI_Beats"].e.set_text(str(beats))
        self.ui_elements["010_BI_Beats"].e.redraw()

        self.ui_elements["011_BI_Splits"].e.set_text(str(splits))
        self.ui_elements["011_BI_Splits"].e.redraw()
