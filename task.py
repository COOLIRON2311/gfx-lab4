from dataclasses import dataclass
import tkinter as tk
from enum import Enum
import numpy as np


class Mode(Enum):
    Rotate = 1  # вращение
    Translate = 2  # перемещение
    Scale = 3  # масштабирование
    Shear = 4  # сдвиг
    PointDraw = 5  # рисование точки
    LineDraw = 6  # рисование линии
    PolygonDraw = 7  # рисование полигона
    SelectShape = 8  # выбор примитива
    ApplySpecFunc = 9  # применение специальной функции

    def __str__(self) -> str:
        return super().__str__().split(".")[-1]


class SpecialFunctions(Enum):
    None_ = 0
    PointInConvexPoly = 1
    PointInNonConvexPoly = 2
    ClassifyPointPosition = 3
    RotateEdge90 = 4
    EdgeIntersect = 5

    def __str__(self) -> str:
        match self:
            case SpecialFunctions.None_:
                return "No special function"
            case SpecialFunctions.PointInConvexPoly:
                return "Point in convex polygon"
            case SpecialFunctions.PointInNonConvexPoly:
                return "Point in non-convex polygon"
            case SpecialFunctions.ClassifyPointPosition:
                return "Classify point position"
            case SpecialFunctions.RotateEdge90:
                return "Rotate edge 90 degrees"
            case SpecialFunctions.EdgeIntersect:
                return "Edge intersection"
        return super().__str__()


@dataclass
class Point:
    x: int
    y: int

    def draw(self, canvas: tk.Canvas, color: str = "black", radius: int = 5):
        canvas.create_oval(self.x - radius, self.y - radius, self.x + radius,
                           self.y + radius, fill=color, outline=color)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Point):
            return self.x == __o.x and self.y == __o.y
        return False


@dataclass
class Line:
    p1: Point
    p2: Point

    def draw(self, canvas: tk.Canvas, color: str = "black"):
        canvas.create_line(self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=color)


@dataclass
class Polygon:
    lines: list[Line]

    def __init__(self, points) -> None:
        self.points = points
        ln = len(points)
        self.lines = [Line(points[i], points[(i + 1) % ln]) for i in range(ln)]

    def draw(self, canvas: tk.Canvas, color: str = "black"):
        for line in self.lines:
            line.draw(canvas, color)


