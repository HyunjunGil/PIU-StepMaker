import pygame, pygame_gui, time, datetime
from pygame import Rect
from pygame_gui.elements import UIButton, UITextEntryLine, UIPanel, UITextBox, UILabel


pygame.init()
screen = pygame.display.set_mode((800, 700))
manager = pygame_gui.UIManager((800, 700), "theme.json")


OPTION_WIDTH = 300

PANEL_1_HEIGHT = 30
PANEL_2_HEIGHT = 200
PANEL_3_HEIGHT = 80
PANEL_4_HEIGHT = 140
PANEL_5_HEIGHT = 200
SUB_PANEL_WIDTH = 80
SUB_PANEL_HEIGHT = 120
SUB_PANEL_BUTTON_HEIGHT = SUB_PANEL_HEIGHT // 4

PANEL_1_BUTTON_WIDTH = 50
F_x0 = PANEL_1_BUTTON_WIDTH * 0
F_x1 = PANEL_1_BUTTON_WIDTH * 1
F_x2 = PANEL_1_BUTTON_WIDTH * 2
F_x3 = PANEL_1_BUTTON_WIDTH * 3

panel_1 = UIPanel(relative_rect=pygame.Rect(0, 0, 300, 30), object_id="@panel_odd")
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
        F_x0, SUB_PANEL_BUTTON_HEIGHT * 0, SUB_PANEL_WIDTH, SUB_PANEL_BUTTON_HEIGHT
    ),
    text="Load",
    object_id="@button_base",
    container=file_dropdown_panel,
    manager=manager,
)
file_load_button.change_layer(100)
file_load_mp3_button = UIButton(
    relative_rect=Rect(
        F_x0, SUB_PANEL_BUTTON_HEIGHT * 1, SUB_PANEL_WIDTH, SUB_PANEL_BUTTON_HEIGHT
    ),
    text="Load MP3",
    object_id="@button_base",
    container=file_dropdown_panel,
    manager=manager,
)
file_load_mp3_button.change_layer(100)
file_save_button = UIButton(
    relative_rect=Rect(
        F_x0, SUB_PANEL_BUTTON_HEIGHT * 2, SUB_PANEL_WIDTH, SUB_PANEL_BUTTON_HEIGHT
    ),
    text="Save",
    object_id="@button_base",
    container=file_dropdown_panel,
    manager=manager,
)
file_save_button.change_layer(100)
file_save_as_button = UIButton(
    relative_rect=Rect(
        F_x0, SUB_PANEL_BUTTON_HEIGHT * 3, SUB_PANEL_WIDTH, SUB_PANEL_BUTTON_HEIGHT
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
    text="beats",
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
    relative_rect=Rect(BO_x0, BO_y0, BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT),
    text="Add ^",
    object_id="@button_base",
    container=panel_3,
)
block_add_below_button = UIButton(
    relative_rect=Rect(BO_x1, BO_y0, BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT),
    text="Add v",
    object_id="@button_base",
    container=panel_3,
)
block_split_button = UIButton(
    relative_rect=Rect(BO_x2, BO_y0, BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT),
    text="Split",
    object_id="@button_base",
    container=panel_3,
)
block_delete_button = UIButton(
    relative_rect=Rect(BO_x3, BO_y0, BLOCK_OPER_BUTTON_WIDTH, BLOCK_OPER_BUTTON_HEIGHT),
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
mode_2_text = UITextBox(
    relative_rect=Rect(MO_x0, MO_y1, MO_w0, MODE_LINE_HEIGHT),
    html_text="Fix selected line to receptor",
    object_id="@textbox_base",
    manager=manager,
    container=panel_4,
)
mode_3_text = UITextBox(
    relative_rect=Rect(MO_x0, MO_y2, MO_w0, MODE_LINE_HEIGHT),
    html_text="Show Logs",
    object_id="@textbox_base",
    manager=manager,
    container=panel_4,
)

mode_1_button = UIButton(
    relative_rect=Rect(MO_x1, MO_y0, MO_w1, MODE_LINE_HEIGHT),
    text="ON",
    object_id="@button_base",
    manager=manager,
    container=panel_4,
)
mode_2_button = UIButton(
    relative_rect=Rect(MO_x1, MO_y1, MO_w1, MODE_LINE_HEIGHT),
    text="ON",
    object_id="@button_base",
    manager=manager,
    container=panel_4,
)
mode_3_button = UIButton(
    relative_rect=Rect(MO_x1, MO_y2, MO_w1, MODE_LINE_HEIGHT),
    text="ON",
    object_id="@button_base",
    manager=manager,
    container=panel_4,
)

offset = 400
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
    relative_rect=Rect(0, 40, OPTION_WIDTH, 110),
    html_text="[{}] Welcome to UCS Editor".format(time.strftime("%H:%M:%S")),
    object_id="@textbox_log",
    manager=manager,
    container=panel_5,
)

logger_clear_button = UIButton(
    relative_rect=Rect(125, 160, 50, 30),
    text="Clear",
    object_id="@button_base",
    manager=manager,
    container=panel_5,
)


FILE_PANEL_VISIBLE = False


log_changed = False


def add_log(s: str):
    t = time.strftime("%H:%M:%S")
    text = logger_textbox.html_text
    logger_textbox.set_text(text + "\n" + f"[{t}] {s}")


def clear_log():
    t = time.strftime("%H:%M:%S")
    logger_textbox.set_text(f"[{t}] Clear logs")


clock = pygame.time.Clock()
running = True
cnt = 0
while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # print()
        # if event.type >= 32866:
        #     print(str(event))
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == file_toolbar_button:
                if FILE_PANEL_VISIBLE:
                    file_dropdown_panel.hide()
                    # panel_1.set_dimensions((0, 0, ))
                else:
                    file_dropdown_panel.show()
                FILE_PANEL_VISIBLE = not FILE_PANEL_VISIBLE
                file_dropdown_panel.rebuild()
            elif event.ui_element == file_load_button:
                log_changed = True
                add_log("Load")
            elif event.ui_element == file_load_mp3_button:
                log_changed = True
                add_log("Load mp3")
            elif event.ui_element == file_save_button:
                log_changed = True
                add_log("Saved!")
            elif event.ui_element == file_save_as_button:
                log_changed = True
                add_log("Saved as")

            elif event.ui_element == block_add_above_button:
                log_changed = True
                add_log("BLOCK Add ABOVE")
            elif event.ui_element == block_add_below_button:
                log_changed = True
                add_log("BLOCK Add BELOW")
            elif event.ui_element == block_split_button:
                log_changed = True
                add_log("BLOCK SPLIT")
            elif event.ui_element == block_delete_button:
                log_changed = True
                add_log("BLOCK DELETE")
            elif event.ui_element == logger_clear_button:
                clear_log()

        manager.process_events(event)
    manager.update(time_delta)
    screen.fill((255, 255, 255))
    if logger_textbox.scroll_bar and log_changed:
        logger_textbox.scroll_bar.set_scroll_from_start_percentage(1.0)
        log_changed = False
        # print(logger_textbox.scroll_bar.target_scroll_position)

        # logger_textbox.scroll_bar.scroll_position = (
        #     logger_textbox.scroll_bar.scrollable_height
        # )
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
