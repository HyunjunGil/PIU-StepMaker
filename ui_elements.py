import pygame, pygame_gui, copy, time


from tkinter.filedialog import askopenfilename
from file_manager import *
from abc import *
from typing import List, Tuple, Dict, Union
from pygame import Rect
from pygame_gui.elements import UIButton, UITextEntryLine, UIPanel, UITextBox, UILabel

type UIElement = Union[UIButton, UITextEntryLine, UIPanel, UITextBox, UILabel]

from history_manager import (
    HistoryManager,
    BlockModifyDelta,
    BlockAddAboveDelta,
    BlockAddBelowDelta,
    BlockSplitDelta,
    BlockDeleteDelta,
)
from state import State
from utils import update_validity, ms_to_beats, beats_to_ms, num_to_str
from constants import *
from block_logic import *

from file_manager import save_ucs_file, load_ucs_file
from scroll_manager import ScrollManager


class ElementBase:

    def __init__(
        self,
        element: UIElement,
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
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, "ElementBase"],
    ):
        raise Exception("Action for ElementBase is not implemented")


# TODO : Seperate files for each buttons


class FileButton(ElementBase):
    def __init__(self, element: UIButton):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


class LoadButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        file_path = askopenfilename(
            title="Select an UCS file", filetypes=[("Ucs Files", "*.ucs")]
        )
        if not file_path:
            return
        elif not file_path.endswith("ucs"):
            print("Invalid File. Selected File must be .ucs file")
            return

        ucs_file_path = file_path
        mp3_file_path = ucs_file_path[:-3] + "mp3"
        if not os.path.exists(mp3_file_path):
            print("MP3 file is not exists")
            return
        step_size_idx = state.step_size_idx
        state.initialize()
        state.step_size_idx = step_size_idx
        load_ucs_file(ucs_file_path, state)
        load_music_file(mp3_file_path, state)
        state.ucs_file_path = ucs_file_path
        state.ucs_save_path = state.ucs_cache_path = ucs_file_path[:-4] + "+cache.ucs"

        history_manager.initialize(state)

        ui_elements[SCROLLBAR_UP_BUTTON].set_location((state.scrollbar_x_start, 0))
        ui_elements[SCROLLBAR_DOWN_BUTTON].set_location(
            (state.scrollbar_x_start, state.screen_height)
        )
        ScrollManager.update_scrollbar_info(state)
        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
        ui_elements[BI_APPLY_BUTTON].e.disable()


class LoadMP3Button(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


class SaveButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        save_ucs_file(state)


class SaveAsButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


class PlaySpeedButton(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 0
class PlayButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        if state.music_len == 0:
            print("MUSIC NOT LOADED")
            return
        if state.MUSIC_PLAYING:
            state.MUSIC_PLAYING = False
            pygame.mixer.music.stop()
        else:
            state.music_start_time = int(time.time() * 1000)
            state.music_start_offset = state.scr_to_time[state.scr_y]
            state.MUSIC_PLAYING = True
            pygame.mixer.music.play(loops=0, start=state.music_start_offset / 1000)


# UI_INDEX : 3
class UndoButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        history_manager.undo(state)


# UI_INDEX : 4
class RedoButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        history_manager.redo(state)


def _get_block_info_texts(ui_elements: Dict[str, ElementBase]) -> List[str]:
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


def _str_to_num(x: str):
    try:
        return int(x)
    except:
        return round(float(x), 4)


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
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            new_info = _get_block_info_texts(ui_elements)
            if (
                state.delay_unit == DelayUnit.beats
                and len(new_info[BLOCK_DL_IDX])
                and len(new_info[BLOCK_BPM_IDX])
            ):
                new_info[BLOCK_DL_IDX] = num_to_str(
                    beats_to_ms(
                        float(new_info[BLOCK_BPM_IDX]), float(new_info[BLOCK_DL_IDX])
                    )
                )
            step_data, block_info = state.get_step_info()
            info = block_info[step_data[state.coor_cur[1]][STEP_DATA_BI_IDX]]
            info = [num_to_str(x) for x in info]
            if _enable_apply_button(info, new_info):
                ui_elements[BI_APPLY_BUTTON].enable()
                state.APPLY_ENABLED = True
            else:
                ui_elements[BI_APPLY_BUTTON].disable()
                state.APPLY_ENABLED = False
            # self.e.redraw()
        else:
            pygame.event.post(
                pygame.event.Event(
                    pygame_gui.UI_BUTTON_PRESSED,
                    {
                        "user_type": pygame_gui.UI_BUTTON_PRESSED,
                        "ui_element": ui_elements[BI_APPLY_BUTTON].e,
                        # "ui_object_id": button.most_specific_combined_id,
                    },
                )
            )

    def set_text(self, s: str):
        self.e.set_text(s)
        self.e.redraw()


# UI_INDEX : 5
class BPMTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters([f"{i}" for i in range(10)] + ["."])

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 6
class BeatPerMeasureTextbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 7
class SplitPerBeatTextbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 8
class DelayTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters([f"{i}" for i in range(10)] + ["."])

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 9
class DelayUnitButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        if state.delay_unit == DelayUnit.ms:
            self.e.set_text("beats")
            state.update_y_info()
            state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
            state.delay_unit = DelayUnit.beats
        else:
            self.e.set_text("ms")
            state.update_y_info()
            state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
            state.delay_unit = DelayUnit.ms


# UI_INDEX : 10
class MeasuresTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 11
class BeatsTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 12
class SplitsTexbox(BlockInformationText):
    def __init__(self, element: UIElement):
        super().__init__(element)
        self.e.set_allowed_characters("numbers")

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 13
class ApplyButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        new_info = [_str_to_num(x) for x in _get_block_info_texts(ui_elements)]
        if state.delay_unit == DelayUnit.beats:
            new_info[BLOCK_DL_IDX] = beats_to_ms(
                new_info[BLOCK_BPM_IDX], new_info[BLOCK_DL_IDX]
            )
        step_data, block_info = state.get_step_info()
        coor_undo = (state.coor_cur, state.coor_base)
        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
        prev_block_step_data = copy.deepcopy(step_data[ln_from:ln_to])
        prev_block_info = block_info[block_idx]

        step_data, block_info = modify_block(step_data, block_info, new_info, block_idx)
        update_validity(step_data, ln_from, ln_to)
        state.step_data = step_data
        state.block_info = block_info
        state.update_y_info()

        state.coor_cur = (state.coor_cur[0], min(len(step_data) - 1, state.coor_cur[1]))
        state.coor_base = (
            state.coor_base[0],
            min(len(step_data) - 1, state.coor_base[1]),
        )
        coor_redo = (state.coor_cur, state.coor_base)
        if state.focus_idx == BI_APPLY_BUTTON:
            state.focus_idx = -1

        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
        history_manager.append(
            BlockModifyDelta(
                coor_undo,
                coor_redo,
                prev_block_step_data,
                prev_block_info,
                new_info,
                block_idx,
            )
        )


# UI_INDEX : 14
class BlockAddAboveButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        step_data, block_info = state.get_step_info()

        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]

        coor_undo = (state.coor_cur, state.coor_base)

        state.step_data, state.block_info = add_block_up(
            step_data, block_info, block_idx
        )
        state.update_y_info()
        ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
        update_validity(state.step_data, ln_from, ln_to)

        coor_redo = (state.coor_cur, state.coor_base)

        state.focus_idx = BO_BLOCK_ADD_A_BUTTON

        history_manager.append(BlockAddAboveDelta(coor_undo, coor_redo, block_idx))


# UI_INDEX : 15
class BlockAddBelowButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        step_data, block_info = state.get_step_info()

        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]

        coor_undo = (state.coor_cur, state.coor_base)

        state.step_data, state.block_info = add_block_down(
            step_data, block_info, block_idx
        )
        state.update_y_info()
        ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
        update_validity(state.step_data, ln_from, ln_to)

        coor_redo = (state.coor_cur, state.coor_base)

        state.focus_idx = BO_BLOCK_ADD_B_BUTTON

        history_manager.append(BlockAddBelowDelta(coor_undo, coor_redo, block_idx))


