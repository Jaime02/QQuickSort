from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QSplitter,
)

from .quicksort_widget import QuicksortWidget
from .widgets import ScrollAreaBottom, LogWidget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Quicksort GUI")

        self.central_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.central_layout)

        self.array_size_layout = QHBoxLayout()
        self.central_layout.addLayout(self.array_size_layout)
        self.central_layout.setAlignment(Qt.AlignTop)

        self.array_size_label = QLabel("Number of elements: ")
        self.array_size_layout.addWidget(self.array_size_label)

        self.array_size_layout.addStretch()

        self.array_size_spinbox = QSpinBox()
        self.array_size_spinbox.setRange(2, 60)
        self.array_size_spinbox.setValue(6)
        self.array_size_spinbox.setMinimumWidth(40)
        self.array_size_layout.addWidget(self.array_size_spinbox)

        self.update_size_button = QPushButton("Update")
        self.array_size_layout.addWidget(self.update_size_button)
        self.update_size_button.clicked.connect(self.update_array_size)

        self.buttons_layout = QHBoxLayout()
        self.central_layout.addLayout(self.buttons_layout)

        self.shuffle_button = QPushButton("Shuffle!")
        self.buttons_layout.addWidget(self.shuffle_button)

        self.start_button = QPushButton("Start")
        self.buttons_layout.addWidget(self.start_button)

        self.next_step_button = QPushButton("Next step")
        self.next_step_button.setDisabled(True)
        self.buttons_layout.addWidget(self.next_step_button)

        self.auto_button = QPushButton("Automatic mode")
        self.auto_button.setDisabled(True)
        self.buttons_layout.addWidget(self.auto_button)

        period_label = QLabel("Period:")
        period_label.setAlignment(Qt.AlignCenter)
        self.buttons_layout.addWidget(period_label)

        self.speed_spinbox = QSpinBox()
        self.speed_spinbox.setRange(1, 5000)
        self.buttons_layout.addWidget(self.speed_spinbox)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setStyleSheet(
            "QSplitter::handle {background: lightgray; margin-top: 10px; margin-bottom: 10px;}"
        )

        self.central_layout.addWidget(self.splitter)
        self.splitter.setHandleWidth(14)
        self.quicksort_widget = QuicksortWidget(self)
        self.splitter.addWidget(self.quicksort_widget)

        self.shuffle_button.clicked.connect(self.quicksort_widget.shuffle)
        self.start_button.clicked.connect(self.quicksort_widget.start)
        self.next_step_button.clicked.connect(self.quicksort_widget.execute_next_step)
        self.auto_button.clicked.connect(self.quicksort_widget.run_auto)

        self.scroll_area_log = ScrollAreaBottom()
        self.log = LogWidget(self)
        self.splitter.addWidget(self.scroll_area_log)
        self.scroll_area_log.setWidget(self.log)

        self.clear_log_button = QPushButton("Clear log")
        self.central_layout.addWidget(self.clear_log_button)
        self.clear_log_button.clicked.connect(self.log.clear)
        self.resize(500, 600)

    def update_array_size(self):
        self.log.add_text(
            f"Updated number of elements: {self.quicksort_widget.number_of_elements} "
            f"-> {self.array_size_spinbox.value()}"
        )
        self.quicksort_widget.old_number_of_elements = (
            self.quicksort_widget.number_of_elements
        )
        self.quicksort_widget.number_of_elements = self.array_size_spinbox.value()
        self.quicksort_widget.create_elements()
