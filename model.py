#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Wed Nov 25 11:17:21 2020
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

""" Modelo """

import pickle
from sklearn import linear_model
from sklearn.metrics import r2_score
import numpy as np
from sklearn.preprocessing import StandardScaler


class Model():
    """ Clase no instanciable """

    def generate(df):
        """ Genera un modelo de regresion lineal a partir de los
        datos.

        Argumentos:
            df -- dataframe con los datos

        Retorna: modelo generado e información
        """
        data = df.values
        X = data[:,:-1]
        y = data[:,-1]
        stsc_X = StandardScaler()
        stsc_y = StandardScaler()
        X = stsc_X.fit_transform(X)
        y = stsc_y.fit_transform(y.reshape(-1,1)).flatten()
        lr = linear_model.LinearRegression()
        lr.fit(X, y)
        y_pred = lr.predict(X)
        r2 = r2_score(y, y_pred)
        model = dict(lr=lr, stsc_X=stsc_X, stsc_y=stsc_y)
        info = dict(R2=r2)
        return (model,info)

    def apply(model, df):
        """ Aplica el modelo

        Argumentos:
            model -- modelo a aplicar
            df -- dataframe con los datos

        Retorna: array con las predicciones
        """
        X = df.values
        X = model['stsc_X'].transform(X)
        y = model['lr'].predict(X)
        y = model['stsc_y'].inverse_transform(y.reshape(-1,1))[:,0]
        return y

    def save(model_file, model):
        """ Guarda el modelo en un fichero

        Argumentos:
            model_file -- nombre del fichero donde se guarda
            model -- modelo a guardar
        """
        pickle.dump(model, open(model_file, 'wb'))

    def load(model_file):
        """ Carga un modelo desde un fichero

        Argumentos:
            model_file -- nombre del fichero a cargar

        Retorna: modelo cargado
        """
        return pickle.load(open(model_file, 'rb'))
