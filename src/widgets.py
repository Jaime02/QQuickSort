from dataclasses import dataclass

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QWidget,
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


class Element(QWidget):
    def __init__(
        self,
        quicksort_widget,
        value: int,
        number_of_elements: int,
        parent_height: int,
        parent_width: int,
    ):
        QWidget.__init__(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.quicksort_widget = quicksort_widget
        self.value = value
        self.position = value - 1  # This is true when the widgets are sorted
        self.number_of_elements = number_of_elements
        self.parent_height = parent_height
        self.parent_width = parent_width

    def update_position(self, position: int):
        self.position = position

    @property
    def widget_width(self):
        return int(self.parent_width / self.number_of_elements)

    @property
    def widget_height(self):
        return int(self.parent_height / self.number_of_elements * self.value)

    def sizeHint(self) -> QSize:
        return QSize(self.widget_width, self.widget_height)

    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        qp = QPainter(self)
        rgb = self.quicksort_widget.colors[self.value - 1]
        qp.fillRect(QRect(0, 0, self.width(), self.height()), QColor(*rgb))

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


@dataclass
class GreenMarkerPlaceholder(QLabel):
    def __init__(self, position: int):
        QLabel.__init__(self)
        self.position = position
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setStyleSheet("background: rgb(230, 230, 230);")

    def __repr__(self):
        return f"GreenMarkerPlaceholder({self.position=})"


@dataclass
class RedMarkerPlaceholder(QLabel):
    def __init__(self, position: int):
        QLabel.__init__(self)
        self.position = position
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setStyleSheet("background: rgb(230, 230, 230);")

    def __repr__(self):
        return f"RedMarkerPlaceholder({self.position=})"


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
