# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 21:28:23 2023

@author: jaime
"""
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from tabulate import tabulate

#%% Definición de funciones utiles para el programa

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


def dispositivos_en_rango(nodo, dispositivos, distancia_maxima):
    '''
    Encuentra los dispositivos cercanos a un nodo dentro de una distancia máxima.

    Argumentos:
    - nodo (list): Coordenadas (nombre, x, y) del nodo central.
    - dispositivos (list(list)): Lista de dispositivos con coordenadas (nombre, x, y).
    - distancia_maxima (float): Distancia máxima para considerar dispositivos cercanos.

    Devuelve:
    - list: Lista de dispositivos dentro del rango especificado alrededor del nodo.
    '''
    
    x_nodo, y_nodo = nodo[1], nodo[2]
    dispositivos_cercanos = []

    for dispositivo in dispositivos:
        x_dispositivo, y_dispositivo = dispositivo[1], dispositivo[2]
        distancia = math.sqrt((x_dispositivo - x_nodo)**2 + 
                              (y_dispositivo - y_nodo)**2)
        if distancia <= distancia_maxima:
            dispositivos_cercanos.append(dispositivo)

    return dispositivos_cercanos

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

def pintar_plano(dispositivos, color, tipo, marcador='o'):
    """
    Pinta grafica dispositivos en un plano.
    
    Argumentos:
    - dispositivos (list): Lista de dispositivos con sus coordenadas.
    - color (str): Color de los dispositivos en el gráfico.
    - tipo (str): Tipo de dispositivo (para la leyenda).
    - marcador (str, opcional): Tipo de marcador ('o' por defecto para círculos).
                               Puede ser 'o' para círculos, '*' para estrellas, 's' para cuadrados, etc.
    
    Devuelve:
        Nada
    """
    
    for dispositivo in dispositivos:
        x, y = dispositivo[1], dispositivo[2]
        plt.scatter(x, y, color=color, marker=marcador)
        plt.text(x, y, dispositivo[0], fontsize=6, ha='right')
        

def pintar_nodo_rango(nodo, distanciaMax):
    """
    Función para pintar un nodo con un círculo que representa su rango máximo.

    Parametros:
        - nodoe (list): Lista que contiene las coordenadas x, y y el nombre del nodo.
        - distanciaMax (float): Valor que representa la distancia máxima del rango.

    Devuelve:
        Nada
    """
    
    x, y = nodo[1], nodo[2]
    nombre = nodo[0]
    plt.scatter(x, y, color='red', marker='*')
    plt.text(x, y, nombre, fontsize=10, ha='right')


    # Dibujar el círculo alrededor del terminal
    circulo = plt.Circle((x, y), distanciaMax, edgecolor='red', 
                         facecolor='blue',alpha=0.3)
    plt.gcf().gca().add_artist(circulo)
    

def imprimir_tabla_cortada(datos,letra):
    """
    Imprime una tabla procesada a partir de los datos dados, mostrando como máximo 3 columnas por fila.
    Si hay más de 3 columnas de datos por fila, se muestra '...' para indicar la limitación.
    
    Parámetros:
        - datos: Lista de datos para procesar y mostrar en la tabla.
        - letra: Carácter o cadena para etiquetar las columnas en la tabla.
    
    Devuelve:
        -nada
    """
    
    datos_procesados = []
    i = 0
    for fila in datos:
        if len(fila) > 3:
            fila = fila[:3] + ["..."]
        datos_procesados.append(fila)
        if i >= 5:
            datos_procesados.append(["..."] * len(fila))
            break
        i += 1
        
    
    l = str(letra)
    headers = [l+"[t][0]", l+"[t][1]", l+"[t][2]", l+"[t][.]"]
    print(tabulate(datos_procesados, headers=headers, tablefmt="grid"))
    print("\n")


           
 
def dibujar_nodos_con_texto(posiciones):
    """
    Dibuja los nodos en un gráfico con texto asociado a cada nodo.

    Parámetros:
        - posiciones (dict): Diccionario con las posiciones de los nodos activos

    Dibuja los nodos en un gráfico, asignando distintos marcadores y colores según su tipo:
        - Terminales (T): marcador '*', color rojo, tamaño 50.
        - Routers (R):
            - Routers WPAN: marcador 's', color morado, tamaño 200.
            - Routers GPRS: marcador 's', color verde, tamaño 200.
        - Concentradores (C): marcador 'o', color azul, tamaño 400.
    Agrega texto a cada nodo para identificarlo en el gráfico.
    """
    for nodo, (x, y) in posiciones.items():
        if nodo.startswith('T'):
            plt.scatter(x, y, marker='*', color='salmon', s=50, label=nodo)
            plt.text(x, y, nodo, ha='right', va='bottom', fontsize=8, color='black')
        elif nodo.startswith('R'):
            if nodo.endswith('W'):
                plt.scatter(x, y, marker='s', color='plum', s=200, label=nodo)
                plt.text(x, y, nodo, ha='right', va='bottom', fontsize=8, color='black')
            elif nodo.endswith('G'):
                plt.scatter(x, y, marker='s', color='LightGreen', s=200, label=nodo)
                plt.text(x, y, nodo, ha='right', va='bottom', fontsize=8, color='black')
        elif nodo.startswith('C'):
            plt.scatter(x, y, marker='o', color='skyblue', s=400, label=nodo) 
            plt.text(x, y, nodo, ha='right', va='bottom', fontsize=8, color='black')
        
 
    
def dibujar_conexiones(conexiones, posiciones, color, estilo):
    """
    Dibuja las conexiones entre dispositivos en un gráfico.

    Parámetros:
        - conexiones (dict): Diccionario que contiene las conexiones y sus valores.
        - posiciones (dict): Diccionario con las posiciones de los dispositivos.
        - color (str): Color de las flechas que representan las conexiones.
        - estilo (str): Estilo de línea de las flechas (p. ej., 'solid', 'dashed', 'dotted').
    
    Devuelve:
        -nada

    Las conexiones se representan con flechas que unen los dispositivos en el gráfico. 
    Los dispositivos pueden ser terminales, routers o concentradores. El nombre del 
    dispositivo puede variar dependiendo del tipo (WPAN/GPRS), y se adapta 
    automáticamente para su representación visual.

    Ejemplo de uso:
    dibujar_conexiones(conexiones_term_routersWPAN_Solucion, posiciones, 'green', 'dashed')
    """
    for conexion, valor in conexiones.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            dispositivo1, dispositivo2 = resto.split('->')
            
            # Modificar el nombre del dispositivo 2 según el tipo (WPAN/GPRS)
            if tipo == 'W':
                dispositivo2 = dispositivo2 + 'W'                
            elif tipo == 'V':
                dispositivo2 = dispositivo2 + 'G'                  
            elif tipo == 'U':
                dispositivo1 = dispositivo1 + 'W'
            elif tipo == 'R':
                dispositivo1 = dispositivo1 + 'W'  
                dispositivo2 = dispositivo2 + 'W'                  
            elif tipo == 'S':
                dispositivo1 = dispositivo1 + 'W'
                dispositivo2 = dispositivo2 + 'G'
                        
            x1, y1 = posiciones[dispositivo1][0], posiciones[dispositivo1][1]
            x2, y2 = posiciones[dispositivo2][0], posiciones[dispositivo2][1]
            
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                            arrowstyle='->', color=color, linestyle=estilo))
            
def configurar_grafico(titulo="",tight_layout = 1):
    """
    Configura el gráfico con los parámetros especificados.
    
    Parámetros:
        - titulo (string): Contiene el título del gráfico.
        - tight_layout (int): 1 ó 0. Evita el mensaje de error en nxgraph
    """
    plt.gca().set_aspect('equal', adjustable='box')  # Eje x e y proporcionales
    plt.title(titulo)
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.xlim(-110, 110)
    plt.ylim(-110, 110)
    plt.grid(True)
    if tight_layout:
        plt.tight_layout()
        
def crea_grafico(figure):
    """
    Crea un gráfico dado un número de figura. Se usa para que todos sean iguales
    """
    plt.figure(figure)
    plt.figure(figsize=(10, 8),dpi=150)
    

def agrupar_conexiones(conexiones):
    """
    Agrupa las conexiones en un diccionario. Agrupando todas las conexiones
    que recibe un dispositivo en cada entrada.

    Parametros:
        - conexiones (list): Lista de conexiones a agrupar.

    Devuelve:
        - dict: Diccionario que contiene las conexiones agrupadas.
    """
    conexiones_agrupadas = {}

    for lista_conexiones in conexiones:
        for conexionCandidata in lista_conexiones:
            for nodo, valorConexion in conexionCandidata.items():
                if nodo in conexiones_agrupadas:
                    conexiones_agrupadas[nodo].append(valorConexion)
                else:
                    conexiones_agrupadas[nodo] = []
                    conexiones_agrupadas[nodo].append(valorConexion)

    return conexiones_agrupadas

def reorganiza_dict(original_dict):
    """
    Reagrupa las conexiones de manera inversa. Si recibe un diccionario que 
    tiene las conexiones agrupadas por dispositivo de salida, devuelve un 
    diccionario que tiene las conexiones agrupadas por dispositivo de entrada

    Parametros:
        - conexiones (list): Lista de conexiones a agrupar.

    Devuelve:
        - dict: Diccionario que contiene las conexiones agrupadas.

    """
    new_dict = {}
    for k1, inner_dict in original_dict.items():
        for k2, value in inner_dict.items():
            if k2 not in new_dict:
                new_dict[k2] = {k1: value}
            else:
                new_dict[k2][k1] = value
    return new_dict



    

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
        - conexiones (list): Lista de conexiones a evaluar.

    Returns:
        - dict: Diccionario de conexiones activas con sus valores de solución.
    """
    conexiones_activas = {}
    for conexion in lista_conexiones:
        for conn in conexion:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                conexiones_activas[c.name()] = c.solution_value()

    return conexiones_activas