# UI_INDEX : 16
class BlockSplitButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        step_data, block_info = state.get_step_info()
        coor_undo = (state.coor_cur, state.coor_base)
        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        state.step_data, state.block_info = split_block(
            step_data, block_info, block_idx, ln
        )
        state.update_y_info()

        coor_redo = (state.coor_cur, state.coor_base)

        state.focus_idx = BO_BLOCK_SPLIT_BUTTON
        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

        history_manager.append(BlockSplitDelta(coor_undo, coor_redo, block_idx, ln))


# UI_INDEX : 17
class BlockDeleteButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        step_data, block_info = state.get_step_info()

        # Check that there is only one block
        if len(block_info) == 1:
            print("Cannot delete last block")
            return

        coor_undo = (state.coor_cur, state.coor_base)

        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
        deleted_step_info: List[Tuple[int, int, int]] = []
        for ln in range(ln_from, ln_to):
            for col in range(STEP_DATA_OFFSET, len(step_data[0])):
                if step_data[ln][col] != 0:
                    deleted_step_info.append((ln, col, step_data[ln][col]))
        deleted_block_info = copy.deepcopy(block_info[block_idx])
        state.step_data, state.block_info = delete_block(
            step_data, block_info, block_idx
        )
        update_validity(state.step_data, ln_from - 1, ln_from + 1)
        state.update_y_info()

        state.coor_cur = (
            state.coor_cur[0],
            min(len(state.step_data) - 1, state.coor_cur[1]),
        )
        state.coor_base = (
            state.coor_base[0],
            min(len(state.step_data) - 1, state.coor_base[1]),
        )

        coor_redo = (state.coor_cur, state.coor_base)

        state.focus_idx = BO_BLOCK_DELETE_BUTTON
        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True

        history_manager.append(
            BlockDeleteDelta(
                coor_undo, coor_redo, deleted_step_info, deleted_block_info, block_idx
            )
        )


class AutoLinePassButton(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


class FixLineToReceptor(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


class LogClearButton(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        return super().action(history_manager, state, event, ui_elements)


# UI_INDEX : 18
class ScrollUpButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        state.scr_y = max(state.scr_y - SCROLL_SPEED, 0)

    def set_location(self, loc: Tuple[int, int]):
        self.e.get_abs_rect().topleft = loc
        self.e.rebuild()


# UI_INDEX : 19
class ScrollDownButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    def action(
        self,
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        state.scr_y = min(state.scr_y + SCROLL_SPEED, state.max_y)

    def set_location(self, loc: Tuple[int, int]):
        self.e.get_abs_rect().bottomleft = loc
        self.e.rebuild()
