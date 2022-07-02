# Girasol

Aplicación para el conteo de plantas de girasol en cultivos en hileras a partir de imágenes UAV.

El conteo de plantas de girasol se realiza mediante modelos de regresión a partir de descriptores de forma y tamaño sobre los objetos que son segmentados como plantas. Los modelos se generan a partir del entrenamiento de conjuntos de puntos marcados sobre los centros de las plantas y son realizados desde la misma aplicación.

## Capturas

![screenshot1](https://user-images.githubusercontent.com/75378876/176992989-09f57342-1a8d-42a3-9367-551aa8e23258.png)

![screenshot2](https://user-images.githubusercontent.com/75378876/176992992-e0fbc3d9-0dec-40bb-a94d-3574d7844a22.png)

![screenshot3](https://user-images.githubusercontent.com/75378876/176992993-514854b1-94a8-4b17-bf1c-8b2aac9d39cc.png)

![screenshot4](https://user-images.githubusercontent.com/75378876/176992994-8f557fd7-aa66-40b7-920f-316ca3756911.png)

## Características

* Detección y corrección de la orientación de las hileras
* Detección de cada hilera
* Estimación de la cantidad de plantas.
* Zoom y ROI (región de interés) para trabajar más cómodo
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
