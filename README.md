README in English : [![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/HyunjunGil/PIU-StepMaker/blob/main/README.en.md)


# PIU StepMaker-KeyboardEdition

## 1. 소개
StepEditLite의 기본 기능 구현 및 키보드만을 사용한 작업이 가능하도록 구현하였습니다.

python의 pygame 패키지를 이용하여 구현하였습니다. 추후에 Electron 프레임워크를 이용하여 웹에서 사용할 수 있도록 구현할 예정입니다.

사실 저는 UCS를 많이 만들어보지 않아 구체적으로 어떤 불편함이 있었는지 잘 모릅니다. 사용하시지 않으시더라도 UCS를 만드시면서 불편하셨던 점들을 rlfahs3025@gmail.com으로 메일을 통해 알려주시면 이후에 반영해보도록 하겠습니다. 그 외에도 사용하시면서 버그나 불편한 점이 생기시면 바로 알려주시면 감사하겠습니다.


## 2. 설치 및 사용 방법

### 2.1. exe 파일 다운
[릴리스 페이지](https://github.com/HyunjunGil/PIU-StepMaker/releases/latest)에 들어가셔서 StepEditKeyboard.zip을 다운받고 압축을 푼 후 안에 있는 exe 파일을 사용하시면 됩니다. **exe 파일을 실행할 때 윈도우에서 알 수 없는 게시자라고 경고가 나와도 무시하고 실행하면 됩니다.** 제가 따로 인증서를 구입해서 포함시켜야 해결되는 문제라 일단 그대로 두었습니다.



### 2.2. 코드 직접 실행
python 3.12버전을 사용하실 것을 권장드립니다.

레포지토리를 로컬에 복사한 후 아래 커맨드로 필요한 패키지를 설치합니다

    pip install -r requirements.txt

레포지토리에서 python main.py 커맨드로도 실행이 가능합니다.    
<br>exe 파일로 만들어서 실행하고 싶으시면 아래 커맨드를 이용하여 exe 파일을 만들 수 있습니다.

    pyinstaller StepEditKeyboard.spec

이후 생성된 dist 폴더 안에 생성된 StepEditKeyboard.exe를 실행하면 됩니다.

### 2.3. 에러 발생 시 대응 방법
새로운 ucs 파일을 불러오거나, 창을 닫거나, 또는 갑작스럽게 에러가 발생하여 프로그램이 정지하더라도 직전까지의 진행상황이 cache.ucs파일에 저장됩니다. 위와 같은 상황이 발생하더라도 cache.ucs 파일을 사용하여 작업내용을 복구할 수 있습니다.

갑작스러운 에러로 프로그램이 정지한 경우 ucs 파일의 경로에 로그 파일도 함께 생성됩니다. 로그 파일과 함께 에러를 제보해주시면 프로그램을 개선하는데 큰 도움이 됩니다.

## 3. 화면 구성 요소 설명
화면은 아래와 같이 구성되어 있으며 각각의 명칭은 아래와 같습니다.


![layout_desc](https://github.com/user-attachments/assets/21686502-38d6-4fe0-b19c-b81794493078)


- **조작 영역** : 가장 좌측에 각종 버튼이 있는 영역 입니다.
- **차트 영역** : 화면 중앙에 차트가 그려지는 영역 입니다.
- **선택 영역** : 속이 빈 검은 색 사각형으로 표시되는 영역입니다.
- **마디 영역** : 차트 영역 바로 우측에 있는 영역 입니다.
- **스크롤바 영역** :마디 영역 우측에 스크롤바가 그려진 영역입니다.



## 4. 키 가이드

### 4.1 기본 키

| **키/버튼** | **기능**           |
|-------------|--------------------|
| 방향키      | 선택 영역을 상하좌우로 이동합니다.<br>- 상하로 이동할 때 Ctrl을을 누르고 이동할 시 마디 단위로 이동합니다. <br>- Shift를 누르고 이동할 경우 처음의 위치를 기준으로 선택된 영역을 넓힐 수 있습니다. <br>- Alt를 누르고 이동할 경우 노트를 미세조정할 수 있습니다. 자세한 내용은 아래에서 확인할 수 있습니다. |
| z/q/s/e/c/v/r/g/y/n (스텝키) | 차트에 있는 각 10개의 라인에 각각 대응되는 키 입니다. 선택 영역의 각 라인을 그리거나 없앨 수 있습니다. 자세한 동작은 아래에서 확인할 수 있습니다.|
|← (Backspace)|선택된 영역에 걸쳐있는 있는 모든 노트를 지웁니다. **롱노트의 일부라도 선택된 영역에 포함된다면 지워집니다.**|
|Tab| 초점이 맞춰진 버튼이 있다면 다음 버튼으로 초점을 옮깁니다.|
|Esc| 초점이 맞춰진 버튼이 있다면 해제합니다.|
|Enter|초점이 맞춰진 버튼튼이 있다면 그 버튼을 클릭하는 효과를 발동합니다.|
| F1 | Auto Line Pass<링크> 모드를 키거나 끕니다.|
| F5 | 음악을 재생하거나 정지합니다.|

### 4.2 Ctrl 단축키

#### 4.2.1 차트영역 조작/편집
| **키/버튼** | **기능**           |
|-------------|--------------------|
|Ctrl + C     |(Copy) 선택된 영역의 차트를 클립보드에 복사합니다. |
|Ctrl + X|(Cut) 선택된 영역의 차트를 클립보드에 복사하고 모두 지웁니다. |
|Ctrl + V|(Paste) **선택된 영역의 차트를 모두 지우고** 클립보드에 있는 차트를 선택된 영역의 시작 라인부터 붙여넣습니다. |
|Ctrl + Z|바로 이전에 했던 행동을 되돌립니다. 되돌릴 수 있는는 행동은 아래와 같습니다 <br> - z/q/s/e/c/v/r/g/y/n 및 backspace <br>- 복사, 잘라내기, 붙여넣기 <br>- 블록 추가/분할/삭제|
|Ctrl + Shift+ Z|바로 이전에 되돌렸던 행동을 되돌립니다|
|Ctrl + S| (Save) 지금까지의 작업을 저장합니다. 만약 지정된 저장 경로가 없다면 설정하도록 한 후 저장합니다.|
|Ctrl + Shift + S|(Save As) 저장 경로를 새롭게 정한 후 지금까지의 작업을 저장합니다.|
|Ctrl + L| (Load) 새로운 ucs파일을 불러옵니다. 만약 불러온 파일과 같은 이름을 가진 mp3파일이 있다면 함께 불러와서 음원으로 사용합니다.|
|Ctrl + Shift + L|(Load mp3) 새로운 mp3 음원파일을 불러옵니다.|
|Ctrl + A|선택된 영역을 현재 블록 전체로 확장합니다. 한 번 더 누르면 차트영역 전체로 확장됩니다.|
|Ctrl + F| 차트영역 전체체에서 오류를 검사하고 오류가 있는 줄을 찾아 해당 줄로 선택 영역을 이동합니다. 만약 없다면 아무 변화도 일어나지 않습니다.|

---
### 4.2.2 블록 조작/편집
| **키/버튼** | **기능**           |
|-------------|--------------------|
|Ctrl + U| (Add ^) 현재 선택된 블록의 위쪽에 마디 1개의 크기를 가진 블록을 추가합니다.<br> 추가된 블록의 정보는 현재 블록과 동일합니다.|
|Ctrl + I| (Add ^) 현재 선택된 블록의 아래쪽에에 마디 1개의 크기를 가진 블록을 추가합니다. <br> 추가된 블록의 정보는 현재 블록과 동일합니다.|
|Ctrl + O| (Split) 현재 선택된 블록을 해당 라인에서 분할합니다.<br> 만약 현재 라인이 현재 블록의 첫 번째 줄이라면 아무일도 일어나지 않습니다.|
|Ctrl + P| (Delete) 현재 선택된 블록을 삭제합니다. <br> 만약 현재 블록이 한 개밖에 남아있지 않다면 아무일도 일어나지 않습니다.|

---
### 4.2.3 차트영역 확대/축소

| **키/버튼** | **기능**           |
|-------------|--------------------|
|Ctrl + ,| 스텝 차트의 크기를 한 단계 감소시킵니다|
|Ctrl + .| 스텝 차트의 크기를 한 단계 증가시킵니다|
|Ctrl + -| 스텝 차트의 높이를 한 단계 감소시킵니다|
|Ctrl + +| 스텝 차트의 높이를 한 단계 증가시킵니다|

---
### 4.2.4 버튼 초점 단축키
| **키/버튼** | **기능**           |
|-------------|--------------------|
|Ctrl + 1| "File" 버튼으로 초점 이동|
|Ctrl + 2| BPM을 입력하는 텍스트박스로 초점 이동|
|Ctrl + 3| "Add ^" 버튼으로 초점 이동|
|Ctrl + 4| "F1" 버튼으로 초점 이동|
|Ctrl + 5| "Clear" 버튼으로 초점 이동|

## 5. 모드
### 5.1 Auto Line Pass
한 줄의 키 입력이 끝난 후에 자동으로 선택된 영역이 다음줄로 이동합니다.
- 선택된 영역은 가로 전체, 세로 1줄로 고정됩니다.
- 모든 스텝키 입력이 끝나야만(눌렸던 키가 올라가야만) 다음 줄로 넘어갑니다.
- 롱노트는 입력이 불가능합니다.



## 6. 동작 설명

### 6.1 파일 불러오기/저장 설명
- 좌측 상단에 File 버튼을 클릭할 시 숨겨져있던 버튼이 활성화 됩니다.
- Load버튼으로 ucs파일과 mp3 파일을 동시에 로드할 수 있습니다. 만약 mp3파일은 ucs파일의 이름과 같아야만 불러올 수 있습니다. Ctrl + L 단축키로도 파일을 불러올 수 있습니다.
- Load MP3 버튼으로 mp3 파일만 따로 불러올 수 있습니다. Ctrl + Shift + L 단축키로도 파일을 불러올 수 있습니다.
- Save 버튼으로 채보를 저장할 수 있습니다. 만약 지정된 저장 경로가 없다면 저장할 경로를 지정한 후 저장할 수 있습니다. Ctrl + S 단축키로도 저장할 수 있습니다.
- Save as 버튼으로 채보를 저장할 위치를 변경할 수 있습니다. Ctrl + Shift + S 단축키로도 저장할 위치를 변경할 수 있습니다. 
![file_decs](https://github.com/user-attachments/assets/167835c1-b165-483f-acf3-e1efad2c85bd)


### 6.2. 스텝키 동작 설명
- 스텝키를 누를 경우 선택된 영역의 첫 번째 줄과 마지막 번 째 줄 사이에 노트를 생성합니다. 만약 선택된 영역이 세로로 한 줄이라면 단노트를, 여러 줄이라면 롱노트를 생성합니다.
- 노트를 생성할 때 그 위치에 단노트 또는 롱노트가 있다면 해당 롱노트 전체를 지웁니다. 
- Alt를 눌렀을 때 **선택된 영역이 1x1 크기이고** 해당 위치에 위치가 있다면 노트의 위치를 조정합니다. Ctrl를 함께 사용하여 마디 단위로 움직일 수 있습니다.
    1. 단노트라면 위치를 조정합니다. 
    2. 롱노트의 머리, 꼬리 부분이라면 롱노트의 길이를 조정합니다. 조정할 때 다른 노트를 넘어갈 수는 없습니다.
    3. 롱노트의 몸통 부분이라면 롱노트의 위치를 조정합니다. 조정할 때 다른 노트를 넘어갈 수는 없습니다.
- 음악을 재생하면서 스텝키를 누르면 채보인식부분에서 노트를 생성할 수 있습니다. 기본적으로 단노트만 생성할 수 있으며 constants.py를 수정하여 롱노트는 활성화할 수 있습니다. 
![stepkey_desc](https://github.com/user-attachments/assets/ac4c4192-9079-4c52-9606-5098c58d8ff7)



### 6.3. 마우스 동작 설명
- File 버튼을 클릭하여 숨겨져있는 Load, Save 등의 옵션 박스를 보이게 하거나 숨길 수 있습니다.
- 마우스의 테두리를 드래그하여 화면의 크기를 조절할 수 있습니다. 일정 수준 이하로는 줄일 수 없습니다.
- 각각의 버튼을 클릭하여 버튼의 기능을 사용할 수 있습니다.
- 스크롤바를 드래그하여 채보 위치를 조절할 수 있습니다.
- 채보 인식부분을 드래그하여 위치를 조절할 수 있습니다.
- 채보 영역을 클릭후 드래그 하여 선택 영역을 조절할 수 있습니다.
- 마디 영역을 클릭하면 선택 영역을 해당 마디와 일치시킬 수 있습니다.
<br>![mouse_desc](https://github.com/user-attachments/assets/52b94c24-5bc0-49e6-94ba-bd23d1adc05d)

### 6.4. 편의 기능 키 설명
- Ctrl + F를 통해 에러가 있는 줄을 찾을 수 있습니다. 에러가 없으면 에러가 없다고 로그에 문구를 출력합니다.
- Ctrl + A를 통해 선택 영역을 해당 블록, 전체 영역으로 확장할 수 있습니다.
<br>![util_etc](https://github.com/user-attachments/assets/00ba5a38-f2d7-4de5-bd5c-5d778bdb3968)

## 7. constants.py
constants.py에 있는 값을 수정하여 본인에게 좀 더 맞는 환경을 세팅할 수 있습니다. 수정할 수 있는 값들은 아래와 같습니다.

| **상수** | **(기본 값) 기능**           |
|-------------|--------------------|
|HARD_MAX_LINES| (2,000) 채보가 가질 수 있는 최대 줄의 개수입니다. 너무 크게 설정하면 실행속도가 느려질 수 있습니다. |
|HARD_MAX_Y| (100,000) 스크롤 영역의 최대 y 값입니다. 너무 크게 설정하면 실행속도가 느려질 수 있습니다. |
|KEY_REPEAT_DELAY_MS| (500) 키를 누른 상태에서 첫 번째 반복 입력까지의 대기 시간을 의미합니다. 숫자가 클 수록 자동입력이 시작되기까지의 시간이 길어집니다.|
|KEY_REPEAT_RATE_MS| (50) 첫 번째 반복 입력 이후, 연속적인 입력 사이의 간격을 의미합니다. 숫자가 작을수록 더 빠른 속도로 입력이 이루어 집니다.|
|MUSIC_SPEED_MAP| ([0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]) 음악이 재생될 속도의 리스트를 지정합니다. **목록에 1은 무조건 포함되어 있어야 합니다.**|
|VERTICAL_MULTIPLIER_MAX| (50) 채보 영역을 세로 방향으로 확대할 수 있는 최대 값을 설정합니다. 10은 1.0배율을 의미합니다.|
|MIN_SPLIT_SIZE| Split/Beat 값이 커져도 줄과 줄 사이의 간격은 이 값보다 같거나 크게 유지가 됩니다.|
|MUSIC_INPUT_DELAY_IN_PIXEL| (10) 음악을 재생하면서 채보를 입력할 때 채보 입력 위치에 대한 보정 값입니다. 펌프에서 judgement와 비슷합니다. 원하는 라인보다 빨리 입력되는 것 같으면 이 값을 적당한 음수로 설정하고, 원하는 라인보다 늦게 입력되는 것 같으면 적당한 양수로 설정하면 됩니다.|
|ALLOW_LONG_NOTE| (False) 음악을 재생하면서 채보를 입력할 때 롱노트를 허용할 지에 대한 여부입니다. 현재 버전으로는 의도치 않은 롱노트가 입력되는 경우가 많기 때문에 특별한 경우를 제외하고는 False로 설정하는 것을 추천드립니다.|


## 8. 피드백 및 추가 기능 제안
아직 초기 버전이라 버그가 있을 수 있고 불편한 점이 있을 수 있습니다. 이러한 점들을 모두 rlfahs3025@gmail.com으로 보내주시거나 여기 리포지토리에 이슈로 남겨주시면 바로 해결할 수 있도록 하겠습니다.

추가로 이후에 새롭게 제작할 버전에서는 좀 더 많은 기능들을 추가할 계획입니다. 생각하고 있는 기능들은 아래와 같은데 더 좋은 기능이나 개선사항이 있다면 이또한 메일로 보내주시면 감사하겠습니다.

- 구간 변속 설정 : 영역을 선택 후 bpm 구간을 선택하면 자동으로 자연스럽게 bpm을 조정하여 bpm이 천천히 증가하거나 감소하는 효과를 쉽게 구현하기
- 롱노트 머리 추가 : 롱노트를 선택 후 우클릭하면 롱노트에 머리를 추가할 수 있도록 하기
- 각종 기믹 : stepmania에서 존재하는 여러 기믹도 추가할 수 있도록 하기
- 직접 플레이 : 만들어진 채보를 직접 플레이 할 수 있도록 하기
