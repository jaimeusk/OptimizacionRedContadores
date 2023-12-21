# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 16:55:52 2023

@author: jaime
"""

import math
import pandas as pd
from tabulate import tabulate


def leerDatos (hoja,x1, y1, x2, y2, orientacion):
    '''
    Lee datos de un archivo Excel en función dadas unas coordenadas y 
    una orientación de lectura.

    Argumentos:
    - x1 (int): Coordenada x inicial.
    - y1 (int): Coordenada y inicial.
    - x2 (int): Coordenada x final.
    - y2 (int): Coordenada y final.
    - orientacion (int): Orientación de extracción (0 para columnas, 1 para filas).

    Devuelve:
    - list: Lista con los datos extraídos del archivo Excel.
    '''
    
    x1=x1-1
    x2=x2-1
    y1=y1-1
    y2=y2-1
    df = pd.read_excel('Caso_HLP_2023.xlsx',sheet_name=hoja,header=None)
    i = 0
    l=[]
    if orientacion == 1:
        while (i+y1 <=y2):
            l.append(list(df.iloc[y1+i][x1:x2+1]))
            i=i+1
    if orientacion == 0:
        while (i+x1 <=x2):
            l.append(list(df[x1+i][y1:y2+1]))
            i=i+1
    return l




def dispositivos_en_rango_lista(nodos, dispositivos, distancia_maxima=0):
    '''
    Devuelve todos los dispositivos candidatos a conectarse con cada uno de los
    nodos de una lista.
    Por ejemplo, devuelve todos los routers candidatos a conectarse con cada
    uno de los routers del escenario.

    Argumentos:
    - nodos (list): Lista de nodos con coordenadas (nombre, x, y).
    - dispositivos (list(list)): Lista de dispositivos con coordenadas (nombre, x, y).
    - distancia_maxima (float): (Opcional para terminales) Distancia máxima para considerar dispositivos cercanos.

    Devuelve:
    - list: Lista de listas de dispositivos dentro del rango especificado alrededor de cada nodo.
    '''
     
    dispositivos_cercanos_por_nodo = []

    for nodo in nodos:
        # Si no pasamos un valor de distancia_maxima, usamos la distancia max
        # almacenada en el valor de cada nodo (Solo vale para terminales)
        if len(nodo) > 3:
            distancia_maxima = nodo[3]
            
        x_nodo, y_nodo = nodo[1], nodo[2]
        dispositivos_cercanos = {"Referencia":nodo, "Vecinos":[]}
        
        for dispositivo in dispositivos:
            x_dispositivo, y_dispositivo = dispositivo[1], dispositivo[2]
            distancia = math.sqrt((x_dispositivo - x_nodo)**2 + 
                                  (y_dispositivo - y_nodo)**2)
            if distancia <= distancia_maxima:
                dispositivos_cercanos["Vecinos"].append(dispositivo)

        dispositivos_cercanos_por_nodo.append(dispositivos_cercanos)

    return dispositivos_cercanos_por_nodo




def obtener_nodos_activos(dispositivosNombres, d_DISPOSITIVOS):
    """
    Obtiene los dispositivos activos a partir de sus nombres y soluciones.
    
    Parametros:
        - dispositivosNombres (list): Lista de nombres de dispositivos.
        - d_DISPOSITIVOS (dict): Diccionario de objetos de dispositivos.
    
    Devuelve:
        - list: Lista de nombres de dispositivos activos.
    """
    dispositivosSolucion = []
    
    for dispositivo in dispositivosNombres:
        d = d_DISPOSITIVOS[dispositivo]
        if d.solution_value() > 0:
            dispositivosSolucion.append(d.name())
    
    return dispositivosSolucion




def obtener_conexiones_activas(lista_conexiones):
    """
    Obtiene las conexiones activas a partir de una lista de conexiones.

    Parámetros:
        - conexiones (dict): Diccionario de conexiones a evaluar si existen.

    Returns:
        - dict: Diccionario de conexiones activas con sus valores de solución.
    """
    
    conexiones_activas = {}
    for clave, valor in lista_conexiones.items():
        if valor.solution_value() > 0:
            conexiones_activas[clave] = valor.solution_value()

    return conexiones_activas



def crea_posiciones(terminales=None, routers=None, concentradores=None,
                    routersWPANSolucion=None, routersGPRSSolucion=None,
                    concentradoresSolucion=None):
    
    posiciones = {}
    
    # Procesar terminales
    if terminales is not None:
        for terminal in terminales:
            nombreTerminal = terminal[0]
            posX, posY = terminal[1], terminal[2]
            posiciones[nombreTerminal] = [posX, posY]

    # Procesar routers si se proporcionan
    if routers is not None:
        if routersWPANSolucion is not None:
            for router in routers:
                nombreRouter = str(router[0])
                if (nombreRouter+"_WPAN") in routersWPANSolucion:
                    posX, posY = router[1], router[2]
                    posiciones[nombreRouter+"W"] = [posX, posY]

        if routersGPRSSolucion is not None:
            for router in routers:
                nombreRouter = str(router[0])
                if (nombreRouter+"_GPRS") in routersGPRSSolucion:
                    posX, posY = router[1], router[2]
                    posiciones[nombreRouter+"G"] = [posX, posY]

    # Procesar concentradores si se proporcionan
    if concentradores is not None and concentradoresSolucion is not None:
        for concentrador in concentradores:
            nombreConcentrador = str(concentrador[0])
            if nombreConcentrador in concentradoresSolucion:
                posX, posY = concentrador[1], concentrador[2]
                posiciones[nombreConcentrador] = [posX, posY]
            
    return posiciones





def crear_variable_conexion(conn_c_D1_D2, l, solver):
    '''
    Crea y devuelve un diccionario de variables de conexión para una pareja de
    dispositivos dadas sus conexiones candidatas.
    
    Esta función genera un conjunto de variables binarias para representar la
    existencia de una conexión entre dos dispositivos (D1 y D2) sean del tipo
    que sean. Cada variable indica si existe una conexión (valor 1) o no (valor
    0).

    Parámetros:
        - conn_c_D1_D2 (list of dict):  Lista de diccionarios dónde cada
                                        elemento de la lista contiene un disp.
                                        de referencia y todos los dispositivos
                                        vecinos a los que podría conectarse.
                                        
        - l (str):  Letra que identifica el tipo de variable que va a crearse.
                    (Por ejemplo W para las conexiones entre terminales y 
                     routers WPAN)
        
        - solver (Solver):  Objeto de solver de OR-Tools para la creación de 
                            variables.
                            
                            
    Devuelve: 
        - x_conexionesD1D2 (dict):  Un diccionario de variables de OR-Tools, 
                                    donde las claves son tuplas (D1, D2) 
                                    representando una posible conexión entre un 
                                    dispositivo D1 y otro D2, y los valores son
                                    las variables binarias de OR-Tools 
                                    correspondientes a estas conexiones.
    
    Ejemplo de uso: 
        w_terminales_WPAN = crear_variable_conexion(conn_c_term_rout, 'W', solver)
   '''
   
    x_conexionesD1D2 = {}

    for conexionCandidata in conn_c_D1_D2:
        D1 = str(conexionCandidata['Referencia'][0])
        for routerCandidato in conexionCandidata["Vecinos"]:
            D2 = routerCandidato[0]
            x_conexionesD1D2[(D1, D2)] = solver.IntVar(0, 1, f'{l}_{D1}->{D2}')
            
    return x_conexionesD1D2


def crear_tabla_con_enlaces(x_D1D2_Solucion):
    
    lista_tabla= [[k[0], k[1], v] for k, v in x_D1D2_Solucion.items()]
    
    # Modificamos la lista para incluir enlaces en el nombre del terminal
    lista_con_enlaces = []
    for D1, D2, valor in lista_tabla:
        # Asumiendo que las imágenes están en una carpeta llamada 'imagenes'
        enlace = f'<a href="graficosSolucion/{D1}_en_rango.jpg">{D1}</a>'
        lista_con_enlaces.append([enlace, D1, valor])

    # Creamos la tabla con formato HTML
    tabla_html = tabulate(lista_con_enlaces, headers=["Terminal", "Router", "Valor"], tablefmt="html")
    return tabla_html



