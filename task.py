from dataclasses import dataclass
import tkinter as tk
from enum import Enum
import numpy as np


class Mode(Enum):
    Rotate = 1
    Translate = 2
    Scale = 3
    Shear = 4
    PointDraw = 5
    LineDraw = 6
    PolygonDraw = 7

    def __str__(self) -> str:
        return super().__str__().split(".")[-1]


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class Line:
    p1: Point
    p2: Point

    def draw(self, canvas: tk.Canvas, color: str = "black"):
        canvas.create_line(self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=color)


@dataclass(frozen=True)
class Polygon:
    points: list[Point]

    def draw(self, canvas: tk.Canvas, color: str = "black"):
        # TODO: Fix drawing last line
        for i in range(len(self.points) - 1):
            Line(self.points[i], self.points[i + 1]).draw(canvas, color)


class App(tk.Tk):
    R: int = 5
    mode: str
    points: list[Point]
    line_buffer: list[Point]
    lines: list[Line]
    polygon_buffer: list[Point]
    polygons: list[Polygon]

    canvas: tk.Canvas
    buttons: tk.Frame
    button1: tk.Button
    button2: tk.Button
    button3: tk.Button
    button4: tk.Button
    button5: tk.Button
    button6: tk.Button
    button7: tk.Button
    status: tk.Label

    def __init__(self):
        super().__init__()
        self.title("Affine Transformation")
        self.geometry("800x600")
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
        self.canvas = tk.Canvas(self, width=800, height=550, bg="white")
        self.buttons = tk.Frame(self)
        self.button1 = tk.Button(self.buttons, text="Rotate", command=self.rotate)
        self.button2 = tk.Button(self.buttons, text="Scale", command=self.scale)
        self.button3 = tk.Button(self.buttons, text="Shear", command=self.shear)
        self.button4 = tk.Button(self.buttons, text="Translate", command=self.translate)
        self.button5 = tk.Button(self.buttons, text="Point Draw", command=self.point_draw)
        self.button6 = tk.Button(self.buttons, text="Line Draw", command=self.line_draw)
        self.button7 = tk.Button(self.buttons, text="Polygon Draw", command=self.polygon_draw)
        self.button8 = tk.Button(self.buttons, text="Reset", command=self.reset)
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
        self.status.pack(side="right", fill="x", padx=5)
        self.canvas.bind("<Button-1>", self.click)
        self.bind("<Escape>", self.reset)
        self.mainloop()

    def reset(self, *_):
        self.canvas.delete("all")
        self.mode = Mode.PointDraw
        self.status.config(text=f"Mode: {self.mode}")
        self.points = []
        self.polygons = []
        self.lines = []
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

    def in_point(self, p: Point, x: int, y: int) -> bool:
        return (x - p.x) ** 2 + (y - p.y) ** 2 <= self.R ** 2

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
                            print(polygon)
                        else:
                            self.polygon_buffer.append(p)
                        break


if __name__ == "__main__":
    App()
