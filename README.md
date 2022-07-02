# conteo-girasol

Aplicación para el conteo de plantas de girasol en cultivos en hileras a partir de imágenes UAV.

El conteo de plantas de girasol se realiza mediante modelos de regresión a partir de descriptores de forma y tamaño sobre los objetos que son segmentados como plantas. Los modelos de predicción se generan a partir del entrenamiento de conjuntos de puntos marcados sobre los centros de las plantas, que se realizan desde la misma aplicación.

## Capturas

![screenshot1](https://user-images.githubusercontent.com/75378876/176986446-b894df29-db65-4c27-9a5c-f9be1cf801aa.png)

![screenshot2](https://user-images.githubusercontent.com/75378876/176986449-479e3feb-9b25-4efa-b0ec-7543ccdcd853.png)

![screenshot3](https://user-images.githubusercontent.com/75378876/176986451-da5a1398-7c3c-49f9-be13-571aad8ab11a.png)

![screenshot4](https://user-images.githubusercontent.com/75378876/176986452-cba227e9-190c-4684-bbb3-036bc742bff8.png)

## Características

* Detección y corrección de la orientación de las hileras
* Detección de cada hilera
* Estimación de la cantidad de plantas.
* Zoom y ROI (región de interés) para trabajar más cómodo
* Generar conjuntos de puntos marcados
* Entrenar nuevos modelos
* Exportar imagen con las plantas detectadas

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
