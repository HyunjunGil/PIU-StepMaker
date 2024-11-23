import os

from typing import List, Tuple
from constants import *
from state import State
from utils import update_validity


def load_music_file(path: str, state: State):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No such file: {path}")
    pygame.mixer.music.load(path)
    state.music_len = int(pygame.mixer.Sound(path).get_length() * 1000)


def load_ucs_file(
    path: str,
    state: State,
) -> Tuple[int, str, List[List[int]], List[List[int | float]]]:

    block_info: List[List[int]] = []
    step_data: List[List[int]] = []

    format, mode, cols = -1, "", 0

    with open(path, "r") as f:
        file_lines = f.readlines()

        ln, tot_ln = 2, len(file_lines)

        try:
            assert file_lines[0].startswith(":Format=") and file_lines[1].startswith(
                ":Mode="
            ), "Invalid UCS Header"

            format = int(file_lines[0].strip().split("=")[1])
            mode = file_lines[1].strip().split("=")[1]

            assert format == 1 and mode in ["Single", "Double"]

            if mode == "Single":
                cols = 5
            else:
                cols = 10

        except Exception as e:
            print(e)
            raise Exception("Failed to parse UCS Header")

        bpm = round(float(file_lines[ln].strip().split("=")[1]), 4)
        delay = int(file_lines[ln + 1].strip().split("=")[1])
        beat = int(file_lines[ln + 2].strip().split("=")[1])
        split = int(file_lines[ln + 3].strip().split("=")[1])
        block_idx = 0
        lcnt = 0
        ln += 4

        while ln < tot_ln:
            if file_lines[ln].startswith(":"):

                assert lcnt > 0, "Zero Size Block Occured at line {}".format(ln)

                block_info.append(
                    [
                        bpm,
                        beat,
                        split,
                        delay,  # in ms
                        lcnt // (beat * split),  # number of measures
                        (lcnt % (beat * split)) // split,  # number of beats
                        lcnt % split,  # number of split
                    ]
                )

                assert (
                    file_lines[ln].startswith(":BPM=")
                    and file_lines[ln + 1].startswith(":Delay=")
                    and file_lines[ln + 2].startswith(":Beat=")
                    and file_lines[ln + 3].startswith(":Split=")
                ), "Invalid Block Header"

                bpm = round(float(file_lines[ln].strip().split("=")[1]), 4)
                delay = int(file_lines[ln + 1].strip().split("=")[1])
                beat = int(file_lines[ln + 2].strip().split("=")[1])
                split = int(file_lines[ln + 3].strip().split("=")[1])
                block_idx += 1
                lcnt = 0
                ln += 4
                # print(delay, beat, split)
            else:
                parsed_line = [
                    block_idx,  # block index
                    lcnt // (beat * split),  # measure index
                    (lcnt % (beat * split)) // split,  # beat index
                    lcnt % split,  # split index
                    1,  # validity index
                ] + [STEP_TO_CODE[c] for c in file_lines[ln].strip()]
                step_data.append(parsed_line)
                lcnt += 1
                ln += 1

    block_info.append(
        [
            bpm,
            beat,  # beat per measure
            split,  # split per beat
            delay,
            lcnt // (beat * split),  # number of measures
            (lcnt % (beat * split)) // split,  # number of beats
            lcnt % split,  # number of split
        ]
    )

    update_validity(step_data, 0, len(step_data))

    state.format = format
    state.mode = mode
    state.block_info = block_info
    state.step_data = step_data
    state.update_y_info()

    step_data, block_info = state.get_step_info()

    state.measure_x_start = state.step_x_start + state.get_step_size() * cols
    state.scrollbar_x_start = state.measure_x_start + MEASURE_DESCRIPTOR_WIDTH


def save_ucs_file(
    state: State,
):

    if state.ucs_save_path == "":
        print("Save path not initialized")
        return
    path, format, mode = state.ucs_save_path, state.format, state.mode
    step_data, block_info = state.get_step_info()
    rows, cols = len(step_data), len(step_data[0]) - STEP_DATA_OFFSET
    with open(path, "w") as f:
        f.write(":Format=1\n")
        f.write(":Mode=" + "Single\n" if mode == "Single" else "Double\n")

        block_idx = -1
        for ln in range(rows):
            row = step_data[ln]
            bi = row[STEP_DATA_BI_IDX]
            if block_idx != bi:
                block = block_info[bi]
                bpm = block[BLOCK_BPM_IDX]
                bpm = bpm if int(bpm) != bpm else int(bpm)
                f.writelines(
                    [
                        f":BPM={bpm}\n",
                        f":Delay={block[BLOCK_DL_IDX]}\n",
                        f":Beat={block[BLOCK_BM_IDX]}\n",
                        f":Split={block[BLOCK_SB_IDX]}\n",
                    ]
                )
                block_idx = bi

            f.write(
                "".join(
                    [
                        CODE_TO_STEP[c]
                        for c in row[STEP_DATA_OFFSET : STEP_DATA_OFFSET + cols]
                    ]
                )
                + "\n"
            )
