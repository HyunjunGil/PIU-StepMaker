from PyQt5 import QtWidgets, QtGui, QtCore
import sys


class GridWidget(QtWidgets.QGraphicsView):
    def __init__(self, rows, cols, cell_size=50):
        super().__init__()

        # 그래픽 장면(Scene) 설정
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        # 격자판 크기 설정
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        # 마우스 이벤트 상태를 저장할 변수들
        self.hovered_item = None
        self.selected_item = None

        # 격자 그리기
        self.draw_grid()

        # 뷰 크기와 스크롤 설정
        self.setFixedSize(self.cols * self.cell_size + 20, 500)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # 스크롤 가능한 영역 설정
        self.setSceneRect(0, 0, self.cols * self.cell_size, self.rows * self.cell_size)

    def draw_grid(self):
        pen = QtGui.QPen(QtGui.QColor("lightgray"))

        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size
                y = row * self.cell_size

                # 1열과 2열의 8행 단위 병합
                if col in [0, 1] and row % 8 == 0:
                    rect = QtCore.QRectF(x, y, self.cell_size * 2, self.cell_size * 8)
                    self.scene.addRect(rect, pen, QtGui.QBrush(QtGui.QColor("white")))
                elif col > 1 or row % 8 != 0:
                    # 나머지 열
                    rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size)
                    item = self.scene.addRect(
                        rect, pen, QtGui.QBrush(QtGui.QColor("white"))
                    )
                    item.setData(0, (row, col))

    # 마우스가 격자 위에 올라갈 때 발생하는 이벤트
    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, QtGui.QTransform())

        if item and item.data(0)[1] >= 2:
            if self.hovered_item and self.hovered_item != item:
                self.hovered_item.setBrush(QtGui.QBrush(QtGui.QColor("white")))

            item.setBrush(QtGui.QBrush(QtGui.QColor("lightgray")))
            self.hovered_item = item
        elif self.hovered_item:
            self.hovered_item.setBrush(QtGui.QBrush(QtGui.QColor("white")))
            self.hovered_item = None

        super().mouseMoveEvent(event)

    # 격자를 클릭할 때 발생하는 이벤트
    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, QtGui.QTransform())

        if item and item.data(0)[1] >= 2:
            if self.selected_item:
                self.selected_item.setPen(QtGui.QPen(QtGui.QColor("lightgray")))

            item.setPen(QtGui.QPen(QtGui.QColor("black"), 2))
            self.selected_item = item

        super().mousePressEvent(event)

    # 키보드 이벤트 처리
    def keyPressEvent(self, event):
        if self.selected_item:
            row, col = self.selected_item.data(0)

            if event.key() == QtCore.Qt.Key_Escape:
                # 선택된 격자가 있을 때 ESC 키를 눌렀을 경우 선택 해제
                self.selected_item.setPen(QtGui.QPen(QtGui.QColor("lightgray")))
                self.selected_item = None

            elif event.key() == QtCore.Qt.Key_Left and col > 2:
                # 왼쪽으로 이동
                self.move_selected_item(row, col - 1)
            elif event.key() == QtCore.Qt.Key_Right and col < self.cols - 1:
                # 오른쪽으로 이동
                self.move_selected_item(row, col + 1)
            elif event.key() == QtCore.Qt.Key_Up and row > 0:
                # 위로 이동
                self.move_selected_item(row - 1, col)
            elif event.key() == QtCore.Qt.Key_Down and row < self.rows - 1:
                # 아래로 이동
                self.move_selected_item(row + 1, col)

        super().keyPressEvent(event)

    def move_selected_item(self, row, col):
        # 선택된 격자를 새 위치로 이동
        if self.selected_item:
            self.selected_item.setPen(QtGui.QPen(QtGui.QColor("lightgray")))

        # 새로운 위치에 선택된 격자의 위치를 업데이트
        item = self.scene.itemAt(
            QtCore.QRectF(
                col * self.cell_size,
                row * self.cell_size,
                self.cell_size,
                self.cell_size,
            ),
            QtGui.QTransform(),
        )
        if item:
            item.setPen(QtGui.QPen(QtGui.QColor("black"), 2))
            self.selected_item = item


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Grid with Scrollbar")

        # 메인 위젯과 레이아웃 설정
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # 격자판 위젯 추가
        self.grid_widget = GridWidget(rows=50, cols=7)
        layout.addWidget(self.grid_widget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
