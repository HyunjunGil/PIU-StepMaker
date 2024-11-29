import pygame, pygame_gui, time, sys, os, json

from typing import List, Tuple, Dict, Union
from pygame import Rect
from pygame_gui.elements import UIButton, UITextEntryLine, UIPanel, UITextBox, UILabel

type UIElement = Union[UIButton, UITextEntryLine, UIPanel, UITextBox, UILabel]


from manager.state_manager import State
from constants import *
from gui import *
from manager.history_manager import HistoryManager
from utils import *


class UIElementManager:
    def __init__(self):
        self.initialize()

    def get_ui_elements(self):
        return self.ui_elements

    def get_ui_element_by_idx(self, idx: int):
        if idx != -1:
            return self.ui_elements[idx]
        else:
            return None

    def relocate_elements(self, state: State):
        screen_height = state.screen_height
        scrollbar_x, scrollbar_y = (
            self.ui_elements[SCROLLBAR_DOWN_BUTTON].e.get_abs_rect().bottomleft
        )
        if scrollbar_x != state.scrollbar_x_start or scrollbar_y != state.screen_height:
            self.ui_elements[SCROLLBAR_UP_BUTTON].set_location(
                (state.scrollbar_x_start, 0)
            )
            self.ui_elements[SCROLLBAR_DOWN_BUTTON].set_location(
                (state.scrollbar_x_start, state.screen_height)
            )

        PANEL_5_START = 390
        w, h = self.panel_5.get_relative_rect().size
        if PANEL_5_START + h != screen_height:
            new_height = screen_height - PANEL_5_START
            self.panel_5.set_dimensions((w, new_height))
            log_textbox = self.ui_elements[LOG_TEXTBOX].e
            log_clear_button = self.ui_elements[LOG_CLEAR_BUTTON].e

            log_textbox.set_dimensions(
                (log_textbox.get_abs_rect().size[0], new_height - 90)
            )
            log_clear_button.set_relative_position((125, new_height - 40))

    def relocate_scroll_button(self, state: State):
        scrollbar_x, scrollbar_y = (
            self.ui_elements[SCROLLBAR_DOWN_BUTTON].e.get_abs_rect().bottomleft
        )
        if scrollbar_x != state.scrollbar_x_start or scrollbar_y != state.screen_height:
            self.ui_elements[SCROLLBAR_UP_BUTTON].set_location(
                (state.scrollbar_x_start, 0)
            )
            self.ui_elements[SCROLLBAR_DOWN_BUTTON].set_location(
                (state.scrollbar_x_start, state.screen_height)
            )

    def draw(self, state: State, screen: pygame.Surface):
        self.manager.draw_ui(screen)

    def process_event(
        self, history_manager: HistoryManager, state: State, event: pygame.Event
    ):
        for i, element in enumerate(self.ui_elements):
            if element.condition(state, event):
                element.action(history_manager, state, event, self.ui_elements)
                break

    def check_textbox_clicked(self, state: State, event: pygame.Event):
        for i, element in enumerate(self.ui_elements):
            if (
                type(element.e) == pygame_gui.elements.UITextEntryLine
                and element.e.get_abs_rect().collidepoint(event.pos)
                and event.type == pygame.MOUSEBUTTONDOWN
            ):
                state.LATTICE_CLICKED, state.SCROLLBAR_CLICKED = False, False
                state.focus_idx = i
                break

    def check_ui_element_clicked(self, state: State, event: pygame.Event):
        for i, element in enumerate(self.ui_elements):
            if (
                element.e.get_abs_rect().collidepoint(event.pos)
                and event.type == pygame.MOUSEBUTTONDOWN
                and element.e.is_enabled
                and element.e.visible
            ):
                state.LATTICE_CLICKED, state.SCROLLBAR_CLICKED = False, False
                state.focus_idx = i
                break

    def update_block_information_textbox(self, state: State):
        step_data, block_info = state.get_step_info()
        y_to_ln, ln_to_y = state.get_y_info()
        ln = state.coor_cur[1]
        block_idx = step_data[ln][STEP_DATA_BI_IDX]
        info = block_info[block_idx]
        [bpm, bm, sb, delay, measures, beats, splits] = info
        self.ui_elements[BI_BPM_TEXTBOX].set_text(num_to_str(bpm))
        self.ui_elements[BI_BM_TEXTBOX].set_text(str(bm))
        self.ui_elements[BI_BS_TEXTBOX].set_text(str(sb))
        self.ui_elements[BI_DL_TEXBOX].set_text(
            num_to_str(delay)
            if state.delay_unit == DelayUnit.ms
            else num_to_str(ms_to_beats(bpm, delay))
        )
        self.ui_elements[BI_MS_TEXTBOX].set_text(str(measures))
        self.ui_elements[BI_BT_TEXTBOX].set_text(str(beats))
        self.ui_elements[BI_SP_TEXTBOX].set_text(str(splits))

    def initialize(self):

        # if getattr(sys, "frozen", False):  # 실행 파일로 패키징된 상태
        #     base_path = sys._MEIPASS
        #     theme_path = os.path.join(base_path, ".\\assets\\theme.json")

        #     # with open(theme_path, "r") as file:
        #     #     theme_data = file.read()
        #     # print(theme_path)
        #     # theme_data.replace("./assets/d2coding.ttf", theme_path)

        #     # with open(theme_path, "w") as temp_file:
        #     #     temp_file.write(theme_data)

        # else:  # 개발 환경
        #     base_path = os.path.abspath(os.path.dirname(__file__))
        #     base_path = os.path.join(base_path, "..\\")
        #     theme_path = os.path.join(base_path, ".\\assets\\theme.json")

        theme_path = os.path.join(get_base_path(), ".\\assets\\theme.json")
        if getattr(sys, "frozen", False):
            with open(theme_path, "r") as f:
                obj = json.load(f)

            font_path = theme_path.replace("theme.json", "d2coding.ttf")

            obj["@textbox_log"]["font"]["regular_path"] = font_path
            with open(theme_path, "w") as f:
                json.dump(obj, f)

        manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path)

        PANEL_1_HEIGHT = 30
        PANEL_2_HEIGHT = 200
        PANEL_3_HEIGHT = 80
        PANEL_4_HEIGHT = 80
        PANEL_5_HEIGHT = 310
        SUB_PANEL_WIDTH = 80
        SUB_PANEL_HEIGHT = 120
        SUB_PANEL_BUTTON_HEIGHT = SUB_PANEL_HEIGHT // 4

        PANEL_1_BUTTON_WIDTH = 50
        F_x0 = PANEL_1_BUTTON_WIDTH * 0
        F_x1 = PANEL_1_BUTTON_WIDTH * 1
        F_x2 = PANEL_1_BUTTON_WIDTH * 2
        F_x3 = PANEL_1_BUTTON_WIDTH * 3

        panel_1 = UIPanel(
            relative_rect=pygame.Rect(0, 0, 300, 30), object_id="@panel_odd"
        )
        file_dropdown_panel = UIPanel(
            relative_rect=Rect(F_x0, PANEL_1_HEIGHT, SUB_PANEL_WIDTH, SUB_PANEL_HEIGHT),
            object_id="@button_base",
            manager=manager,
            visible=False,
        )
        # file_dropdown_panel.change_layer(100)
        file_toolbar_button = UIButton(
            relative_rect=Rect(0, 0, 50, PANEL_1_HEIGHT),
            text="File",
            object_id="@button_base",
            manager=manager,
            container=panel_1,
        )

        file_load_button = UIButton(
            relative_rect=Rect(
                F_x0,
                SUB_PANEL_BUTTON_HEIGHT * 0,
                SUB_PANEL_WIDTH,
                SUB_PANEL_BUTTON_HEIGHT,
            ),
            text="Load",
            object_id="@button_base",
            container=file_dropdown_panel,
            manager=manager,
        )
        file_load_button.change_layer(100)
        file_load_mp3_button = UIButton(
            relative_rect=Rect(
                F_x0,
                SUB_PANEL_BUTTON_HEIGHT * 1,
                SUB_PANEL_WIDTH,
                SUB_PANEL_BUTTON_HEIGHT,
            ),
            text="Load MP3",
            object_id="@button_base",
            container=file_dropdown_panel,
            manager=manager,
        )
        file_load_mp3_button.change_layer(100)
        file_save_button = UIButton(
            relative_rect=Rect(
                F_x0,
                SUB_PANEL_BUTTON_HEIGHT * 2,
                SUB_PANEL_WIDTH,
                SUB_PANEL_BUTTON_HEIGHT,
            ),
            text="Save",
            object_id="@button_base",
            container=file_dropdown_panel,
            manager=manager,
        )
        file_save_button.change_layer(100)
        file_save_as_button = UIButton(
            relative_rect=Rect(
                F_x0,
                SUB_PANEL_BUTTON_HEIGHT * 3,
                SUB_PANEL_WIDTH,
                SUB_PANEL_BUTTON_HEIGHT,
            ),
            text="Save as",
            object_id="@button_base",
            container=file_dropdown_panel,
            manager=manager,
        )
        file_save_as_button.change_layer(100)

        playspeed_button = UIButton(
            relative_rect=Rect(F_x1, 0, 50, 30),
            text="1.0x",
            object_id="@button_base",
            manager=manager,
            container=panel_1,
        )
        playspeed_button.change_layer(100)

        play_button = UIButton(
            relative_rect=Rect(F_x2, 0, 50, 30),
            text="Play",
            object_id="@button_base",
            manager=manager,
            container=panel_1,
        )
        play_button.change_layer(100)

        play_time_text = UILabel(
            relative_rect=Rect(F_x3, 0, 150, 30),
            text="00:00:000",
            object_id="@textbox_time",
            manager=manager,
            container=panel_1,
        )

        # Block Information
        panel_2 = UIPanel(
            relative_rect=Rect(0, PANEL_1_HEIGHT, OPTION_WIDTH, PANEL_2_HEIGHT),
            object_id="@panel_even",
            manager=manager,
        )

        BLOCK_INFO_GAP = 10
        BI_x0 = BLOCK_INFO_GAP
        BI_w0 = 60
        BI_x1 = BI_x0 + BI_w0 + BLOCK_INFO_GAP // 2
        BI_w1 = 80
        BI_x2 = BI_x1 + BI_w1 + BLOCK_INFO_GAP // 2
        BI_w2 = 60
        BI_x3 = BI_x2 + BI_w2 + BLOCK_INFO_GAP // 2
        BI_w3 = 40 + BLOCK_INFO_GAP

        BI_h = 25
        BI_y0 = BLOCK_INFO_GAP + 30
        BI_y1 = BI_y0 + BI_h + BLOCK_INFO_GAP
        BI_y2 = BI_y1 + BI_h + BLOCK_INFO_GAP
        BI_y3 = BI_y2 + BI_h + BLOCK_INFO_GAP

        # Text
        block_main_text = UILabel(
            relative_rect=Rect(0, 0, 300, 40),
            text="Block Information",
            object_id="@header_even",
            manager=manager,
            container=panel_2,
        )

        # block_main_text.disable()
        block_bpm_text = UILabel(
            relative_rect=Rect(BI_x0, BI_y0, BI_w0, BI_h),
            text="BPM",
            object_id="@label_base",
            manager=manager,
            container=panel_2,
        )
        block_bm_text = UILabel(
            relative_rect=Rect(BI_x0, BI_y1, BI_w0, BI_h),
            text="B/M",
            object_id="@label_base",
            manager=manager,
            container=panel_2,
        )
        block_sb_text = UILabel(
            relative_rect=Rect(BI_x0, BI_y2, BI_w0, BI_h),
            text="S/B",
            object_id="@label_base",
            manager=manager,
            container=panel_2,
        )
        block_delay_text = UILabel(
            relative_rect=Rect(BI_x0, BI_y3, BI_w0, BI_h),
            text="Delay",
            object_id="@label_base",
            manager=manager,
            container=panel_2,
        )
        block_measures_text = UILabel(
            relative_rect=Rect(BI_x2, BI_y0, BI_w0, BI_h),
            text="Measures",
            object_id="@label_measures",
            manager=manager,
            container=panel_2,
        )
        block_beats_text = UILabel(
            relative_rect=Rect(BI_x2, BI_y1, BI_w0, BI_h),
            text="Beats",
            object_id="@label_base",
            manager=manager,
            container=panel_2,
        )
        block_splits_text = UILabel(
            relative_rect=Rect(BI_x2, BI_y2, BI_w0, BI_h),
            text="Splits",
            object_id="@label_base",
            manager=manager,
            container=panel_2,
        )

        # Block Information TextEntryLine
        block_bpm_line = UITextEntryLine(
            relative_rect=Rect(BI_x1, BI_y0, BI_w1, BI_h),
            object_id="@textentryline_base",
            manager=manager,
            container=panel_2,
        )
        block_bm_line = UITextEntryLine(
            relative_rect=Rect(BI_x1, BI_y1, BI_w1, BI_h),
            object_id="@textentryline_base",
            manager=manager,
            container=panel_2,
        )
        block_sb_line = UITextEntryLine(
            relative_rect=Rect(BI_x1, BI_y2, BI_w1, BI_h),
            object_id="@textentryline_base",
            manager=manager,
            container=panel_2,
        )
        block_delay_line = UITextEntryLine(
            relative_rect=Rect(BI_x1, BI_y3, BI_w1, BI_h),
            object_id="@textentryline_base",
            manager=manager,
            container=panel_2,
        )
        block_measures_line = UITextEntryLine(
            relative_rect=Rect(BI_x3, BI_y0, BI_w3, BI_h),
            object_id="@textentryline_base",
            manager=manager,
            container=panel_2,
        )
        block_beats_line = UITextEntryLine(
            relative_rect=Rect(BI_x3, BI_y1, BI_w3, BI_h),
            object_id="@textentryline_base",
            manager=manager,
            container=panel_2,
        )
        block_splits_line = UITextEntryLine(
            relative_rect=Rect(BI_x3, BI_y2, BI_w3, BI_h),
            object_id="@textentryline_base",
            manager=manager,
            container=panel_2,
        )

        block_delay_unit_button = UIButton(
            relative_rect=Rect(BI_x2, BI_y3, 40, BI_h),
            text="ms",
            object_id="@delay_unit_button",
            manager=manager,
            container=panel_2,
        )

        block_apply_button = UIButton(
            relative_rect=Rect(BI_x3, BI_y3, BI_w3, BI_h),
            text="Apply",
            object_id="@delay_unit_button",
            manager=manager,
            container=panel_2,
        )

        # Block Operation
        panel_3 = UIPanel(
            relative_rect=Rect(
                0, PANEL_1_HEIGHT + PANEL_2_HEIGHT, OPTION_WIDTH, PANEL_3_HEIGHT
            ),
            object_id="@panel_odd",
            manager=manager,
        )

        block_operation_header_text = UITextBox(
            relative_rect=Rect(0, 0, OPTION_WIDTH, 40),
            html_text="Block Operation",
            object_id="@header_odd",
            manager=manager,
            container=panel_3,
        )

        BLOCK_OPER_BUTTON_WIDTH = 75
        BLOCK_OPER_BUTTON_HEIGHT = 30
        BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT = (
            BLOCK_OPER_BUTTON_WIDTH,
            BLOCK_OPER_BUTTON_HEIGHT,
        )

        BO_x0 = 0
        BO_x1 = BO_x0 + BLOCK_OPER_BUTTON_WIDTH
        BO_x2 = BO_x1 + BLOCK_OPER_BUTTON_WIDTH
        BO_x3 = BO_x2 + BLOCK_OPER_BUTTON_WIDTH
        BO_y0 = 40

        block_add_above_button = UIButton(
            relative_rect=Rect(
                BO_x0, BO_y0, BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT
            ),
            text="Add ^",
            object_id="@button_base",
            container=panel_3,
        )
        block_add_below_button = UIButton(
            relative_rect=Rect(
                BO_x1, BO_y0, BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT
            ),
            text="Add v",
            object_id="@button_base",
            container=panel_3,
        )
        block_split_button = UIButton(
            relative_rect=Rect(
                BO_x2, BO_y0, BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT
            ),
            text="Split",
            object_id="@button_base",
            container=panel_3,
        )
        block_delete_button = UIButton(
            relative_rect=Rect(
                BO_x3, BO_y0, BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT
            ),
            text="Delete",
            object_id="@button_base",
            container=panel_3,
        )

        # Mode
        panel_4 = UIPanel(
            relative_rect=Rect(
                0,
                PANEL_1_HEIGHT + PANEL_2_HEIGHT + PANEL_3_HEIGHT,
                OPTION_WIDTH,
                PANEL_4_HEIGHT,
            ),
            object_id="@panel_even",
            manager=manager,
        )

        mode_header_text = UITextBox(
            relative_rect=Rect(0, 0, OPTION_WIDTH, 40),
            html_text="Mode",
            object_id="@header_even",
            manager=manager,
            container=panel_4,
        )

        MODE_LINE_HEIGHT = 30
        MODE_GAP = 10
        MO_x0 = MODE_GAP
        MO_w0 = 240
        MO_x1 = BI_x0 + MO_w0
        MO_w1 = 40

        MO_y0 = 40
        MO_y1 = MO_y0 + MODE_LINE_HEIGHT
        MO_y2 = MO_y1 + MODE_LINE_HEIGHT
        MO_y3 = MO_y2 + MODE_LINE_HEIGHT

        mode_1_text = UITextBox(
            relative_rect=Rect(MO_x0, MO_y0, MO_w0, MODE_LINE_HEIGHT),
            html_text="Auto line pass",
            object_id="@textbox_base",
            manager=manager,
            container=panel_4,
        )

        mode_1_button = UIButton(
            relative_rect=Rect(MO_x1, MO_y0, MO_w1, MODE_LINE_HEIGHT),
            text="F1",
            object_id="@button_onoff",
            manager=manager,
            container=panel_4,
        )

        panel_5 = UIPanel(
            relative_rect=Rect(
                0,
                PANEL_1_HEIGHT + PANEL_2_HEIGHT + PANEL_3_HEIGHT + PANEL_4_HEIGHT,
                OPTION_WIDTH,
                PANEL_5_HEIGHT,
            ),
            object_id="@panel_odd",
            manager=manager,
        )

        logger_header = UITextBox(
            relative_rect=Rect(0, 0, OPTION_WIDTH, 40),
            html_text="Log",
            object_id="@header_odd",
            manager=manager,
            container=panel_5,
        )

        logger_textbox = UITextBox(
            relative_rect=Rect(0, 40, OPTION_WIDTH, 220),
            html_text="[{}] Welcome to UCS Editor".format(time.strftime("%H:%M:%S")),
            object_id="@textbox_log",
            manager=manager,
            container=panel_5,
        )

        logger_clear_button = UIButton(
            relative_rect=Rect(125, 270, 50, 30),
            text="Clear",
            object_id="@button_base",
            manager=manager,
            container=panel_5,
        )

        SCROLLBAR_BUTTON_WIDTH = 20
        SCROLLBAR_BUTTON_HEIGHT = 30
        scrollbar_up_button = UIButton(
            relative_rect=Rect(0, 0, SCROLLBAR_BUTTON_WIDTH, SCROLLBAR_BUTTON_HEIGHT),
            text="^",
            object_id="@button_base",
            manager=manager,
        )
        scrollbar_down_button = UIButton(
            relative_rect=Rect(0, 0, SCROLLBAR_BUTTON_WIDTH, SCROLLBAR_BUTTON_HEIGHT),
            text="v",
            object_id="@button_base",
            manager=manager,
        )

        self.manager = manager
        self.panel_5 = panel_5
        self.ui_elements: List[ElementBase] = [
            # Panel 1 : File & Play Area
            FileButton(file_toolbar_button),
            LoadButton(file_load_button),
            LoadMP3Button(file_load_mp3_button),
            SaveButton(file_save_button),
            SaveAsButton(file_save_as_button),
            PlaySpeedButton(playspeed_button),
            PlayButton(play_button),
            PlayTimeTextbox(play_time_text),
            # Panel 2 : Block Information Area
            BPMTexbox(block_bpm_line),
            BeatPerMeasureTextbox(block_bm_line),
            SplitPerBeatTextbox(block_sb_line),
            DelayTexbox(block_delay_line),
            DelayUnitButton(block_delay_unit_button),
            MeasuresTexbox(block_measures_line),
            BeatsTexbox(block_beats_line),
            SplitsTexbox(block_splits_line),
            ApplyButton(block_apply_button),
            # Panel 3 : Block Operation Area
            BlockAddAboveButton(block_add_above_button),
            BlockAddBelowButton(block_add_below_button),
            BlockSplitButton(block_split_button),
            BlockDeleteButton(block_delete_button),
            # Panel 4 : Mode Area
            AutoLinePassButton(mode_1_button),
            # Panel 5 : Logger Area
            LogTextbox(logger_textbox),
            LogClearButton(logger_clear_button),
            # Panel 6 : Scrollbar Area
            ScrollUpButton(scrollbar_up_button),
            ScrollDownButton(scrollbar_down_button),
        ]
