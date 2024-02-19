import math
import sys
import socket
import threading
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPolygon, QIcon, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QMessageBox, \
    QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSlider, QGraphicsProxyWidget
from PyQt5.QtCore import Qt, QPoint

# 서버에 수신한 메세지 코드
START = "START"
SEND_CREATE = "2000"
BLACK_PLAYER = 1
WHITE_PLAYER = 2
# 명령어 코드
JOIN = "JOIN"
CLOSE = "CLOSE"
CLOSE_FIN = "CLOSE_FIN"
BEFORE_GAME = "BEFORE_GAME"


# SERVER_HOST = "192.168.10.68"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5557
BUFFER_SIZE = 1024


class HexagonGUI(QWidget):
    client_socket = None
    MY_COLOR = Qt.black
    OPPONENT = Qt.white
    my_place = []
    opp_place = []
    temp_circle = []
    step_point = []
    move_start = False
    move_end = False
    select_remove = False
    count = 0
    step_start = False
    step_end = False
    move_x = 0.0
    move_y = 0.0
    lbl_txt = ""

    uiEnableSgn = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("NineMensMorris")
        self.setGeometry(100, 100, 550, 550)  # 크기 설정

        # 레이아웃 생성
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # 라벨 생성
        self.label = QLabel("접속 버튼을 누르시오.")
        self.label.setFixedSize(400, 30)  # 가로 200, 세로 50
        self.label.setFrameShape(QLabel.Panel)
        # 글자 크기 설정
        font = QFont()
        font.setPointSize(10)  # 원하는 크기로 설정
        self.label.setFont(font)
        top_layout.addWidget(self.label)

        # 접속 버튼 생성
        self.connect_button = QPushButton("접속", self)
        self.connect_button.setFixedSize(100, 30)
        self.connect_button.clicked.connect(self.connect_to_server)
        top_layout.addWidget(self.connect_button)

        main_layout.addLayout(top_layout)

        # QGraphicsView 및 MyScene 인스턴스 생성
        self.view = MyGraphicsView()
        self.scene = MyScene()
        self.view.setScene(self.scene)

        # 레이아웃에 QGraphicsView 추가
        main_layout.addWidget(self.view)

        self.b_label = QLabel(f"남은 돌 개수 : {7 - self.count}", )
        self.b_label.setFixedSize(150, 30)  # 가로 200, 세로 50
        self.b_label.setFrameShape(QLabel.Panel)
        # 글자 크기 설정
        self.b_label.setFont(font)
        bottom_layout.addWidget(self.b_label)

        # 투명도 조절을 위한 슬라이더 추가
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setFocusPolicy(Qt.NoFocus)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(90)
        self.opacity_slider.valueChanged[int].connect(self.changeOpacity)
        self.changeOpacity(self.opacity_slider.value())

        bottom_layout.addWidget(self.opacity_slider)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        self.init_board()

        self.uiEnableSgn.emit(2)
        self.label.setText("접속 버튼을 누르세요.")

    def changeOpacity(self, value):
        opacity_value = value / 100.0
        self.setWindowOpacity(opacity_value)

    def init_board(self):
        button = self.HexagonButton(60, 60)
        button_2 = self.HexagonButton(120, 120)
        proxy = QGraphicsProxyWidget()
        proxy.setWidget(button)
        self.scene.addItem(proxy)
        proxy.setWidget(button_2)

    class HexagonButton(QPushButton):
        def __init__(self, x, y):
            super().__init__()
            self.x = x
            self.y = y

            # 육각형 이미지 생성
            self.hexagon_image = self.create_hexagon_image()

            # QIcon 생성
            icon = QIcon(self.hexagon_image)

            # 버튼 설정
            self.setIcon(icon)
            self.setIconSize(self.hexagon_image.size())
            self.setCheckable(True)

            # 스타일 시트를 사용하여 버튼의 모양을 육각형으로 조정
            hexagon_style = '''
                 QPushButton {
                     border: none;
                     background-color: transparent;
                 }
                 QPushButton::checked {
                     background-color: transparent;
                 }
                 QPushButton:checked:hover {
                     background-color: transparent;
                 }
             '''
            self.setStyleSheet(hexagon_style)

        def create_hexagon_image(self):
            # 이미지 크기와 배경색 설정
            size = 60
            hexagon_image = QPixmap(size, size)
            hexagon_image.fill(Qt.transparent)

            # QPainter를 사용하여 육각형 그리기
            painter = QPainter(hexagon_image)
            painter.setRenderHint(QPainter.Antialiasing)  # 안티앨리어싱을 사용하여 부드럽게 그리기

            # 육각형의 꼭지점 계산
            hexagon_points = self.calculate_hexagon_points(QPoint(int(size / 2), int(size / 2)), int(size / 2))

            # 육각형 그리기
            painter.drawPolygon(QPolygon(hexagon_points))

            # Draw text
            text_rect = hexagon_image.rect().adjusted(10, 10, -10, -10)  # Adjust the text position
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "1")

            # painter.drawText(self.rect().center(), "1")
            painter.end()

            return hexagon_image

        def calculate_hexagon_points(self, center, size):
            points = []
            for i in range(6):
                angle_deg = 60 * i
                angle_rad = math.radians(angle_deg)
                x = center.x() + size * math.cos(angle_rad)
                y = center.y() + size * math.sin(angle_rad)
                points.append(QPoint(int(x), int(y)))
            return points

        def mousePressEvent(self, event):
            print("Click!!")

    def game_result(self, result):
        win_msg = QMessageBox()
        lose_msg = QMessageBox()
        print("메세지 생성 시작")
        if result == 1:
            win_msg.information(self, "경기 결과", "승리 하셨습니다.")
        else:
            lose_msg.information(self, "경기 결과", "패배 하였습니다.")

    def connect_to_server(self):
        err_msg = QMessageBox()

        # 서버 연결
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f'Connected to server on {SERVER_HOST}:{SERVER_PORT}\n')

            # 클라이언트 수신을 위한 스레드 생성
            receive_thread = threading.Thread(target=receive_to_server, args=(self.client_socket,))
            receive_thread.start()

            self.client_socket.sendall(
                (JOIN + "|" + '\n').encode("utf-8"))

            self.label.setText("서버와 연결 되었습니다.")

        except socket.error as e:
            err_msg.information(self, "접속 실패", "서버 접속에 실패 하였습니다." + "\n" + e)


    def closeEvent(self, event):
        if self.client_socket:
            self.client_socket.sendall(
                (CLOSE + "|" + '\n').encode("utf-8"))


