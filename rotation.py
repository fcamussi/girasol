#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on Fri Oct 30 03:42:57 2020
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

""" Rotación """

import numpy as np
from PIL import Image


def rotation(image, angle):
    """ Rota una imagen en sentido anti-horario

    Argumentos:
        image -- imagen a rotar
        angle -- ángulo de rotación en grados

    Retorna: imagen rotada
    """
    image = Image.fromarray(image)
    image = image.rotate(angle, Image.BICUBIC, expand=True)
    image = np.asarray(image)
    return image
