import sys
import enum
from PyQt5 import QtCore as qc
from PyQt5 import QtWidgets as qw
from PyQt5 import QtGui as qg
from random import randint

from PyQt5.QtWidgets import QDesktopWidget


class Directions(enum.IntEnum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class Color(enum.IntEnum):
    FRUIT = 0xffff0000
    SNAKE = 0xff00ff00
    POWER_UP = 0xff0000ff
    BACKGROUND = 0xff000000


class Settings:
    def __init__(self, speed, field_size, zoom, boarder_loop, fruit_prob):
        self.speed = speed
        self.field_size = field_size
        self.zoom = zoom
        self.boarder_loop = boarder_loop
        self.fruit_prob = fruit_prob
        self.first_spawn = 0


class FieldElement:
    def __init__(self, pos_x, pos_y):
        self.pos_x = int(pos_x)
        self.pos_y = int(pos_y)


class Snake:
    direction = Directions.DOWN
    current_direction = Directions.DOWN
    eaten = 0

    def __init__(self, field_size):
        self.field_size = field_size
        self.head = FieldElement(field_size // 2, field_size // 2 + 1)
        self.snake_list = [self.head, FieldElement(field_size // 2 - 1, field_size // 2 + 1),
                           FieldElement(field_size // 2 - 2, field_size // 2 + 1)]
        self.fruit_list = [self.new_fruit()]

    def spawn_fruit(self):
        print_pixel(self.fruit_list[0].pos_x, self.fruit_list[0].pos_y, Color.FRUIT)

    def swap_list(self):
        # check if new fruit is spawned at snake tail
        if self.snake_list[-1].pos_x != self.fruit_list[0].pos_x or \
                        self.snake_list[-1].pos_y != self.fruit_list[0].pos_y:
            print_pixel(self.snake_list[-1].pos_x, self.snake_list[-1].pos_y, Color.BACKGROUND)

        self.snake_list.insert(0, FieldElement(self.head.pos_x, self.head.pos_y))
        self.head = self.snake_list[0]

        print_pixel(self.head.pos_x, self.head.pos_y, Color.SNAKE)
        del self.snake_list[-1]

    def new_fruit(self):
        new_x, new_y = randint(1, self.field_size), randint(1, self.field_size)
        check_element = FieldElement(new_x, new_y)

        while not self.check_collision(check_element, 0):
            new_x = randint(1, self.field_size)
            new_y = randint(1, self.field_size)

            check_element = FieldElement(new_x, new_y)

        return FieldElement(new_x, new_y)

    def move(self):
        # prevent snake running into itself!
        if self.direction == Directions.UP and self.current_direction == Directions.DOWN:
            self.direction = Directions.DOWN
        else:
            if self.direction == Directions.RIGHT and self.current_direction == Directions.LEFT:
                self.direction = Directions.LEFT
            else:
                if self.direction == Directions.DOWN and self.current_direction == Directions.UP:
                    self.direction = Directions.UP
                else:
                    if self.direction == Directions.LEFT and self.current_direction == Directions.RIGHT:
                        self.direction = Directions.RIGHT

        if self.direction == Directions.UP:
            self.head = FieldElement(self.head.pos_x - 1, self.head.pos_y)
            if self.check_boarder_collision() == 0 or self.check_head_collision() == 0:
                return 0
            self.current_direction = Directions.UP
        else:
            if self.direction == Directions.RIGHT:
                self.head = FieldElement(self.head.pos_x, self.head.pos_y + 1)
                if self.check_boarder_collision() == 0 or self.check_head_collision() == 0:
                    return 0
                self.current_direction = Directions.RIGHT
            else:
                if self.direction == Directions.DOWN:
                    self.head = FieldElement(self.head.pos_x + 1, self.head.pos_y)
                    if self.check_boarder_collision() == 0 or self.check_head_collision() == 0:
                        return 0
                    self.current_direction = Directions.DOWN
                else:
                    if self.direction == Directions.LEFT:
                        self.head = FieldElement(self.head.pos_x, self.head.pos_y - 1)
                        if self.check_boarder_collision() == 0 or self.check_head_collision() == 0:
                            return 0
                        self.current_direction = Directions.LEFT

    def check_collision(self, field_element, start):
        for i_check_collision in range(start, len(self.snake_list)):
            if field_element.pos_x == self.snake_list[i_check_collision].pos_x and \
                            field_element.pos_y == self.snake_list[i_check_collision].pos_y:
                return False
            return 1

    def check_head_collision(self):
        for i_check_collision in range(0, len(self.snake_list)):
            # print(self.head.pos_x, self.snake_list[i_check_collision].pos_x)
            # print(self.head.pos_y, self.snake_list[i_check_collision].pos_y)
            if self.head.pos_x == self.snake_list[i_check_collision].pos_x and \
                            self.head.pos_y == self.snake_list[i_check_collision].pos_y:
                game_over()
                return 0

    def check_boarder_collision(self):
        # check for boarder collision if enabled
        if self.head.pos_y > self.field_size \
                or self.head.pos_x > self.field_size \
                or self.head.pos_y < 1 \
                or self.head.pos_x < 1:
            game_over()
            return 0


class Form(qw.QWidget):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        main_widget = qw.QWidget(main_window)
        main_widget.resize(1000, 500)

        # Layouts
        h_box_wrap = qw.QHBoxLayout()
        form_wrap = qw.QFormLayout()

        btn_start = qw.QPushButton("Start")
        btn_exit = qw.QPushButton("Exit")
        btn_start.setDefault(True)
        btn_start.clicked.connect(lambda: self.clicked_start())

        self.le_speed = qw.QLineEdit("500")
        self.le_size = qw.QLineEdit("17")
        self.le_zoom = qw.QLineEdit("1")
        self.le_loop = qw.QLineEdit("0")
        self.le_prob = qw.QLineEdit("1")

        form_wrap.addRow(qw.QLabel("Speed"), self.le_speed)
        form_wrap.addRow(qw.QLabel("Field size"), self.le_size)
        form_wrap.addRow(qw.QLabel("zoom"), self.le_zoom)
        form_wrap.addRow(qw.QLabel("Boarder Loop"), self.le_loop)
        form_wrap.addRow(qw.QLabel("Fruit Prob"), self.le_prob)
        form_wrap.addRow(btn_start, btn_exit)

        h_box_wrap.addLayout(form_wrap)
        # h_box_wrap.addStretch()
        h_box_wrap.addWidget(display)

        main_widget.setLayout(h_box_wrap)

    def clicked_start(self):
        # Timer
        timer.start(500)
        display.setFocus()

# ----- main function ----
#
# Snake logic and functions

def move_event(e):
    if e.key() == qc.Qt.Key_Up and not snake.direction == Directions.DOWN:
        snake.direction = Directions.UP
    if e.key() == qc.Qt.Key_Right and not snake.direction == Directions.LEFT:
        snake.direction = Directions.RIGHT
    if e.key() == qc.Qt.Key_Down and not snake.direction == Directions.UP:
        snake.direction = Directions.DOWN
    if e.key() == qc.Qt.Key_Left and not snake.direction == Directions.RIGHT:
        snake.direction = Directions.LEFT


def event_loop():

    # TEST: Show Snake Elements
    # for test_i in range(0, len(snake.snake_list)):
    #     print("Snake Element ", test_i+1, ": ", snake.snake_list[test_i].pos_x, snake.snake_list[test_i].pos_y)

    # check first fruit spawn
    if len(snake.snake_list) == 3 and gameSettings.first_spawn < 1:
        snake.spawn_fruit()
        gameSettings.first_spawn = 1

    # move snake
    checker = snake.move()

    # check if fruit was eaten
    if snake.fruit_list[0].pos_y == snake.head.pos_y and snake.fruit_list[0].pos_x == snake.head.pos_x:

        # add new snake segment
        snake.snake_list.insert(0, snake.fruit_list[0])
        snake.head = snake.fruit_list[0]
        print_pixel(snake.head.pos_x, snake.head.pos_y, Color.SNAKE)

        # spawn new/next fruit
        snake.fruit_list[0] = snake.new_fruit()
        snake.spawn_fruit()
    else:
        if checker != 0:
            snake.swap_list()

    snake_field_img_scaled_def = snake_field_img.scaled(display.size(), qc.Qt.KeepAspectRatio)
    display.setPixmap(qg.QPixmap.fromImage(snake_field_img_scaled_def))


def game_over():
    main_window.setWindowTitle("Game Over!")
    timer.stop()


def print_pixel(pos_x, pos_y, color):
    snake_field_img.setPixel(pos_y - 1, pos_x - 1, color)
    # swapping dimensions!


if __name__ == "__main__":
    # Start QW Application
    #tset comment
    app = qw.QApplication(sys.argv)

    # Create Display Widget to contain
    display = qw.QLabel()
    display.resize(500, 500)
    # display.move(500, 0)

    # ----- Window -----
    main_window = qw.QMainWindow()
    main_window.setGeometry(0, 0, 1000, 500)
    frame_geometry = main_window.frameGeometry()
    center = QDesktopWidget().availableGeometry().center()
    frame_geometry.moveCenter(center)
    main_window.move(frame_geometry.topLeft())
    main_window.setWindowTitle("Snake - much extreme, much niceness")

    # Assign Event Handler
    main_window.keyPressEvent = move_event

    widget = Form(main_window)
    main_window.show()

    # Create Standard Game Settings
    gameSettings = Settings(widget.le_speed.toInt(), widget.le_size, widget.le_zoom, widget.le_loop, widget.le_prob)

    # Create Snake Game Object
    snake = Snake(gameSettings.field_size)

    # print_pixel(snake.snake_list[-1].pos_x, snake.snake_list[-1].pos_y, Color.BACKGROUND)


    timer = qc.QTimer()
    timer.setInterval(int(gameSettings.speed))
    timer.timeout.connect(event_loop)

    # Create Drawable Image
    snake_field_img = qg.QImage(gameSettings.field_size, gameSettings.field_size, qg.QImage.Format_RGB32)
    snake_field_img.fill(qc.Qt.black)


    # Draw start Snake Elements on image
    for i in range(0, len(snake.snake_list)):
        print_pixel(snake.snake_list[i].pos_x, snake.snake_list[i].pos_y, Color.SNAKE)

    # Scale and show image
    snake_field_img_scaled = snake_field_img.scaled(display.size(), qc.Qt.KeepAspectRatio)
    display.setPixmap(qg.QPixmap.fromImage(snake_field_img_scaled))


sys.exit(app.exec_())