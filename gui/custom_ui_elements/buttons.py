import os, numpy as np, time, copy
from gui.custom_ui_elements.base import *
from constants import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from utils import (
    str_to_num,
    beats_to_ms,
    update_validity,
)
from core import (
    modify_block,
    add_block_up,
    add_block_down,
    split_block,
    delete_block,
    save_ucs_file,
    load_ucs_file,
    load_music_file,
)
from manager.history_manager import (
    BlockModifyDelta,
    BlockAddAboveDelta,
    BlockAddBelowDelta,
    BlockSplitDelta,
    BlockDeleteDelta,
)


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
        state.initialize(state.get_screen_size())
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
        state.update_scrollbar_info()
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

        # state.focus_idx = FILE_PLAYSPEED_BUTTON


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
            state.beat_ln = -1
            state.MUSIC_PLAYING = False
        else:
            if state.music_len != 0:
                music_speed = MUSIC_SPEED_MAP[state.music_speed_idx]

                new_frame_rate = int(state.music.frame_rate * music_speed)
                audio = state.music._spawn(
                    state.music.raw_data, overrides={"frame_rate": new_frame_rate}
                ).set_frame_rate(PYGAME_SAMPLE_RATE)
                raw_data = np.array(audio.get_array_of_samples())

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
                state.music_start_time = int(time.time() * 1000)
            else:
                state.music_start_time = int(time.time() * 1000)
                state.music_start_offset = int(
                    state.scr_to_time[state.scr_y + state.receptor_y]
                )
            state.MUSIC_PLAYING = True

        # state.focus_idx = FILE_PLAY_BUTTON


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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot modify block while music playing")
            return
        new_info = [str_to_num(x) for x in get_block_info_texts(ui_elements)]
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
        try:
            new_step_data, new_block_info = modify_block(
                step_data, block_info, new_info, block_idx
            )
            valid, error_msg = state.is_valid_step_info(new_step_data, new_block_info)
            if not valid:
                state.log(f"(Error) {error_msg}")
                return
        except:
            state.log("(Error) Failed to modify block. Please check your input")
            return
        state.step_data = new_step_data
        state.block_info = new_block_info
        update_validity(state.step_data, ln_from, ln_to)
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
        state.sync_scr_y()
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot add block while music playing")
            return
        step_data, block_info = state.get_step_info()

        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
        block_height = state.ln_to_y[ln_to] - state.ln_to_y[ln_from]
        if len(step_data) + (ln_to - ln_from) > HARD_MAX_LINES:
            state.log("(Error) Cannot add block. Maximum line number reached")
            return
        elif state.max_y + block_height >= HARD_MAX_Y:
            state.log("(Error) Cannot add block. Maximum scrollable height reached")
            return
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
        # state.focus_idx = BO_BLOCK_ADD_A_BUTTON
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot add block while music playing")
            return

        step_data, block_info = state.get_step_info()

        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        ln_from, ln_to = state.get_block_range_by_block_idx(block_idx)
        block_height = state.ln_to_y[ln_to] - state.ln_to_y[ln_from]
        if len(step_data) + (ln_to - ln_from) > HARD_MAX_LINES:
            state.log("(Error) Cannot add block. Maximum line number reached")
            return
        elif state.max_y + block_height >= HARD_MAX_Y:
            state.log("(Error) Cannot add block. Maximum scrollable height reached")
            return

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
        # state.focus_idx = BO_BLOCK_ADD_B_BUTTON
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot split block while music playing")
            return

        step_data, block_info = state.get_step_info()
        coor_undo = (state.coor_cur, state.coor_base)
        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        ln_from, _ = state.get_block_range_by_block_idx(block_idx)
        if ln_from == ln:
            state.log("Cannot split the block at first line of it")
            return
        state.step_data, state.block_info = split_block(
            step_data, block_info, block_idx, ln
        )
        state.update_y_info()
        state.update_scr_to_time()

        coor_redo = (state.coor_cur, state.coor_base)

        state.log(f"(Split) Block #{block_idx} is splited")
        # state.focus_idx = BO_BLOCK_SPLIT_BUTTON
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
        if state.MUSIC_PLAYING:
            state.log("(Error) Cannot delete block while music playing")
            return

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
        # state.focus_idx = BO_BLOCK_DELETE_BUTTON
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
        # state.focus_idx = LOG_CLEAR_BUTTON


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
        if state.MUSIC_PLAYING:
            return
        state.scr_y = max(state.scr_y - SCROLL_SPEED, -state.receptor_y)

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
        if state.MUSIC_PLAYING:
            return
        state.scr_y = min(state.scr_y + SCROLL_SPEED, state.max_y - state.receptor_y)

    def set_location(self, loc: Tuple[int, int]):
        self.e.get_abs_rect().bottomleft = loc
        self.e.rebuild()
