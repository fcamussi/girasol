#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Tue Aug 25 20:14:29 2020
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

""" Morfología """

import numpy as np
import cv2 as cv


def morphology(mask, ppm):
    """ Aplica operaciones morfológicas de apertura, remoción y relleno
    a la máscara

    Argumentos:
        mask -- máscara a la que se le aplican las operaciones

    Retorna: máscara con operaciones aplicadas
    """

    # Apertura
    kernel = cv.getStructuringElement(shape=cv.MORPH_ELLIPSE, ksize=(5,5))
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

    # Remueve objetos pequeños y rellena agujeros
    U = (ppm/20)**2
    contours,_ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    contours = list(filter(lambda a: cv.contourArea(a) > U, contours))
    mask2 = np.zeros(mask.shape, np.uint8)
    cv.drawContours(mask2, contours, -1, 255, cv.FILLED)

    return mask2
