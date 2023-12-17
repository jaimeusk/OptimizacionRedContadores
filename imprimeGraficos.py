# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 17:25:08 2023

@author: jaime
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


#%% Funciones para la creación de gráficos

def crea_grafico(figure):
    """
    Crea un gráfico dado un número de figura. Se usa para que todos sean iguales
    """
    plt.figure(figure)
    plt.figure(figsize=(10, 8),dpi=150)
    
    

    
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
    
 

       
def pintar_dispositivos(numFigura, concentradores, routers, terminales):
    '''
    Pinta grafica con todos los dispositivos en un plano.
    
    Argumentos:
    - numFigura (int): número de figura.
    - concentradores (list): Lista que contiene todos los concentradores
    - routers (list): Lista que coniene los routers
    - terminales (list): Lista que contiene todos los terminales.
    
    Devuelve:
        Nada
    '''
    
    crea_grafico(numFigura)
    pintar_plano(concentradores, 'blue', 'Concentradores', marcador='o')
    pintar_plano(routers, 'green', 'Routers',marcador='s')
    pintar_plano(terminales, 'red', 'Terminales',marcador='*')
    
    # Creamos una leyenda para el gráfico
    concentrador_patch = mpatches.Patch(color='green', 
                                        label='Concentradores (Candidatos)')
    router_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
    terminal_patch = mpatches.Patch(color='red', label='Terminales')
    plt.legend(handles=[concentrador_patch, router_patch, terminal_patch])


    # Configuraciones del gráfico
    configurar_grafico("Terminales y ubicaciones candidatas de routers " +
                       "y concentradores")
    
    
    

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
    
    

    
#%% Pintamos routers en rango de un terminal de ejemplo para ver candidatos
def pintar_dispositivos_en_rango(numFigura, indiceDispositivo, conn_c_D1_D2,
                                 distanciaMax = 0):

    crea_grafico(numFigura)
    
    indiceDispositivo = indiceDispositivo - 1
    
    dispositivoReferencia = conn_c_D1_D2[indiceDispositivo]["Referencia"]
    dispositivosCompatibles = conn_c_D1_D2[indiceDispositivo]["Vecinos"]
    
    # Si distancia máxima es 0, es que es un dispositivo distinto a un 
    # terminal y necesita que se le pase por parámetros. En caso contrario
    # lo lee del 4º campo de dispositivoReferencia (Terminal)
    if distanciaMax == 0:
        distanciaMax = dispositivoReferencia[3]
    
    nombreDispositivo = str(dispositivoReferencia[0])
    print(dispositivosCompatibles[0][0])
    
    
    if nombreDispositivo.startswith('R'):
        tipoDisp = "Router"
        
        if dispositivosCompatibles[0][0].startswith('R'):
            nomDisps = "routers"
            D_compatibles_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
        elif dispositivosCompatibles[0][0].startswith('C'):
            nomDisps = "concentradores"
            D_compatibles_patch = mpatches.Patch(color='blue', label='Concentradores (Candidatos)')
        
        
        D_ref_patch = mpatches.Patch(color='red', label=tipoDisp)
        
        
    
    elif nombreDispositivo.startswith('T'):
        tipoDisp = "Terminal"
        nomDisps = "routers"
        D_compatibles_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
        D_ref_patch = mpatches.Patch(color='red', label=tipoDisp)
    
    
    
    
    
    # Pintamos gráfica con dispositivos
    pintar_plano(dispositivosCompatibles, 'blue', tipoDisp, marcador='o')    
    pintar_nodo_rango(dispositivoReferencia, distanciaMax)
    
    
    plt.legend(handles=[D_compatibles_patch, D_ref_patch])
    
    configurar_grafico("Ubicaciones " + nomDisps + " candidatos para " + 
                       "conectarse con " + str(nombreDispositivo))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    