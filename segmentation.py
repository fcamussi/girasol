#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Sun Aug  9 02:26:37 2020
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

""" Segmentación """

import cv2 as cv


def segmentation(image):
    """ Segmenta la imagen

    Argumentos:
        image -- imagen

    Retorna: máscara obtenida
    """
    R = image[:,:,2]
    G = image[:,:,1]
    B = image[:,:,0]

    R = R.astype(int)
    G = G.astype(int)
    B = B.astype(int)

    ExG = 2*G-R-B
    ExG[ExG>255] = 255
    ExG[ExG<0] = 0

    ExG = ExG.astype('uint8')

    _,mask = cv.threshold(ExG, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    return mask