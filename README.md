# Girasol

Aplicación para el conteo de plantas de girasol en cultivos en hileras a partir de imágenes UAV.

El conteo de plantas de girasol se realiza mediante modelos de regresión a partir de descriptores de forma y tamaño sobre los objetos que son segmentados como plantas. Los modelos se generan a partir del entrenamiento de conjuntos de puntos marcados sobre los centros de las plantas y son realizados desde la misma aplicación.

Ésta aplicación implementa el resultado de mi trabajo de investigación durante el desarrollo de mi tesina de grado *"Conteo de plantas de girasol en cultivos en hileras a partir de imágenes UAV"*, en la cual se proponen cuatro algoritmos para el conteo:

* Segmentación de la imagen, para separar las plantas de girasol del fondo.
* Detección de la orientación de las hileras, para rotar la imagen de manera que las hileras queden de forma horizontal.
* Detección de hileras y etiquetado de objetos de plantas de girasol a las mismas.
* Estimación de la cantidad de plantas de girasol mediante métodos de regresión.

Si bien durante el trabajo se probaron diferentes métodos de regresión: Modelo lineal multivariado con mínimos cuadrados, regresión Ridge, Lasso, y SVR (Regresión de Vectores Soporte) lineal. En ésta aplicación sólo se implementó el Modelo lineal multivariado con mínimos cuadrados, el cual obtuvo un R^2 0.96 en la etapa de testeo.

## Capturas

![screenshot1](https://user-images.githubusercontent.com/75378876/176992989-09f57342-1a8d-42a3-9367-551aa8e23258.png)

![screenshot2](https://user-images.githubusercontent.com/75378876/176992992-e0fbc3d9-0dec-40bb-a94d-3574d7844a22.png)

![screenshot3](https://user-images.githubusercontent.com/75378876/176992993-514854b1-94a8-4b17-bf1c-8b2aac9d39cc.png)

## Características de la aplicación

* Detección y corrección de la orientación de la imagen
* Detección de cada hilera
* Estimación de la cantidad de plantas
* Zoom y ROI (región de interés)
* Creación de conjuntos de puntos marcados
* Entrenamiento de nuevos modelos

## Requisitos

* Python >= 3.8.8
* PyQt5 >= 5.12.3
* OpenCV >= 4.5.2
* pandas >= 1.3.5
* scikit-learn >= 1.0.2
* PIL >= 8.4.0
* SciPy >= 1.7.3

## Ejecución

```
python main.py
```
