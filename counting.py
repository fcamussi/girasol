#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Sun Nov 29 11:24:09 2020
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

""" Conteo de plantas """

from rows_detection import rows_detection
from descriptors import Descriptors
from model import Model
import cv2 as cv


def counting(mask, model_file, ppm):
    """ Aplica el modelo para predecir la cantidad de plantas que hay en
        la máscara

    Argumentos:
        mask -- máscara
        model_file -- nombre del fichero del modelo

    Retorna: total de plantas, lista de rectángulos con la cantidad de plantas
        que hay en el mismo, total de hileras, y lineas de las hileras
    """

    model = Model.load(model_file)
    contours,total_rows,lines = rows_detection(mask, ppm)
    if len(contours) > 0:
        n_plants = Model.apply(model, Descriptors.compute(contours, ppm))
        total_plants = round(sum(n_plants))
        rects = [(cv.boundingRect(cnt),'%.1f' % n_plants[j])
                    for j,cnt in enumerate(contours) if n_plants[j] > 0]
    return (total_plants,rects,total_rows,lines)
