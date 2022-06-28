#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Wed Feb 26 01:54:04 2020
# @author: Fernando Camussi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" Pizarra """

from enum import Enum, auto
from PyQt5.QtWidgets import (QLabel,
                             QRubberBand,
                             QFrame)
from PyQt5.QtGui import (QPen,
                         QPainter,
                         QColor)
from PyQt5.QtCore import (Qt,
                          QPoint,
                          QRect,
                          QSize,
                          pyqtSignal)


class Mode(Enum):
    MARKER = auto()
    ROI = auto()
    VIEWER = auto()


class Blackboard(QLabel):

    """ Muestra en pantalla la imagen y los puntos de coordenadas de las
    plantas. También permite marcar y desmarcar los puntos, y marcar con un
    rectangulo un grupo de plantas mostrando su cantidad
    """

    ROI_selected = pyqtSignal(QRect, list)
    points_marked = pyqtSignal(int)

    def __init__(self, circle_rad=6, circle_width=3, circle_color='blue',
                 line_width=3, line_color='green',
                 rect_font_size=10, rect_width=3, rect_color='red'):
        super().__init__()
        self.mode = Mode.VIEWER
        self.circle_rad = circle_rad
        self.circle_width = circle_width
        self.circle_color = circle_color
        self.line_width = line_width
        self.line_color = line_color
        self.rect_width = rect_width
        self.rect_color = rect_color
        self.rect_font_size = rect_font_size
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.ROI_origin = None
        self.setFrameStyle(QFrame.NoFrame)

    def mousePressEvent(self, event):
        if self.pixmap() and event.button() == Qt.LeftButton:
            if self.mode == Mode.MARKER:
                point = QPoint(event.pos()) / self.zoom
                [x,y] = [point.x(), point.y()]
                if not any(map(lambda c: (c.x()-x)**2 + (c.y()-y)**2 <
                                         (2*self.circle_rad)**2,
                               self.points)): # si se puede agregar un punto
                    self.__addPoint(point)
                else:
                    self.__removeMark(point)
            elif self.mode == Mode.ROI:
                self.ROI_origin = QPoint(event.pos())
                self.rubberBand.setGeometry(QRect(self.ROI_origin, QSize()))
                self.rubberBand.show()
        QLabel.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if not (self.ROI_origin is None):
            self.rubberBand.setGeometry(QRect(self.ROI_origin,
                                              event.pos()).normalized())
        QLabel.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.pixmap() and event.button() == Qt.LeftButton:
            if self.ROI_origin:
                self.rubberBand.hide()
                end = QPoint(event.pos())
                if end.x() < 0: end.setX(0)
                if end.y() < 0: end.setY(0)
                if end.x() > self.width(): end.setX(self.width())
                if end.y() > self.height(): end.setY(self.height())
                ROI = QRect(self.ROI_origin / self.zoom,
                            end / self.zoom).normalized()
                self.ROI_origin = None
                if ROI.width() > 20 and ROI.height() > 20:
                    points = list(filter(ROI.contains, self.points))
                    self.ROI_selected.emit(ROI, points)
        QLabel.mouseReleaseEvent(self, event)

    def setImage(self, image):

        """ Resetea los paramentros y fija la imagen
        """
        self.image = image
        self.image_to_draw = image.copy()
        self.zoom = 1
        self.points = []
        self.lines = []
        self.rectangles = []
        self.__update()
        self.points_marked.emit(len(self.points))

    def changeImage(self, image):

        """ Cambia la imagen
        """
        self.image = image
        self.image_to_draw = self.image.scaledToHeight(
            self.image.height() * self.zoom)
        self.__update()

    def setPoints(self, points):

        """ Fija la lista de puntos
        """
        self.points = points
        self.__update()
        self.points_marked.emit(len(self.points))

    def getPoints(self):

        """ Obtiene la lista de puntos
        """
        return self.points

    def addRectangles(self, rectangles):

        """ Agrega rectangulos con la cantidad de plantas
        """
        self.rectangles.extend(rectangles)
        self.__update()

    def addLines(self, lines):

        """ Agrega lineas
        """
        self.lines.extend(lines)
        self.__update()

    def zoomIn(self):

        """ Agranda la imagen
        """
        height = self.image.height() * self.zoom * 2
        image = self.image.scaledToHeight(height)
        if not image.isNull():
            self.zoom = self.zoom * 2
            self.image_to_draw = image
            self.__update()

    def zoomOut(self):

        """ Achica la imagen
        """
        if self.zoom > 0.10:
            height = self.image.height() * self.zoom / 2
            image = self.image.scaledToHeight(height)
            self.zoom = self.zoom / 2
            self.image_to_draw = image
            self.__update()

    def getPixmap(self):
        return self.pixmap()

    def __addPoint(self, point):
        self.points.append(point)
        self.__drawMarks([point])
        self.points_marked.emit(len(self.points))

    def __removeMark(self, point):
        [x,y] = [point.x(), point.y()]
        remove = list(filter(lambda c: (c.x()-x)**2 + (c.y()-y)**2 <=
                                       self.circle_rad**2,
                             self.points))
        if len(remove) == 1:
            self.points.remove(remove[0])
            self.__update()
            self.points_marked.emit(len(self.points))

    def __drawMarks(self, points):
        painter = QPainter(self.pixmap())
        pen = QPen()
        pen.setWidth(self.circle_width)
        pen.setColor(QColor(self.circle_color))
        painter.setPen(pen)
        for p in points:
            p2 = QPoint(p.x() * self.zoom, p.y() * self.zoom)
            radius = self.circle_rad * self.zoom
            painter.drawEllipse(p2, radius, radius)
        painter.end()
        self.update()

    def __drawLines(self, lines):
        painter = QPainter(self.pixmap())
        pen = QPen()
        pen.setWidth(self.line_width)
        pen.setColor(QColor(self.line_color))
        painter.setPen(pen)
        lines = [list(map(lambda x: x * self.zoom, l)) for l in lines]
        for l in lines:
            painter.drawLine(l[0],l[1],l[2],l[3])
        painter.end()
        self.update()

    def __drawRectangles(self, rectangles):
        painter = QPainter(self.pixmap())
        pen = QPen()
        pen.setWidth(self.rect_width)
        pen.setColor(QColor(self.rect_color))
        painter.setPen(pen)
        font = painter.font()
        font.setPointSize(self.rect_font_size * self.zoom)
        painter.setFont(font)
        for (r,n) in rectangles:
            r2 = QRect(*[x * self.zoom for x in r])
            painter.drawRect(r2)
            if r2.y() - self.rect_font_size - self.rect_width > 0:
                # dibujo el número arriba a la derecha
                p = QPoint(r2.x() + r2.width() - 2*self.rect_font_size,
                           r2.y() - self.rect_width)
            else:
                # dibujo el número abajo a la izquierda
                p = QPoint(r2.x(),
                           r2.y() + r2.height() + self.rect_font_size
                           + self.rect_width)
            painter.drawText(p, str(n))
        painter.end()
        self.update()

    def __update(self):
        self.setPixmap(self.image_to_draw)
        self.resize(self.image_to_draw.width(), self.image_to_draw.height())
        self.__drawMarks(self.points)
        self.__drawLines(self.lines)
        self.__drawRectangles(self.rectangles)
        self.update()
