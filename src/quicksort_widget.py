from random import shuffle

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QSizePolicy

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
            Element(self, i, self.number_of_elements, self.height(), self.width())
            for i in range(1, self.number_of_elements + 1)
        ]
        self.steps = []

        self.central_layout = QVBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.central_layout)

        self.layout_pivot_marker = QHBoxLayout()
        self.central_layout.addLayout(self.layout_pivot_marker)

        self.layout_bars = QHBoxLayout()
        self.layout_green_marker = DebugLayout("GM")
        self.layout_red_marker = DebugLayout("RM")
        self.central_layout.addLayout(self.layout_bars, stretch=1)
        self.central_layout.addLayout(self.layout_green_marker)
        self.central_layout.addLayout(self.layout_red_marker)

        self.colors = self.generate_gradient_rgbs(self.number_of_elements)

        self.values = [element.value for element in self.elements]

        self.pivot_marker = PivotMarker(0)
        self.green_marker = Marker("green", self.number_of_elements - 1)
        self.red_marker = Marker("red", self.number_of_elements - 1)

        self.create_elements()

    def mark_pivot(self, step: Pivot):
        # todo calculate pivot position
        ph = self.layout_pivot_marker.takeAt(0)
        self.layout_pivot_marker.removeWidget(ph.widget())
        ph.widget().deleteLater()
        self.layout_pivot_marker.insertWidget(
            self.pivot_marker.position, self.pivot_marker
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
        self.main_window.log.clear()
        self.log("--- Start ---")
        self.main_window.next_step_button.setEnabled(True)

        v = [element.value for element in self.elements]
        self.values = [element.value for element in self.elements]
        self.values = self.quicksort(v)
        # from pprint import pprint
        # pprint(self.steps)
        self.execute_next_step()

    def swap_widgets(self, layout: QHBoxLayout | QVBoxLayout, w1, w2, log=False):
        if w1 == w2:
            return

        if log:
            # print("Layout ", layout, ":")
            # for i in range(layout.count()):
            #     print(layout.itemAt(i).widget())
            print("i start:", layout.indexOf(w1), layout.indexOf(w2))
            print("w pos:", w1.position, w2.position)

        assert layout.count() == self.number_of_elements

        w1.position, w2.position = w2.position, w1.position

        layout.removeWidget(w1)
        layout.removeWidget(w2)

        assert layout.count() == self.number_of_elements - 2

        layout.insertWidget(w1.position, w1)
        layout.insertWidget(w2.position, w2)

        assert layout.count() == self.number_of_elements

        if log:
            print("i end:", layout.indexOf(w1), layout.indexOf(w2))
            print()

    def log(self, text: str):
        self.main_window.log.add_text(text)

    def pick_green_red(self, step: PickGreenRed):
        green = self.layout_green_marker.takeAt(step.green_index).widget()
        self.layout_green_marker.insertWidget(step.green_index, self.green_marker)
        green.deleteLater()

        red = self.layout_red_marker.takeAt(step.red_index).widget()
        self.layout_red_marker.insertWidget(step.red_index, self.red_marker)
        red.deleteLater()

        assert self.layout_green_marker.count() == self.number_of_elements
        assert self.layout_red_marker.count() == self.number_of_elements
        self.log(f"Green: {step.green_value} Red: {step.red_value}")

    def swap_markers(self, step: PickGreenRed):
        self.layout_green_marker.log = True
        self.swap_widgets(
            self.layout_green_marker,
            self.green_marker,
            self.layout_green_marker.itemAt(step.green_index).widget(),
            log=True
        )

        self.swap_widgets(
            self.layout_red_marker,
            self.red_marker,
            self.layout_red_marker.itemAt(step.red_index).widget(),
            log=True
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
            assert self.layout_green_marker.count() == self.number_of_elements
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
            assert self.layout_red_marker.count() == self.number_of_elements
        else:
            print("Red underflow")

    def green_greater_pivot(self, step: GreenGreaterPivot):
        self.log(f"Green > pivot: {step.green_value} > {step.pivot_value}")

    def swap_green_red(self, step: SwapGreenRed):
        self.swap_widgets(
            self.layout_bars,
            self.layout_bars.itemAt(self.green_marker.position).widget(),
            self.layout_bars.itemAt(self.red_marker.position).widget(),
            log=True
        )
        self.log(f"Swapping green <-> red: {step.green_value} <-> {step.red_value}")

    def swap_pivot_red(self, step: SwapPivotRed):
        self.swap_widgets(
            self.layout_bars,
            self.layout_bars.itemAt(step.pivot_index).widget(),
            self.layout_bars.itemAt(self.red_marker.position).widget(),
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

    def quicksort(self, v: list):
        if len(v) == 1:
            return v
        elif len(v) == 0:
            return []
        # print("Args:", v)

        pivot_value = v[0]
        pivot_index = self.values.index(pivot_value)

        self.steps.append(Pivot(pivot_index, pivot_value))

        green = len(v) - 1
        red = len(v) - 1

        self.steps.append(PickGreenRed(self.values.index(v[green]), v[green], self.values.index(v[red]), v[red]))

        while green:
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
        v[0], v[red] = v[red], v[0]

        result = []
        left = self.quicksort(v[:red])
        right = self.quicksort(v[red + 1:])
        result.extend(left)
        result.append(pivot_value)
        result.extend(right)
        return result

    @staticmethod
    def generate_gradient_rgbs(num_buckets):
        rgb_codes = []
        step_size = 1024 / num_buckets
        for step in range(0, num_buckets):
            red = int(max(0, 255 - (step_size * step * 0.5)))
            # step size is half of the step size since both this item goes down and the next one goes up
            blue = int(max(0, 255 - (step_size * 0.5 * (num_buckets - step - 1))))
            green = (255 - red) if red else (255 - blue)
            rgb_codes.append((red, green, blue))
        return rgb_codes

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
            layout.addWidget(w)

    @staticmethod
    def empty_layout(layout):
        w = layout.takeAt(0)
        while w:
            w.widget().deleteLater()
            w = layout.takeAt(0)

    def create_elements(self):
        self.elements = [
            Element(self, i, self.number_of_elements, self.height(), self.width())
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
            self.layout_bars.addWidget(element)
            self.layout_bars.setAlignment(element, Qt.AlignBottom)

        self.colors = self.generate_gradient_rgbs(self.number_of_elements)

    def update_pivot(self):
        for element in [
            self.layout_pivot.itemAt(i).widget()
            for i in range(self.layout_pivot.count())
        ]:
            self.layout_pivot.removeWidget(element)
            self.layout_pivot.insertWidget(element.position, element)
            self.layout_pivot.setAlignment(element, Qt.AlignBottom)

    def update_green_marker(self):
        widgets = []
        for _ in range(self.layout_green_marker.count()):
            widgets.append(self.layout_green_marker.takeAt(0).widget())

        assert self.layout_green_marker.count() == 0
        
        for element in sorted(widgets, key=lambda elem: elem.position):
            self.layout_green_marker.addWidget(element)
            self.layout_green_marker.setAlignment(element, Qt.AlignBottom)

    def update_red_marker(self):
        widgets = []
        for _ in range(self.layout_red_marker.count()):
            widgets.append(self.layout_red_marker.takeAt(0).widget())

        assert self.layout_red_marker.count() == 0

        for element in sorted(widgets, key=lambda elem: elem.position):
            self.layout_red_marker.addWidget(element)
            self.layout_red_marker.setAlignment(element, Qt.AlignBottom)

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
            self.layout_bars.addWidget(element, 0, Qt.AlignBottom)

        self.main_window.log.add_text(f"Suffled {self.number_of_elements} elements")
