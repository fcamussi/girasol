#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Mon Sep 28 06:38:50 2020
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

""" Descriptores """

import cv2 as cv
import numpy as np
import pandas as pd
import math


class Descriptors():

    """ Clase no instanciable """

    def compute(contours, ppm, points=None):
        """ Calcula los descriptores para cada contorno

        Argumentos:
            contours -- lista de contornos
            points -- puntos con las coordenadas de las plantas

            si puntos es None se calcula para todos los contornos, sino se
            calcula para los contornos donde hay algún punto y se agrega la
            cantidad de puntos como última columna

        Retorna: dataframe con los datos
        """
        descr_list = []
        if points is None:
            for cnt in contours:
                descr_vector = __class__.__vector(cnt, ppm)
                descr_list.append(descr_vector)
            df = pd.DataFrame(descr_list, columns = __class__.__header[:-1])
        else:
            n_plants = lambda cnt: sum(map(lambda p:
                                           cv.pointPolygonTest(
                                               cnt, (p.x(),p.y()), False) >= 0,
                                           points))
            for i,cnt in enumerate(contours):
                n = n_plants(cnt)
                if n > 0:
                    descr_vector = __class__.__vector(cnt, ppm)
                    descr_vector.append(n)
                    descr_list.append(descr_vector)
            df = pd.DataFrame(descr_list, columns = __class__.__header)
        return df

    def load(descr_files):
        """ Carga descriptores a partir de varios ficheros omitiendo la primer
        fila de cada uno (encabezados)

        Argumentos:
            descr_files -- lista de nombres de ficheros de descriptores

        Retorna: array con los datos
        """
        df = pd.concat(map(pd.read_csv, descr_files))
        return df

    def save(descr_file, df):
        """ Guarda un dataframe en un fichero

        Argumentos:
            descr_files -- nombre del fichero donde se guarda
        """
        df.to_csv(descr_file, index = False)


    __header = ['AREA_M',
                'AREA_BB_M',
                'PERIMETRO_M',
                'PERIMETRO_BB_M',
                'COMPACIDAD',
                'EXCENTRICIDAD',
                'RELACION_ASPECTO_BB',
                'EXTENT',
                'CONVEXIDAD',
                'SOLIDEZ',
                'CANTIDAD_PLANTAS']
                
    def __descr_eccentricity(contour):
        z = np.matrix(contour[:,0,:])
        K = z.shape[0]
        z_ = np.sum(z,axis=0)/K
        C = np.sum([np.matmul((zk-z_).T,zk-z_) for zk in z],axis=0)/(K-1)
        eigval,_ = np.linalg.eig(C)
        return math.sqrt(1-(min(eigval)/max(eigval))**2)       

    def __vector(contour, ppm):
        _,_,w,h = cv.boundingRect(contour)
        bb_area = w*h
        area = cv.contourArea(contour)
        perimeter = cv.arcLength(contour, True)
        hull = cv.convexHull(contour)
        hull_area = cv.contourArea(hull)
        hull_perimeter = cv.arcLength(hull, True)

        # 1 - Área en m^2
        area_m = area / ppm**2
        # 2 - Área del bounding box en m^2
        area_bb_m = bb_area / ppm**2
        # 3 - Perímetro en m
        perimeter_m = perimeter / ppm
        # 4 - Perímetro del bounding box en m
        perimeter_bb_m = (2*w+2*h) / ppm
        # 5 - Compacidad
        compactness = perimeter**2 / area
        # 6 - Excentricidad
        eccentricity = __class__.__descr_eccentricity(contour)
        # 7 - Relación de aspecto del bounding box
        aspect_ratio_bb = w/h
        # 8 - Extent
        extent = area / bb_area
        # 9 - Convexidad
        convexity = hull_perimeter / perimeter
        # 10 - Solidez
        solidity = area / hull_area

        return [area_m,
                area_bb_m,
                perimeter_m,
                perimeter_bb_m,
                compactness,
                eccentricity,
                aspect_ratio_bb,
                extent,
                convexity,
                solidity]
