from dataclasses import dataclass

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QScrollArea,
)


class LogWidget(QLabel):
    def __init__(self, main_window):
        QLabel.__init__(self)
        self.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        self.main_window = main_window

    def add_text(self, text: str):
        if self.text():
            self.setText(self.text() + "\n" + text)
        else:
            self.setText(text)
        self.main_window.scroll_area_log.move_bottom()


class Element(QLabel):
    def __init__(
        self,
        quicksort_widget,
        value: int,
        number_of_elements: int,
        parent_height: int,
        parent_width: int,
    ):

        QLabel.__init__(self)
        self.quicksort_widget = quicksort_widget
        self.value = value
        self.position = value - 1  # This is true when the widgets are sorted
        self.number_of_elements = number_of_elements
        self.parent_height = parent_height
        self.parent_width = parent_width
        self.setText(f"{self.position} - {self.value}")
        self.setAlignment(Qt.AlignCenter | Qt.AlignBottom)

    def update_position(self, position: int):
        self.position = position
        self.setText(f"{self.position} - {self.value}")

    def widget_width(self):
        return int(self.parent_width / self.number_of_elements)

    def widget_height(self):
        return int(self.parent_height / self.number_of_elements * self.value)

    def sizeHint(self) -> QSize:
        return QSize(self.widget_width(), self.widget_height())

    def paintEvent(self, event):
        qp = QPainter(self)

        # From https://stackoverflow.com/a/3407960/11760835
        def spectral_color(w):
            if 380 <= w < 440:
                R = -(w - 440.0) / (440.0 - 380.0)
                G = 0.0
                B = 1.0
            elif 440 <= w < 490:
                R = 0.0
                G = (w - 440.0) / (490.0 - 440.0)
                B = 1.0
            elif 490 <= w < 510:
                R = 0.0
                G = 1.0
                B = -(w - 510.0) / (510.0 - 490.0)
            elif 510 <= w < 580:
                R = (w - 510.0) / (580.0 - 510.0)
                G = 1.0
                B = 0.0
            elif 580 <= w < 645:
                R = 1.0
                G = -(w - 645.0) / (645.0 - 580.0)
                B = 0.0
            elif 645 <= w <= 780:
                R = 1.0
                G = 0.0
                B = 0.0
            else:
                R = 0.0
                G = 0.0
                B = 0.0

            return R * 255, G * 255, B * 255

        rgb = spectral_color(
            400 + 250 * self.value / self.quicksort_widget.number_of_elements
        )

        qp.fillRect(QRect(0, 0, self.width(), self.height()), QColor(*rgb))
        QLabel.paintEvent(self, event)
        self.setText(f"{self.position} - {self.value}")

    def __repr__(self):
        return f"E({self.position=}, {self.value=})"


@dataclass
class PivotMarker(QLabel):
    def __init__(self, position):
        QLabel.__init__(self)
        self.position = position
        self.setStyleSheet("background: yellow;")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)


class Marker(QLabel):
    def __init__(self, color: str, position: int):
        QLabel.__init__(self)
        self.color = color
        if color == "green":
            self.setStyleSheet(f"background: rgb(0, 255, 0)")
        elif color == "red":
            self.setStyleSheet(f"background: rgb(255, 77, 77)")
        else:
            raise Exception("Unknown color")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.position = position

    def __repr__(self):
        return f"Marker({self.color=}, {self.position=})"

    # def __del__(self):
    #     print(f"Se borró {self}")


@dataclass
class GreenMarkerPlaceholder(QLabel):
    def __init__(self, position: int):
        QLabel.__init__(self)
        self.position = position
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setStyleSheet("background: rgb(230, 230, 230);")

    def __repr__(self):
        return f"GreenMarkerPlaceholder({self.position=})"

    # def __del__(self):
    #     print(f"Deleted {self}")


@dataclass
class RedMarkerPlaceholder(QLabel):
    def __init__(self, position: int):
        QLabel.__init__(self)
        self.position = position
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setStyleSheet("background: rgb(230, 230, 230);")

    def __repr__(self):
        return f"RedMarkerPlaceholder({self.position=})"

    # def __del__(self):
    #     print(f"Deleted {self}")


@dataclass
class PivotPlaceholder(QLabel):
    def __init__(self, position: int):
        QLabel.__init__(self)
        self.position = position
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setStyleSheet("background: rgb(230, 230, 230);")

    def __repr__(self):
        return f"PivotPlaceholder({self.position=})"


@dataclass
class Pivot:
    index: int
    value: int


@dataclass
class PickGreenRed:
    green_index: int
    green_value: int
    red_index: int
    red_value: int


@dataclass
class GreenLessEqPivot:
    green_index: int
    green_value: int
    pivot_index: int
    pivot_value: int


@dataclass
class GreenGreaterPivot:
    green_index: int
    green_value: int
    pivot_index: int
    pivot_value: int


@dataclass
class SwapGreenRed:
    green_index: int
    green_value: int
    red_index: int
    red_value: int


@dataclass
class SwapPivotRed:
    pivot_index: int
    pivot_value: int
    red_index: int
    red_value: int


@dataclass
class DecreaseGreen:
    pass


@dataclass
class DecreaseRed:
    pass


class ScrollAreaBottom(QScrollArea):
    def __init__(self):
        QScrollArea.__init__(self)
        self.setWidgetResizable(True)

    def move_bottom(self):
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def resizeEvent(self, event):
        QScrollArea.resizeEvent(self, event)
        self.move_bottom()
