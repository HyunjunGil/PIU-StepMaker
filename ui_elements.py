import pygame, pygame_gui, copy, time, io, numpy as np


from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
from tkinter.filedialog import askopenfilename, asksaveasfilename
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
            return False

    @staticmethod
    def action(
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

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        sub_panel = ui_elements[FILE_LOAD_BUTTON].e.ui_container
        if sub_panel.visible:
            sub_panel.hide()
        else:
            sub_panel.show()
            state.focus_idx = FILE_BUTTON
        pass


class LoadButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        file_path = askopenfilename(
            title="Select an UCS file", filetypes=[("Ucs Files", "*.ucs")]
        )
        if not file_path:
            state.log("UCS file is not selected")
            return
        ucs_file_path = file_path
        mp3_file_path = ucs_file_path[:-3] + "mp3"
        ucs_name = file_path.split("/")[-1]
        mp3_name = mp3_file_path.split("/")[-1]
        if state.AUTO_LINE_PASS:
            AutoLinePassButton.off(history_manager, state, event, ui_elements)
        if state.FIX_LINE:
            FixLineModeButton.off(history_manager, state, event, ui_elements)
        step_size_idx = state.step_size_idx
        state.initialize()
        state.step_size_idx = step_size_idx
        load_ucs_file(ucs_file_path, state)
        if not os.path.exists(mp3_file_path):
            state.log("(Warning) MP3 file is not loaded")
        else:
            load_music_file(state, mp3_file_path)
            state.log(f"MP3 file {mp3_name} is loaded")

        state.ucs_file_path = state.ucs_save_path = ucs_file_path
        state.ucs_cache_path = ucs_file_path[:-4] + ".cache.ucs"

        history_manager.initialize(state)

        ui_elements[SCROLLBAR_UP_BUTTON].set_location((state.scrollbar_x_start, 0))
        ui_elements[SCROLLBAR_DOWN_BUTTON].set_location(
            (state.scrollbar_x_start, state.screen_height)
        )
        ScrollManager.update_scrollbar_info(state)
        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
        ui_elements[BI_APPLY_BUTTON].e.disable()
        state.log(f"UCS file {ucs_name} is loaded")

        # Hide sub-panel
        state.focus_idx = -1


class LoadMP3Button(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        file_path = askopenfilename(
            title="Select an mp3 file", filetypes=[("mp3 Files", "*.mp3")]
        )
        if not file_path:
            return
        mp3_file_path = file_path
        file_name = mp3_file_path.split("/")[-1]
        if not os.path.exists(mp3_file_path):
            state.log("MP3 file is not selected")
            return
        load_music_file(state, mp3_file_path)
        state.log(f"MP3 file {file_name} is loaded")
        # Hide sub-panel
        state.focus_idx = -1


class SaveButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        if state.ucs_file_path == "" and state.ucs_save_path == "":
            SaveAsButton.action(history_manager, state, event, ui_elements)

        # Do nothing ucs_save_path is still not updated(ex. quit without select)
        if not state.ucs_save_path:
            return
        save_ucs_file(state)

        state.log(f"Saved to {state.ucs_save_path}")

        # Hide sub-panel
        state.focus_idx = -1


class SaveAsButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        save_path = asksaveasfilename(
            title="Save file as",
            filetypes=[("UCS files", "*.ucs")],
            defaultextension=".ucs",
        )
        if save_path == "":
            return
        state.ucs_save_path = save_path
        SaveButton.action(history_manager, state, event, ui_elements)
        # Hide sub-panel
        state.focus_idx = -1


class PlaySpeedButton(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        if state.music is None:
            state.log("(Warning) Music is not loaded")

        restart = False
        if state.MUSIC_PLAYING:
            PlayButton.action(history_manager, state, event, ui_elements)
            restart = True

        state.music_speed_idx = (state.music_speed_idx + 1) % len(MUSIC_SPEED_MAP)
        music_speed = MUSIC_SPEED_MAP[state.music_speed_idx]
        ui_elements[FILE_PLAYSPEED_BUTTON].e.set_text(f"{music_speed}x")
        if restart:
            PlayButton.action(history_manager, state, event, ui_elements)

        state.focus_idx = FILE_PLAYSPEED_BUTTON


# UI_INDEX : 0
class PlayButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):

        if state.MUSIC_PLAYING:
            if state.music_len != 0:
                pygame.mixer.stop()
            state.MUSIC_PLAYING = False
        else:
            if state.music_len != 0:
                music_speed = MUSIC_SPEED_MAP[state.music_speed_idx]

                new_frame_rate = int(state.music.frame_rate * music_speed)
                audio = state.music._spawn(
                    state.music.raw_data, overrides={"frame_rate": new_frame_rate}
                ).set_frame_rate(PYGAME_SAMPLE_RATE)
                raw_data = np.array(audio.get_array_of_samples())

                state.music_start_time = int(time.time() * 1000)
                state.music_start_offset = int(
                    state.scr_to_time[state.scr_y + state.receptor_y]
                )
                # a = time.time()
                start_idx = int(
                    len(raw_data) * (state.music_start_offset / state.music_len)
                )
                sound = pygame.mixer.Sound(buffer=raw_data[start_idx:].tobytes())
                # print("Elapsed : {:.4f}s".format(time.time() - a))
                sound.play()
            else:
                state.music_start_time = int(time.time() * 1000)
                state.music_start_offset = int(
                    state.scr_to_time[state.scr_y + state.receptor_y]
                )
            state.MUSIC_PLAYING = True

        state.focus_idx = FILE_PLAY_BUTTON


class PlayTimeTextbox(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)
        self.e.disable()

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        pass


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
        ui_elements: List[ElementBase],
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
        else:
            pygame.event.post(
                pygame.event.Event(
                    pygame_gui.UI_BUTTON_PRESSED,
                    {
                        "user_type": pygame_gui.UI_BUTTON_PRESSED,
                        "ui_element": ui_elements[BI_APPLY_BUTTON].e,
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
        ui_elements: List[ElementBase],
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
        ui_elements: List[ElementBase],
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
        ui_elements: List[ElementBase],
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
        ui_elements: List[ElementBase],
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
        ui_elements: List[ElementBase],
    ):
        if state.delay_unit == DelayUnit.ms:
            ui_elements[BI_DL_UNIT_BUTTON].e.set_text("beats")
            state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
            state.delay_unit = DelayUnit.beats
        else:
            ui_elements[BI_DL_UNIT_BUTTON].e.set_text("ms")
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
        ui_elements: List[ElementBase],
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
        ui_elements: List[ElementBase],
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
        ui_elements: List[ElementBase],
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
        ui_elements: List[ElementBase],
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
        state.update_scr_to_time()

        state.coor_cur = (state.coor_cur[0], min(len(step_data) - 1, state.coor_cur[1]))
        state.coor_base = (
            state.coor_base[0],
            min(len(step_data) - 1, state.coor_base[1]),
        )
        coor_redo = (state.coor_cur, state.coor_base)
        state.focus_idx = -1

        state.log(f"Block #{block_idx} is modified")
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

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        step_data, block_info = state.get_step_info()

        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]

        coor_undo = (state.coor_cur, state.coor_base)

        state.step_data, state.block_info = add_block_up(
            step_data, block_info, block_idx
        )
        state.update_y_info()
        state.update_scr_to_time()
        ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
        update_validity(state.step_data, ln_from, ln_to)

        coor_redo = (state.coor_cur, state.coor_base)

        state.log(f"(Add ^) Block #{block_idx} is added")
        state.focus_idx = BO_BLOCK_ADD_A_BUTTON
        history_manager.append(BlockAddAboveDelta(coor_undo, coor_redo, block_idx))


# UI_INDEX : 15
class BlockAddBelowButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        step_data, block_info = state.get_step_info()

        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]

        coor_undo = (state.coor_cur, state.coor_base)

        state.step_data, state.block_info = add_block_down(
            step_data, block_info, block_idx
        )
        state.update_y_info()
        state.update_scr_to_time()
        ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
        update_validity(state.step_data, ln_from, ln_to)

        coor_redo = (state.coor_cur, state.coor_base)

        state.log(f"(Add v) Block #{block_idx + 1} is added")
        state.focus_idx = BO_BLOCK_ADD_B_BUTTON
        history_manager.append(BlockAddBelowDelta(coor_undo, coor_redo, block_idx))


# UI_INDEX : 16
class BlockSplitButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        step_data, block_info = state.get_step_info()
        coor_undo = (state.coor_cur, state.coor_base)
        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        state.step_data, state.block_info = split_block(
            step_data, block_info, block_idx, ln
        )
        state.update_y_info()
        state.update_scr_to_time()

        coor_redo = (state.coor_cur, state.coor_base)

        state.log(f"(Split) Block #{block_idx} is splited")
        state.focus_idx = BO_BLOCK_SPLIT_BUTTON
        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
        history_manager.append(BlockSplitDelta(coor_undo, coor_redo, block_idx, ln))


# UI_INDEX : 17
class BlockDeleteButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        step_data, block_info = state.get_step_info()

        # Check that there is only one block
        if len(block_info) == 1:
            state.log("(Error) Cannot delete last block")
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
        state.update_scr_to_time()

        state.coor_cur = (
            state.coor_cur[0],
            min(len(state.step_data) - 1, state.coor_cur[1]),
        )
        state.coor_base = (
            state.coor_base[0],
            min(len(state.step_data) - 1, state.coor_base[1]),
        )

        coor_redo = (state.coor_cur, state.coor_base)

        state.log(f"(Delete) Block #{block_idx} is deleted")
        state.focus_idx = BO_BLOCK_DELETE_BUTTON
        state.UPDATE_BLOCK_INFORMATION_TEXTBOX = True
        history_manager.append(
            BlockDeleteDelta(
                coor_undo, coor_redo, deleted_step_info, deleted_block_info, block_idx
            )
        )


class OnOffButton(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def on(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        raise Exception("OnOffButton.on is not implemented")

    @staticmethod
    def off(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        raise Exception("OnOffButton.off is not implemented")

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        raise Exception("OnOffButton.action is not implemented")


class AutoLinePassButton(OnOffButton):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def on(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        state.AUTO_LINE_PASS = True
        state.coor_base = (0, state.coor_cur[1])
        state.coor_cur = (state.get_cols() - 1, state.coor_cur[1])
        state.log("(Change mode) Auto Line Pass")

        element = ui_elements[AUTO_LINE_PASS_BUTTON].e
        element.colours["normal_bg"] = pygame.Color(BUTTON_ON_COLOR)
        element.rebuild()

    @staticmethod
    def off(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        state.AUTO_LINE_PASS = False
        state.log("(Change mode) None")

        element = ui_elements[AUTO_LINE_PASS_BUTTON].e
        element.colours["normal_bg"] = pygame.Color(BUTTON_OFF_COLOR)
        element.rebuild()

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):

        if state.AUTO_LINE_PASS:
            AutoLinePassButton.off(history_manager, state, event, ui_elements)

        else:
            AutoLinePassButton.on(history_manager, state, event, ui_elements)


class FixLineModeButton(OnOffButton):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def on(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        state.sync_scr_y()
        state.FIX_LINE = True
        state.log("(Change mode) Fix Line Mode")

        # Adjust receptor_y
        state.receptor_y = state.ln_to_y[state.coor_cur[1]] - state.scr_y

        element = ui_elements[FIX_LINE_BUTTON].e
        element.colours["normal_bg"] = pygame.Color(BUTTON_ON_COLOR)
        element.rebuild()

    @staticmethod
    def off(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        state.FIX_LINE = False
        state.log("(Change mode) None")

        state.scr_y += state.receptor_y
        state.receptor_y = 0

        element = ui_elements[FIX_LINE_BUTTON].e
        element.colours["normal_bg"] = pygame.Color(BUTTON_OFF_COLOR)
        element.rebuild()

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):

        if state.FIX_LINE:
            FixLineModeButton.off(history_manager, state, event, ui_elements)

        else:
            FixLineModeButton.on(history_manager, state, event, ui_elements)


class LogTextbox(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)
        self.e.disable()

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: Dict[str, ElementBase],
    ):
        pass


class LogClearButton(ElementBase):
    def __init__(
        self, element: UIButton | UITextEntryLine | UIPanel | UITextBox | UILabel
    ):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        t = time.strftime("%H:%M:%S")
        ui_elements[LOG_TEXTBOX].e.set_text(f"[{t}] Clear logs")
        state.focus_idx = LOG_CLEAR_BUTTON


# UI_INDEX : 18
class ScrollUpButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        state.scr_y = max(state.scr_y - SCROLL_SPEED, -state.receptor_y)
        state.focus_idx = SCROLLBAR_UP_BUTTON

    def set_location(self, loc: Tuple[int, int]):
        self.e.get_abs_rect().topleft = loc
        self.e.rebuild()


# UI_INDEX : 19
class ScrollDownButton(ElementBase):
    def __init__(self, element: UIElement):
        super().__init__(element)

    def condition(self, state: State, event: pygame.Event):
        return super().condition(state, event)

    @staticmethod
    def action(
        history_manager: HistoryManager,
        state: State,
        event: pygame.Event,
        ui_elements: List[ElementBase],
    ):
        state.scr_y = min(state.scr_y + SCROLL_SPEED, state.max_y - state.receptor_y)
        state.focus_idx = SCROLLBAR_DOWN_BUTTON

    def set_location(self, loc: Tuple[int, int]):
        self.e.get_abs_rect().bottomleft = loc
        self.e.rebuild()