class App(tk.Tk):
    W: int = 1000
    H: int = 600
    R: int = 5
    mode: str
    points: list[Point]
    line_buffer: list[Point]
    lines: list[Line]
    polygon_buffer: list[Point]
    polygons: list[Polygon]
    selected_shape = None
    spec_func_idx: int = 0

    def __init__(self):
        super().__init__()
        self.title("Affine Transformation")
        self.geometry(f"{self.W}x{self.H}")
        self.resizable(0, 0)
        self.mode = Mode.PointDraw
        self.points = []
        self.lines = []
        self.polygons = []
        self.line_buffer = []
        self.polygon_buffer = []

        self.create_widgets()
        self.mainloop()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=self.W, height=self.H-30, bg="white")
        self.buttons = tk.Frame(self)
        self.button1 = tk.Button(self.buttons, text="Rotate", command=self.rotate)
        self.button2 = tk.Button(self.buttons, text="Scale", command=self.scale)
        self.button3 = tk.Button(self.buttons, text="Shear", command=self.shear)
        self.button4 = tk.Button(self.buttons, text="Translate", command=self.translate)
        self.button5 = tk.Button(self.buttons, text="Point Draw", command=self.point_draw)
        self.button6 = tk.Button(self.buttons, text="Line Draw", command=self.line_draw)
        self.button7 = tk.Button(self.buttons, text="Polygon Draw", command=self.polygon_draw)
        self.button8 = tk.Button(self.buttons, text="Reset", command=self.reset)
        self.button9 = tk.Button(self.buttons, text="Select Shape", command=self.select_shape)
        self.button10 = tk.Button(self.buttons, text="Apply", command=self.apply_spec_func)
        self.listbox = tk.Listbox(self.buttons, selectmode=tk.SINGLE, height=1, width=30)
        self.scrollbar = tk.Scrollbar(self.buttons, orient=tk.VERTICAL)
        self.status = tk.Label(self.buttons, text=f"Mode: {self.mode}", bd=1, relief=tk.SUNKEN, anchor=tk.E)
        self.canvas.pack()
        self.canvas.config(cursor="cross")
        self.buttons.pack(side="bottom", fill="x")
        self.button1.pack(side="left", fill="x")
        self.button2.pack(side="left", fill="x")
        self.button3.pack(side="left", fill="x")
        self.button4.pack(side="left", fill="x")
        self.button5.pack(side="left", fill="x")
        self.button6.pack(side="left", fill="x")
        self.button7.pack(side="left", fill="x")
        self.button8.pack(side="left", fill="x")
        self.status.pack(side="right", fill="x", padx=5)
        self.button10.pack(side="right", fill="x", padx=5)
        self.listbox.pack(side="right", fill="x")
        self.scrollbar.pack(side="right", fill="y")

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.scroll)
        self.listbox.delete(0, tk.END)
        self.listbox.insert(0, *SpecialFunctions)

        self.button9.pack(side="right", fill="x", padx=5)
        self.canvas.bind("<Button-1>", self.click)
        self.bind("<Escape>", self.reset)
        self.bind("<Return>", self.redraw)
        self.bind("<BackSpace>", self.clear_buffs)
        self.mainloop()

    def scroll(self, *args):
        d = int(args[1])
        if 0 < self.spec_func_idx + d < len(SpecialFunctions):
            self.spec_func_idx += d
        self.listbox.yview(*args)

    def reset(self, *_):
        self.canvas.delete("all")
        self.mode = Mode.PointDraw
        self.status.config(text=f"Mode: {self.mode}")
        self.points = []
        self.polygons = []
        self.lines = []
        self.line_buffer = []
        self.polygon_buffer = []

    def redraw(self, *_):
        self.canvas.delete("all")
        self.points = []
        for line in self.lines:
            line.draw(self.canvas)
        for polygon in self.polygons:
            polygon.draw(self.canvas)

    def clear_buffs(self, *_):
        self.line_buffer = []
        self.polygon_buffer = []

    def rotate(self):
        self.mode = Mode.Rotate
        self.status.config(text=f"Mode: {self.mode}")

    def scale(self):
        self.mode = Mode.Scale
        self.status.config(text=f"Mode: {self.mode}")

    def shear(self):
        self.mode = Mode.Shear
        self.status.config(text=f"Mode: {self.mode}")

    def translate(self):
        self.mode = Mode.Translate
        self.status.config(text=f"Mode: {self.mode}")

    def point_draw(self):
        self.mode = Mode.PointDraw
        self.status.config(text=f"Mode: {self.mode}")

    def line_draw(self):
        self.mode = Mode.LineDraw
        self.status.config(text=f"Mode: {self.mode}")

    def polygon_draw(self):
        self.mode = Mode.PolygonDraw
        self.status.config(text=f"Mode: {self.mode}")

    def select_shape(self):
        self.mode = Mode.SelectShape
        self.status.config(text=f"Mode: {self.mode}")

    def apply_spec_func(self):
        func = SpecialFunctions(self.spec_func_idx)

        match func:
            case SpecialFunctions.None_:
                ...
            case SpecialFunctions.PointInConvexPoly:
                ...
            case SpecialFunctions.PointInNonConvexPoly:
                ...
            case SpecialFunctions.ClassifyPointPosition:
                ...
            case SpecialFunctions.RotateEdge90:
                ...
            case SpecialFunctions.EdgeIntersect:
                ...

        self.mode = Mode.SelectShape
        self.status.config(text=f"Mode: {self.mode}")

    def in_point(self, p: Point, x: int, y: int) -> bool:
        return (x - p.x) ** 2 + (y - p.y) ** 2 <= self.R ** 2

    def highlight_point(self, p: Point, timeout: int = 200):
        highlight = self.canvas.create_oval(p.x - self.R, p.y - self.R, p.x + self.R,
                                            p.y + self.R, fill="red", outline="red")
        self.canvas.after(timeout, self.canvas.delete, highlight)

    def click(self, event: tk.Event):
        match self.mode:
            case Mode.PointDraw:
                point = Point(event.x, event.y)
                self.points.append(point)
                point.draw(self.canvas)

            case Mode.LineDraw:
                for p in self.points:
                    if self.in_point(p, event.x, event.y):
                        self.line_buffer.append(p)
                        self.highlight_point(p)

                if len(self.line_buffer) == 2:
                    line = Line(self.line_buffer[0], self.line_buffer[1])
                    self.line_buffer = []
                    line.draw(self.canvas)
                    self.lines.append(line)

            case Mode.PolygonDraw:
                point = Point(event.x, event.y)
                for p in self.points:
                    if self.in_point(point, p.x, p.y):
                        if len(self.polygon_buffer) > 0 and p == self.polygon_buffer[0]:
                            polygon = Polygon(self.polygon_buffer)
                            self.polygon_buffer = []
                            polygon.draw(self.canvas)
                            self.polygons.append(polygon)
                        else:
                            self.polygon_buffer.append(p)
                            self.highlight_point(p)
                        break

            case Mode.Rotate:
                ...

            case Mode.Scale:
                ...

            case Mode.Shear:
                ...

            case Mode.Translate:
                ...

            case Mode.SelectShape:
                ...

            case Mode.ApplySpecFunc:
                ...


if __name__ == "__main__":
    App()
