# Optimización de Redes de Telegestión

Este proyecto se centra en la optimización de una red de telegestión de contadores de agua, haciendo uso de métodos de programación lineal para encontrar la solución óptima en término de costes de compra de los dispositivos. Se hace uso de OR-Tools para la resolución del problemas.

Puedes acceder al informe HTML generado en el siguiente enlace: [https://jaimeusk.github.io/OptimizacionRedContadores/](https://jaimeusk.github.io/OptimizacionRedContadores/)

## Estructura del Proyecto

El código se divide en tres ficheros principales:

- `casoFinalRefactorizado.py`: Contiene el código principal para la resolución del problema de optimización de la red de telegestión. Utiliza OR-Tools y contiene la lógica principal del proyecto.
  
- `utilidades.py`: Incluye funciones útiles para la resolución del problema y el manejo de los datos.

- `imprimeGraficos.py`: Contiene las funciones necesarias para la creación de gráficos y la interfaz HTML que muestra los resultados de la optimización.

## Librerías Necesarias

El proyecto hace uso de varias librerías de Python para su funcionamiento. Puedes instalarlas usando el archivo `requirements.txt` proporcionado. Mas abajo se indica como hacer uso del este fichero de texto.

Las librerías utilizadas son:

- matplotlib
- networkx
- pandas
- tabulate
- ortools
- os
- webbrowser
- re
- math
- time

## Instalación de Dependencias

Para instalar las dependencias necesarias, puedes usar el archivo `requirements.txt` que se incluye en el repositorio. Ejecuta el siguiente comando para instalar todas las dependencias:

pip install -r requirements.txt


## Uso del Proyecto

Para usar el proyecto, es necesario tener el archivo de datos `Caso_HLP_2023.xlsx` en la misma carpeta que los archivos de código Python. Este archivo contiene los datos descriptivos del problema.

Para ejecutar el código debes ejecutar el archivo `casoFinalRefactorizado.py`. Este script principal utilizará funciones de los otros módulos (`utilidades.py` e `imprimeGraficos.py`) por lo que necesitarás que todos los ficheros estén en la misma carpeta.

### Pasos para la Ejecución:

1. Asegúrate de tener el archivo `Caso_HLP_2023.xlsx` en la misma carpeta que los scripts de Python.
2. Ejecuta el archivo `casoFinalRefactorizado.py`.
3. El programa procesará los datos, realizará la optimización y generará los resultados en forma de gráficos y una interfaz HTML para su fácil comprensión.
