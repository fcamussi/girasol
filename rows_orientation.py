#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Wed Aug 26 18:32:28 2020
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

""" Orientación de las filas """

import cv2 as cv
import numpy as np
from scipy.signal import correlate


def rows_orientation(mask, h_crop=4000, w_crop=4000):
    """ Calcula la orientación de las hileras

    Argumentos:
        mask -- máscara de la imagen

    Retorna: orientación en grados o None en caso de error
    """

    # Si la máscara supera cierto tamaño se toma solo una parte central
    [h,w] = mask.shape
    if h_crop > h:
        h_crop = h
    if w_crop > w:
        w_crop = w
    h_s = int((h-h_crop)/2)
    w_s = int((w-w_crop)/2)
    mask = mask[h_s:h_s+h_crop,
                w_s:w_s+w_crop]

    # Auto-correlación + Otsu
    mask = cv.normalize(mask, None, 0, 1, cv.NORM_MINMAX, cv.CV_32F)
    xc = correlate(mask, mask, mode = 'full', method='fft')
    xc = cv.normalize(xc, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
    _,xc_bin = cv.threshold(xc, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    # Busco el objeto central en la autocorrelación binarizada
    [h,w] = xc_bin.shape
    center = (int(w/2), int(h/2))
    contours,_ = cv.findContours(xc_bin, cv.RETR_TREE,
                                 cv.CHAIN_APPROX_NONE)
    cnt_center = None
    for cnt in contours:
        if cv.pointPolygonTest(cnt, center , False) >= 0:
            cnt_center = cnt
    if cnt_center is not None:
        # Calculo la orientación del objeto central calculando el ángulo del
        # autovector asociado al menor autovalor en valor absoluto de la
        # matriz de covarianza C
        z = np.matrix(cnt_center[:,0,:])
        K = z.shape[0]
        z_ = np.sum(z,axis=0)/K
        C = np.sum([np.matmul((zk-z_).T,zk-z_) for zk in z],axis=0)/(K-1)
        eigval,eigvec = np.linalg.eig(C)
        v = eigvec[np.where(eigval == np.abs(eigval).max())][0]
        orientation = np.degrees(np.arctan2(v[1],v[0]))
        return orientation
    else:
        # Si no hay blob central retorno None
        return None
