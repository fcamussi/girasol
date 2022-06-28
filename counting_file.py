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

""" Fichero de conteo """

import cv2 as cv
import os.path
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QImage, QPixmap


class CountingFile():

    """ Carga y guarda la información relacionada con el conteo """

    def __init__(self, file=None):
        self.points = []
        if file is None:
            self.file = None
            self.imageFile = None
            self.imageMask = None
            self.image = None
            self.mask = None
            self.ppm = None
        else:
            self.file = file
            f = open(self.file, 'r')
            imageFile = f.readline().rstrip()
            maskFile = f.readline().rstrip()
            ppm = int(f.readline().rstrip())
            self.imageFile = os.path.dirname(self.file) + '/' +  imageFile
            self.maskFile = os.path.dirname(self.file) + '/' +  maskFile
            self.image = cv.imread(self.imageFile, cv.IMREAD_COLOR)
            self.mask = cv.imread(self.maskFile, cv.IMREAD_GRAYSCALE)
            self.ppm = ppm
            for l in f:
                p = list(map(int, l.split(',')))
                self.points.append(QPoint(p[0],p[1]))
            f.close()

    def getFile(self):

        """ Retorna el nombre del fichero de conteo """
        return self.file

    def getImage(self):

        """ Retorna la imagen """
        return self.image

    def setImage(self, image):

        """ Fija la imagen """
        self.image = image

    def getMask(self):

        """ Retorna la máscara """
        return self.mask

    def setMask(self, mask):

        """ Fija la máscara """
        self.mask = mask

    def getPoints(self):

        """ Retorna una lista con los puntos de coordenadas de las plantas """
        return self.points

    def setPoints(self, points):

        """ Fija la lista de puntos de coordenadas de las plantas """
        self.points = points

    def getPPM(self):

        """ Retorna pixeles por metro """
        return self.ppm

    def setPPM(self, ppm):

        """ Fija pixeles por metro """
        self.ppm = ppm

    def saveFile(self, file):

        """ Guarda los puntos, la máscara y la imagen
        """
        self.file = file
        f = open(self.file, 'w')
        if self.imageFile is None:
            self.imageFile = os.path.splitext(self.file)[0] + '.image.tif'
            self.maskFile = os.path.splitext(self.file)[0] + '.mask.tif'
            cv.imwrite(self.imageFile, self.image)
            cv.imwrite(self.maskFile, self.mask)
        f.write(os.path.basename(self.imageFile) + '\n')
        f.write(os.path.basename(self.maskFile) + '\n')
        f.write(str(self.ppm) + '\n')
        for p in self.points:
            f.write(str(p.x()) + ',' + str(p.y()) + '\n')
        f.close()

    def cvImageToQPixmap(cv_image):

        """ Convierte una imagen en formato OpenCV a una imagen en formato
            QPixmap
        """
        cv_image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
        [h,w,_] = cv_image.shape
        image = QImage(cv_image.data, w, h, w*3, QImage.Format_RGB888)
        return QPixmap(image)

    def isRGB(cv_image):

        """ Retorna True si la imagen es RGB
        """
        channel_R = cv_image[:,:,2]
        channel_G = cv_image[:,:,1]
        channel_B = cv_image[:,:,0]
        return not ((channel_R == channel_G).all() and \
                    (channel_G == channel_B).all())