def generar_diccionario_variables_conn(conexiones_candidatas_nodoOrigen_nodoDestino,
                                  solver):
    """
    Genera un diccionario de conexiones entre nodos de origen y destino 
    utilizando un solucionador (solver).
    
    Parámetros:
        - conexiones_candidatas_nodoOrigen_nodoDestino (list): Lista de 
                        conexiones candidatas entre nodos de origen y destino.
        - solver: Solucionador utilizado para crear las variables de conexión.
    
    Devuelve:
        - x_conexionesNodoOrigenToNodoDestino (dict): Diccionario que 
                    representa las conexiones entre nodos de origen y destino.
    """
    x_conexionesNodoOrigenToNodoDestino = {}
    
    for conexionCandidata in conexiones_candidatas_nodoOrigen_nodoDestino:
        x_aux = {}
        for nodoCandidato in conexionCandidata["Vecinos"]:
            origen = str(conexionCandidata['Referencia'][0])
            candidatoD = nodoCandidato[0]
            variable_x = solver.IntVar(0, 1, 'W_' + origen + '->' + candidatoD)
            x_aux[str(candidatoD)] = variable_x
            print(x_aux.items())
            print(x_aux.values())
            
        x_conexionesNodoOrigenToNodoDestino[str(origen)] = x_aux
        
        '''
        
        w_aux = {}
        for routerCandidato in conexionCandidata["Vecinos"]:
            t = str(conexionCandidata['Referencia'][0])
            r = routerCandidato[0]
            variable_w = solver.IntVar(0, 1, 'W_' + t + '->' + r)
            w_aux[str(r)] = variable_w
        
        w_conexionesTerminalesRouterWPAN[str(i)] = w_aux
        '''
    
    return x_conexionesNodoOrigenToNodoDestino

   
    
