from random import shuffle

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox

from .widgets import (
    Element,
    PivotMarker,
    Marker,
    PickGreenRed,
    GreenGreaterPivot,
    GreenLessEqPivot,
    SwapGreenRed,
    Pivot,
    DecreaseGreen,
    DecreaseRed,
    SwapPivotRed,
    GreenMarkerPlaceholder,
    RedMarkerPlaceholder,
    PivotPlaceholder,
)


class DebugLayout(QHBoxLayout):
    def __init__(self, name):
        QHBoxLayout.__init__(self)
        self.log = False
        self.name = name

    def addWidget(self, widget):
        print(f"{self.name}: Added {widget}")
        QHBoxLayout.addWidget(self, widget)

    def insertWidget(self, index, widget, stretch=0):
        if self.log:
            print(f"{self.name}: Inserted {widget} at {index}")
        QHBoxLayout.insertWidget(self, index, widget, stretch)

    def removeWidget(self, widget):
        if self.log:
            print(f"{self.name}: Removed {widget}")
        QHBoxLayout.removeWidget(self, widget)


class QuicksortWidget(QWidget):
    def __init__(self, main_window):
        QWidget.__init__(self)
        self.main_window = main_window
        self.number_of_elements = 5
        self.old_number_of_elements = 5
        self.iteration = 1
        self.markers_placed = False

        self.elements = [
            Element(self,
                    value=i,
                    number_of_elements=self.number_of_elements,
                    parent_height=self.height(),
                    parent_width=self.width()
                    )
            for i in range(1, self.number_of_elements + 1)
        ]
        self.steps = []

        self.central_layout = QVBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.central_layout)

        self.layout_pivot_marker = QHBoxLayout()
        self.central_layout.addLayout(self.layout_pivot_marker)

        self.layout_bars = QHBoxLayout()
        self.layout_green_marker = QHBoxLayout()
        self.layout_red_marker = QHBoxLayout()
        self.central_layout.addLayout(self.layout_bars, stretch=1)
        self.central_layout.addLayout(self.layout_green_marker)
        self.central_layout.addLayout(self.layout_red_marker)

        self.values = [element.value for element in self.elements]

        self.pivot_marker = PivotMarker(0)
        self.green_marker = Marker("green", self.number_of_elements - 1)
        self.red_marker = Marker("red", self.number_of_elements - 1)

        self.create_elements()

    def mark_pivot(self, step: Pivot):
        # todo calculate pivot position
        self.pivot_marker = PivotMarker(0)
        ph = self.layout_pivot_marker.takeAt(0)
        self.layout_pivot_marker.removeWidget(ph.widget())
        ph.widget().deleteLater()
        self.layout_pivot_marker.insertWidget(
            self.pivot_marker.position, self.pivot_marker, 1
        )

        self.log(f"Pivot: {self.layout_bars.itemAt(step.index).widget().value}")

    def swap_pivot(self, step):
        self.swap_widgets(
            self.layout_pivot_marker,
            self.layout_pivot_marker.itemAt(step.index).widget(),
            self.layout_pivot_marker.itemAt(self.pivot_marker.position).widget(),
        )

        self.log(f"Pivot: {self.layout_bars.itemAt(step.index).widget().value}")

    def start(self):
        if self.main_window.start_button.text() == "Start":
            self.main_window.log.clear()
            self.main_window.start_button.setText("Stop")
            self.main_window.shuffle_button.setDisabled(True)
            self.log("--- Start ---")
            self.main_window.next_step_button.setEnabled(True)

            v = [element.value for element in self.elements]
            self.values = [element.value for element in self.elements]
            self.steps = []
            self.values = self.quicksort(v, 0, len(v) - 1)
            # from pprint import pprint
            # pprint(self.steps)
            self.execute_next_step()
        else:
            self.stop_sorting()
            self.main_window.start_button.setText("Start")
            self.log("--- Stop ---")
            self.main_window.next_step_button.setDisabled(True)
            self.main_window.shuffle_button.setEnabled(True)
            self.iteration = 1

    @staticmethod
    def swap_widgets(layout: QHBoxLayout | QVBoxLayout, w1, w2, log=False, align=None):
        if w1 == w2:
            return

        # if log:
        #     print("Layout ", layout, ":")
        #     for i in range(layout.count()):
        #         print(layout.itemAt(i).widget())
        #     print("i start:", layout.indexOf(w1), layout.indexOf(w2))
        #     print("w pos:", w1.position, w2.position)

        w1.position, w2.position = w2.position, w1.position

        widgets = []
        while layout.count():
            w = layout.takeAt(0).widget()
            widgets.append(w)

        widgets.sort(key=lambda w: w.position)
        for w in widgets:
            if align:
                layout.addWidget(w, 1, align)
            else:
                layout.addWidget(w, 1)

    def log(self, text: str):
        self.main_window.log.add_text(text)

    def pick_green_red(self, step: PickGreenRed):
        if self.green_marker is None:
            self.green_marker = Marker("green", self.number_of_elements - 1)
        if self.red_marker is None:
            self.red_marker = Marker("red", self.number_of_elements - 1)

        green = self.layout_green_marker.takeAt(step.green_index).widget()
        self.layout_green_marker.insertWidget(step.green_index, self.green_marker, 1)
        green.deleteLater()

        red = self.layout_red_marker.takeAt(step.red_index).widget()
        self.layout_red_marker.insertWidget(step.red_index, self.red_marker, 1)
        red.deleteLater()

        self.log(f"Green: {step.green_value} Red: {step.red_value}")

    def swap_markers(self, step: PickGreenRed):
        self.layout_green_marker.log = True
        self.swap_widgets(
            self.layout_green_marker,
            self.green_marker,
            self.layout_green_marker.itemAt(step.green_index).widget(),
        )

        self.swap_widgets(
            self.layout_red_marker,
            self.red_marker,
            self.layout_red_marker.itemAt(step.red_index).widget(),
        )
        self.log(f"Green: {step.green_value} Red: {step.red_value}")

    def green_less_eq_pivot(self, step: GreenLessEqPivot):
        self.log(f"Green {step.green_value} <= {step.pivot_value}")

    def decrease_green_marker(self):
        if self.green_marker.position > 0:
            self.swap_widgets(
                self.layout_green_marker,
                self.green_marker,
                self.layout_green_marker.itemAt(self.green_marker.position - 1).widget()
            )

            self.log("Decrease green marker")
        else:
            print("Green underflow")

    def decrease_red_marker(self):
        if self.red_marker.position > 0:
            self.swap_widgets(
                self.layout_red_marker,
                self.red_marker,
                self.layout_red_marker.itemAt(self.red_marker.position - 1).widget(),
            )
            self.log("Decrease red marker")
        else:
            print("Red underflow")

    def green_greater_pivot(self, step: GreenGreaterPivot):
        self.log(f"Green > pivot: {step.green_value} > {step.pivot_value}")

    def swap_green_red(self, step: SwapGreenRed):
        self.swap_widgets(
            self.layout_bars,
            self.layout_bars.itemAt(self.green_marker.position).widget(),
            self.layout_bars.itemAt(self.red_marker.position).widget(),
            align=Qt.AlignBottom
        )
        self.log(f"Swapping green <-> red: {step.green_value} <-> {step.red_value}")

    def swap_pivot_red(self, step: SwapPivotRed):
        self.swap_widgets(
            self.layout_bars,
            self.layout_bars.itemAt(step.pivot_index).widget(),
            self.layout_bars.itemAt(self.red_marker.position).widget(),
            align=Qt.AlignBottom
        )

        self.log(f"Swapping pivot <-> red: {step.pivot_value} <-> {step.red_value}")

    def execute_next_step(self):
        step = self.steps.pop(0) if self.steps else None
        # print("Executing", step)
        match step:
            case Pivot():
                if self.iteration == 1:
                    self.mark_pivot(step)
                    self.iteration += 1
                else:
                    self.swap_pivot(step)
            case PickGreenRed():
                if not self.markers_placed:
                    self.markers_placed = True
                    self.pick_green_red(step)
                else:
                    self.swap_markers(step)
            case GreenLessEqPivot():
                self.green_less_eq_pivot(step)
            case GreenGreaterPivot():
                self.green_greater_pivot(step)
            case SwapGreenRed():
                self.swap_green_red(step)
            case SwapPivotRed():
                self.swap_pivot_red(step)
            case DecreaseGreen():
                self.decrease_green_marker()
            case DecreaseRed():
                self.decrease_red_marker()
            case _:
                QMessageBox.about(self, "End of quicksort", "All element are sorted")
        self.main_window.scroll_area_log.move_bottom()

    def quicksort(self, v: list, start: int, end: int):
        if start == end:
            return []
        elif start == end + 1:
            return v

        pivot_value = v[start]
        pivot_index = v.index(pivot_value)

        self.steps.append(Pivot(pivot_index, pivot_value))

        green = end
        red = end

        self.steps.append(PickGreenRed(green, v[green], red, v[red]))

        while green > start:
            if pivot_value < v[green]:
                self.steps.append(
                    GreenGreaterPivot(green, v[green], pivot_index, pivot_value)
                )

                self.steps.append(SwapGreenRed(green, v[green], red, v[red]))
                v[green], v[red] = v[red], v[green]

                red -= 1
                self.steps.append(DecreaseRed())
            else:
                self.steps.append(
                    GreenLessEqPivot(green, v[green], pivot_index, pivot_value)
                )

            green -= 1
            self.steps.append(DecreaseGreen())

        self.steps.append(SwapPivotRed(pivot_index, pivot_value, red, v[red]))
        v[start], v[red] = v[red], v[start]

        self.quicksort(v, start, red - 1)
        self.quicksort(v, red + 1, end)

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        for element in self.elements:
            element.parent_height = self.layout_bars.geometry().height()
            element.updateGeometry()

    def delete_elements(self):
        for i in range(self.old_number_of_elements - 1, -1, -1):
            w = self.layout_bars.itemAt(i)
            if w:
                w = w.widget()
                self.layout_bars.removeWidget(w)
                w.deleteLater()

    @staticmethod
    def fill_layout(layout, widget, count: int):
        for i in range(count):
            w = widget(i)
            layout.addWidget(w, 1)

    @staticmethod
    def empty_layout(layout):
        w = layout.takeAt(0)
        while w:
            w.widget().deleteLater()
            w = layout.takeAt(0)

    def create_elements(self):
        self.empty_layout(self.layout_bars)

        self.elements = [
            Element(self,
                    value=i,
                    number_of_elements=self.number_of_elements,
                    parent_height=self.height(),
                    parent_width=self.width()
                    )
            for i in range(1, self.number_of_elements + 1)
        ]

        self.empty_layout(self.layout_pivot_marker)
        self.fill_layout(
            self.layout_pivot_marker, PivotPlaceholder, self.number_of_elements
        )

        self.empty_layout(self.layout_red_marker)
        self.fill_layout(
            self.layout_red_marker, RedMarkerPlaceholder, self.number_of_elements
        )

        self.empty_layout(self.layout_green_marker)
        self.fill_layout(
            self.layout_green_marker, GreenMarkerPlaceholder, self.number_of_elements
        )

        self.pivot_marker.position = 0
        self.green_marker.position = self.number_of_elements - 1
        self.red_marker.position = self.number_of_elements - 1

        # self.update_green_marker()
        # self.update_red_marker()

        for element in self.elements:
            self.layout_bars.addWidget(element, 1)
            self.layout_bars.setAlignment(element, Qt.AlignBottom)

    def stop_sorting(self):
        if self.red_marker:
            self.layout_red_marker.replaceWidget(self.red_marker, RedMarkerPlaceholder(self.red_marker.position))
            self.red_marker.deleteLater()
            self.red_marker = None

        if self.green_marker:
            self.layout_green_marker.replaceWidget(self.green_marker,
                                                   GreenMarkerPlaceholder(self.green_marker.position))
            self.green_marker.deleteLater()
            self.green_marker = None

        self.markers_placed = False

        if self.pivot_marker:
            self.layout_pivot_marker.replaceWidget(self.pivot_marker, PivotPlaceholder(self.pivot_marker.position))
            self.pivot_marker.deleteLater()
            self.pivot_marker = None

    def shuffle(self):
        self.main_window.log.clear()

        new_positions = list(range(self.number_of_elements))
        shuffle(new_positions)

        for position, element in zip(new_positions, self.elements):
            element.update_position(position)

        while self.layout_bars.count():
            self.layout_bars.removeWidget(self.layout_bars.itemAt(0).widget())

        self.elements.sort(key=lambda x: x.position)

        for element in self.elements:
            self.layout_bars.addWidget(element, 1, Qt.AlignBottom)

        self.main_window.log.add_text(f"Suffled {self.number_of_elements} elements")
