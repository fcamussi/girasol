# Conteo de plantas de girasol

Aplicación para el conteo de plantas de girasol en cultivos en hileras a partir de imágenes UAV.

El conteo de plantas de girasol se realiza mediante modelos de regresión a partir de descriptores de forma y tamaño sobre los objetos que son segmentados como plantas. Los modelos se generan a partir del entrenamiento de conjuntos de puntos marcados sobre los centros de las plantas.

Ésta aplicación implementa parte de mi trabajo de investigación durante el desarrollo de mi tesina de grado *"Conteo de plantas de girasol en cultivos en hileras a partir de imágenes UAV"* la cuál combina técnicas de Procesamiento Digital de Imágenes con Machine Learning y en la cual se proponen cuatro algoritmos esenciales para el conteo:

* Segmentación de la imagen, para separar las plantas de girasol del fondo.
* Detección de la orientación de las hileras, para rotar la imagen de manera que las hileras queden de forma horizontal.
* Detección de hileras y etiquetado de objetos de plantas de girasol a las mismas.
* Estimación de la cantidad de plantas de girasol mediante métodos de regresión.

Si bien durante el trabajo se probaron diferentes métodos de regresión: Modelo lineal multivariado con mínimos cuadrados, regresión Ridge, Lasso, y SVR (Regresión de Vectores Soporte) lineal. En ésta aplicación sólo se implementó el Modelo lineal multivariado con mínimos cuadrados, el cual obtuvo un R^2 de 0.96 en la etapa de testeo.

## Capturas

![screenshot1](https://user-images.githubusercontent.com/75378876/187995752-0a5a7c6e-0e21-47ce-814e-cafa629a444d.png)

![screenshot2](https://user-images.githubusercontent.com/75378876/187995764-ed08b946-d371-41e9-8180-5f5a03db4f79.png)

![screenshot3](https://user-images.githubusercontent.com/75378876/187995770-99027a5e-ee71-4993-861f-3751acb4cc66.png)

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

Para su ejecución sugiero instalar la plataforma de Data Science, Anaconda.

Una vez instalada se recomienda actualizar todos los paquetes a la última versión ejecutando:

```
conda update --prefix $CONDA_DIR anaconda
```

donde $CONDA_DIR es el directorio donde fue instalada.

Luego instalar la librería OpenCV ejecutando:

```
conda install -c conda-forge opencv
```

Y dado que por defecto Anaconda ya trae el resto de las dependencias, para ejecutar la aplicación sólo basta con ejecutar:

```
python main.py
```
