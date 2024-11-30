README in Korean : [![kr](https://img.shields.io/badge/lang-kr-red.svg)](https://github.com/HyunjunGil/PIU-StepMaker/blob/main/README.md)

# PIU StepMaker-KeyboardEdition

# 1. Introduction
The basic functionality of StepEditLite has been implemented, allowing users to perform tasks using only the keyboard.

This project is developed using Python's pygame package. In the future, it will be re-implemented using the Electron framework to make it accessible on the web.

To be honest, I haven't created many UCS files myself, so I’m not entirely familiar with the specific inconveniences users might face. Even if you don’t use this tool, I’d greatly appreciate it if you could share any challenges or inconveniences you’ve experienced while creating UCS files. You can reach me via email at rlfahs3025@gmail.com, and I’ll do my best to incorporate your feedback in future updates. Additionally, if you encounter any bugs or issues while using this tool, please don’t hesitate to let me know.


## 2. Installation and Usage Instructions

### 2.1. Download exe file
To use the program, go to the [release page](https://github.com/HyunjunGil/PIU-StepMaker/releases/tag/1.0.0), download StepEditKeyboard.zip, extract it, and run the executable file inside. When running the executable, Windows may display a warning about an unknown publisher. You can safely ignore this and proceed. This issue occurs because I haven’t purchased and included a digital certificate. I’ve decided to leave it as is for now.

### 2.2. Running the Code Directly
It is recommended to use Python 3.12.

After cloning the repository locally, install the required packages using the following command:

    pip install -r requirements.txt

You can also run the program directly from the repository using the command:

    python main.py

If you prefer to create and run an executable file, you can do so with the following command:

    pyinstaller StepEditKeyboard.spec

Afterward, navigate to the dist folder and run the generated StepEditKeyboard.exe file.

## 3.Explanation of Screen Components

The screen is structured as shown below, and the names of each component are as follows.

![layout_desc_en](https://github.com/user-attachments/assets/4986b983-687e-4f23-bea9-eeed7402a0e9)

- **Control Area**: The leftmost area containing various buttons.
- **Chart Area**: The central area where the chart is displayed.
- **Selection Area**: The area highlighted with a hollow black rectangle.
- **Measure Area**: The area located immediately to the right of the chart area.
- **Scrollbar Area**: The area to the right of the measure area where the scrollbar is displayed.

## 4. Key Guide

### 4.1 Basic Keys
| **Key/Button** | **Function**|
|-------------|--------------------|
|Arrow Keys|Move the selection area up, down, left, or right. <br>- Hold **Ctrl** while moving vertically to move by measure units.<br>- Hold **Shift** to expand the selected area based on the initial position.<br>- Hold **Alt** to fine-tune notes. More details are provided below.|
| z/q/s/e/c/v/r/g/y/n (Step Keys)|Each key corresponds to one of the 10 lines in the chart. You can draw or erase notes on the respective lines of the selection area. Detailed behavior is explained below.|
|← (Backspace)|Deletes all notes within the selected area. **Even if only part of a long note is within the selected area, it will be deleted.**|
|Tab|If a button is focused, moves the focus to the next button.|
|Esc|Removes focus from the currently focused button.|
|Enter|Activates the effect of clicking the currently focused button.|
|F1|Toggles Auto Line Pass mode.|
|F5|Plays or pauses the music.|

### 4.2 Ctrl Shortcuts
#### 4.2.1 Chart Area Manipulation/Editing
| **Key/Button** | **Function**|
|-------------|--------------------|
|Ctrl + C|(Copy) Copies the selected chart area to the clipboard.|
|Ctrl + Z|(Cut) Copies the selected chart area to the clipboard and deletes it.|
|Ctrl + V|(Paste) **Deletes all notes in the selected area** and pastes the clipboard chart from the start line of the selected area.|
|Ctrl + Z|Undoes the last action. Actions that can be undone include:<br>- z/q/s/e/c/v/r/g/y/n and backspace<br>- Copy, cut, paste<br>- Block addition/splitting/deletion|
|Ctrl + Shift + Z|edoes the last undone action.|
|Ctrl + S|(Save) Saves the current work. If no save path is specified, it will prompt to set a save location before saving.|
|Ctrl + Shift + S|(Save As) Saves the current work after setting a new save path.|
|Ctrl + L|(Load) Loads a new UCS file. If an MP3 file with the same name exists, it will also be loaded as the audio.|
|Ctrl + Shift + L|(Load MP3) Loads a new MP3 audio file.|
|Ctrl + A|Expands the selected area to the entire current block. Pressing it again will expand it to the entire chart area.|
|Ctrl + F|Scans the entire chart area for errors, moving the selection area to the line with the error. If no errors are found, nothing will change.|


#### 4.2.2 Block Manipulation/Editing
| **Key/Button** | **Function**|
|-------------|--------------------|
|Ctrl + U|(Add ^) Adds a block of 1 measure in size above the currently selected block. The newly added block will have the same information as the current block.|
|Ctrl + I|(Add ^) Adds a block of 1 measure in size below the currently selected block. The newly added block will have the same information as the current block.|
|Ctrl + O|(Split) Splits the currently selected block at the specified line. If the current line is the first line of the block, no action will be taken.|
|Ctrl + P|(Delete) Deletes the currently selected block. If there is only one block left, no action will be taken.|


#### 4.2.3 Chart Area Zoom In/Out
| **Key/Button** | **Function**|
|-------------|--------------------|
|Ctrl + ,|Decreases the size of the step chart by one level.|
|Ctrl + .|Increases the size of the step chart by one level.|
|Ctrl + -|Decreases the height of the step chart by one level.|
|Ctrl + +|Increases the height of the step chart by one level.|


#### 4.2.4 Button Focus Shortcuts
| **Key/Button** | **Function**|
|-------------|--------------------|
|Ctrl + 1|Moves focus to the "File" button.|
|Ctrl + 2|Moves focus to the text box for entering BPM.|
|Ctrl + 3|Moves focus to the "Add ^" button.|
|Ctrl + 4|Moves focus to the "F1" button.|
|Ctrl + 5|Moves focus to the "Clear" button.|

## 5. Modes
### 5.1 Auto Line Pass
After completing key input for one line, the selected area automatically moves to the next line.

- The selected area is fixed to the entire width and 1 row in height.
- The selection will only move to the next line once all step keys are pressed and released.
- Long notes cannot be entered in this mode.


## 6. Explanation of Actions
### 6.1 File Loading/Saving Description
- Clicking the File button in the top left will activate previously hidden buttons.
- The Load button allows you to load both a UCS file and an MP3 file simultaneously. - The MP3 file must have the same name as the UCS file to be loaded. You can also use the Ctrl + L shortcut to load files.
- The Load MP3 button allows you to load only an MP3 file. You can also use the Ctrl + Shift + L shortcut to load a file.
- The Save button allows you to save your chart. If no save path is specified, you will be prompted to choose one before saving. You can also use the Ctrl + S shortcut to save.
- The Save As button allows you to change the save location. You can also use the Ctrl + Shift + S shortcut to change the save location.
<br> ![file_decs](https://github.com/user-attachments/assets/167835c1-b165-483f-acf3-e1efad2c85bd)

### 6.2 Step Key Behavior Description
- When a step key is pressed, a note is created between the first and last lines of the selected area. If the selected area is a single vertical line, a single note is created; if it spans multiple lines, a long note is created.
- If there is already a single note or long note at the location where a note is being created, the existing long note will be deleted.
- When the Alt key is held, and the selected area is 1x1 size, and there is already a note at that position, you can adjust the note's position. You can use Ctrl to move the note in measure units.
    1. If it's a single note, the position is adjusted.
    2. If it's the head or tail of a long note, the length of the long note is adjusted. When adjusting, the note cannot overlap with other notes.
    3. If it's the body of a long note, the position of the long note is adjusted. When adjusting, the note cannot overlap with other notes.
- When the music is playing and a step key is pressed, a note can be created in the chart recognition area. You can create only short note in default. Long notes can be disabled by modifying constants.py.
![stepkey_desc](https://github.com/user-attachments/assets/ac4c4192-9079-4c52-9606-5098c58d8ff7)

### 6.3 Mouse Interaction Description
- Click the File button to show or hide hidden options like Load, Save, etc.
Drag the edges of the mouse to resize the window. The window cannot be reduced below a certain size.
- Click on each button to use its respective function.
Drag the scrollbar to adjust the chart position.
Drag the chart recognition area to adjust its position.
- Click and drag the chart area to adjust the selected area.
- Click on a measure area to align the selected area with that measure.
![mouse_desc](https://github.com/user-attachments/assets/52b94c24-5bc0-49e6-94ba-bd23d1adc05d)

### 6.4 Convenient Function Key Description
- Press Ctrl + F to find the line with errors. If no errors are found, a message indicating that there are no errors will be displayed in the log.
- Press Ctrl + A to expand the selected area to the entire block or the entire chart area.
![util_etc](https://github.com/user-attachments/assets/00ba5a38-f2d7-4de5-bd5c-5d778bdb3968)

## 7. constants.py
You can modify the values in constants.py to adjust the environment to better suit your needs. The following values can be modified:

| **Contant** | **(Default Value) Function**           |
|-------------|--------------------|
|HARD_MAX_LINES|(2,000) The maximum number of lines the chart can have. Setting this value too high may slow down performance.|
|HARD_MAX_Y|(100,000) The maximum Y value of the scroll area. Setting this value too high may slow down performance.|
|KEY_REPEAT_DELAY_MS|(500) The delay time for the first repeat input when a key is pressed. The larger the number, the longer the delay.|
|KEY_REPEAT_RATE_MS|(50) The time interval between continuous inputs after the first repeat input. The smaller the number, the faster it repeats.|
|MUSIC_SPEED_MAP|([0.2, 0.3, 0.4, 0.5, 0.6, 1]) The list of possible music playback speeds. The value 1 must always be included.|
|VERTICAL_MULTIPLIER_MAX|(50) The maximum value to which the chart area can be scaled vertically. A value of 10 corresponds to a 1.0 scale.|
|MIN_SPLIT_SIZE|The minimum space maintained between lines even as the Split/Beat value increases.|
|MUSIC_INPUT_DELAY_IN_PIXEL|(10) The correction value for the chart input position when music is playing. Adjust it if the input seems too early or late.|
|ALLOW_LONG_NOTE|(False) Whether long notes are allowed during music playback when inputting the chart. It is recommended to keep this as False unless necessary, as unintended long notes may be created in the current version.
|

## 8. Feedback and Feature Suggestions
As this is still an early version, there may be bugs or inconveniences. If you encounter any issues, please send them to rlfahs3025@gmail.com or leave them as issues in the repository, and I will work on resolving them as soon as possible.

Additionally, for future versions, I plan to add more features. Some of the ideas I'm considering are listed below, but if you have any suggestions for improvements or new features, please feel free to send them via email.

- Section BPM Adjustment: After selecting an area and a BPM range, automatically adjust the BPM to smoothly increase or decrease over time.
- Add Head to Long Notes: Right-click on a long note to add a head to the long note.
- Various Gimmicks: Add multiple gimmicks similar to those found in StepMania.
- Play Mode: Allow users to play the chart they created directly.