class MyGraphicsView(QGraphicsView):
    def __init__(self):
        super(MyGraphicsView, self).__init__()


class MyScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(MyScene, self).__init__(parent)


def receive_to_server(clients_socket):
    while True:
        try:
            receive_data = clients_socket.recv(BUFFER_SIZE).decode("utf-8")

            if len(receive_data) == 0:
                print("연결 끊김")
                clients_socket.close()

            data = receive_data.split("\n")

            for msg in data:
                command = msg.split("|")
                # 게임 시작 전 흑/백 선정
                if command[0] == BEFORE_GAME:
                    if command[1].strip() == START:
                        if client_gui.MY_COLOR == Qt.black:
                            client_gui.uiEnableSgn.emit(1)
                            client_gui.label.setText("게임 시작합니다. 당신은 흑 입니다.")
                        else:
                            client_gui.uiEnableSgn.emit(2)
                            client_gui.label.setText("게임 시작합니다. 당신은 백 입니다.")
                    elif int(command[1].strip()) == WHITE_PLAYER:
                        client_gui.MY_COLOR = Qt.white
                        client_gui.OPPONENT = Qt.black
                        client_gui.uiEnableSgn.emit(2)
                # 게임 시작 후

        except Exception as e:
            print(f'Error: {e}')
            clients_socket.close()
            break


# signal_object = SignalObject()
app = QtWidgets.QApplication(sys.argv)

client_gui = HexagonGUI()
client_gui.show()

# # 시그널이 발생하면 GUI를 업데이트
# signal_object.DataReceived.connect(client_gui.draw_board)
# # 클라이언트 송신을 위한 스레드 생성
# send_thread = threading.Thread(target=send_to_server, args=(client_socket,))
# send_thread.start()
sys.exit(app.exec_())