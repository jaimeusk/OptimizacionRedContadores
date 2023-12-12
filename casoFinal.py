# -*- coding: utf-8 -*-
"""
Caso final IO

Created on Fri Dec  1 11:07:33 2023

@author: jaime
"""

import pandas as pd
from ortools.linear_solver import pywraplp
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from tabulate import tabulate
import math

print("\nInicio ejecución\n")
plt.close('All')


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
    

#%% Leemos los datos provenientes de la hoja excel
'''
terminales = leerDatos('Terminales',1, 2, 4, 161, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,281,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,25,1)
'''


# Leemos menos datos para validar el modelo con menor coste computacional
terminales = leerDatos('Terminales',1, 2, 4, 10, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,20,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,10,1)




distMaxTerm = leerDatos('Distancias_Máximas',2,2,4,2,1)[0]
distMaxRout = leerDatos('Distancias_Máximas',2,3,2,3,1)[0][0]
distMaxConc = leerDatos('Distancias_Máximas',2,4,2,4,1)[0][0]

capacidadMaxWPAN = leerDatos('Capacidad_y_Coste',2,2,2,2,1)[0][0]
capacidadMaxGPRS = leerDatos('Capacidad_y_Coste',2,3,2,3,1)[0][0]
capacidadMaxConcentradores = leerDatos('Capacidad_y_Coste',2,4,2,4,1)[0][0]

costeWPAN = leerDatos('Capacidad_y_Coste',3,2,3,2,1)[0][0]
costeGPRS = leerDatos('Capacidad_y_Coste',3,3,3,3,1)[0][0]
costeConcentrador = leerDatos('Capacidad_y_Coste',3,4,3,4,1)[0][0]
# Cambiamos el valor "Tipo de terminal" por su distancia máxima
for terminal in terminales:
    terminal[3] = distMaxTerm[terminal[3]-1]


#%% Imprimimos un plano con todos los dispositivos, para hacernos una 
#   idea previa de la configuración del escenario.
plt.figure(1)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)


# Pintamos en la gráfica los 3 tipos de terminales
pintar_plano(concentradores, 'green', 'Concentradores', marcador='s')
pintar_plano(routers, 'blue', 'Routers',marcador='o')
pintar_plano(terminales, 'red', 'Terminales',marcador='*')


# Creamos una leyenda para el gráfico
concentrador_patch = mpatches.Patch(color='green', label='Concentradores (Candidatos)')
router_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_patch = mpatches.Patch(color='red', label='Terminales')
plt.legend(handles=[concentrador_patch, router_patch, terminal_patch])


# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Ubicaciones candidatas de Dispositivos')
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()



#%% Obtenemos todas las conexiones candidatas entre dispositivos
conn_c_term_rout = dispositivos_en_rango_lista(terminales, routers)
conn_c_rout_rout = dispositivos_en_rango_lista(routers, routers, distMaxRout)
conn_c_rout_conc = dispositivos_en_rango_lista(routers, concentradores, distMaxConc)


#%% Pintamos gráficos de ejemplo de conexiones candidatas.
    

#%% Pintamos routers en rango de un terminal de ejemplo para ver candidatos
indiceEjemplo = 0

terminalEjemplo = conn_c_term_rout[indiceEjemplo]["Referencia"]
distanciaMaxEjemplo = terminalEjemplo[3]
nombreTerminalEjemplo = str(terminalEjemplo[0])
routersCompatiblesEjemplo = conn_c_term_rout[indiceEjemplo]["Vecinos"]

plt.figure(2)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)

# Pintamos gráfica con dispositivos
pintar_plano(routersCompatiblesEjemplo, 'blue', 'Routers',marcador='o')

pintar_nodo_rango(terminalEjemplo, distanciaMaxEjemplo)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_evaluado_patch = mpatches.Patch(color='red', label='Terminal')
plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])

# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Ubicaciones routers candidatas para conectarse con '+ nombreTerminalEjemplo)
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()


#%% Pintamos routers en rango de un router de ejemplo para ver candidatos
indiceEjemplo = 7

routerEjemplo = conn_c_rout_rout[indiceEjemplo]["Referencia"]
nombreRouterEjemplo = str(routerEjemplo[0])
routersCompatiblesEjemplo = conn_c_rout_rout[indiceEjemplo]["Vecinos"]

plt.figure(3)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)


# Pintamos gráfica con dispositivos
pintar_plano(routersCompatiblesEjemplo, 'blue', 'Routers',marcador='o')

pintar_nodo_rango(routerEjemplo, distMaxRout)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_evaluado_patch = mpatches.Patch(color='red', label='Router referencia')
plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])

# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Ubicaciones routers candidatas para conectarse con router '+ nombreRouterEjemplo)
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()



#%% Pintamos concentradores en rango de un router de ejemplo
indiceEjemplo = 10

routerEjemplo = conn_c_rout_conc[indiceEjemplo]["Referencia"]
nombreRouterEjemplo = str(routerEjemplo[0])
concentradoresCompatiblesEjemplo = conn_c_rout_conc[indiceEjemplo]["Vecinos"]

plt.figure(4)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)


# Pintamos gráfica con dispositivos
pintar_plano(concentradoresCompatiblesEjemplo, 'green', 'Routers',marcador='s')

pintar_nodo_rango(routerEjemplo, distMaxConc)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='green', label='Concentradores (Candidatos)')
terminal_evaluado_patch = mpatches.Patch(color='red', label='Router referencia')
plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])

# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Ubicaciones concentradores candidatas para conectarse con router '+ nombreRouterEjemplo)
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()


#%% Definimos el modelo
solver = pywraplp.Solver.CreateSolver('SCIP')



# Creamos las variables de conexión terminales-router WPAN
# Solamente crearemos las fisicamente posibles para cada terminal
w_conexionesTerminalesRouterWPAN = []

for conexionCandidata in conn_c_term_rout:
    w_aux = []
    for routerCandidato in conexionCandidata["Vecinos"]:
        t = str(conexionCandidata['Referencia'][0])
        r = routerCandidato[0]
        variable_w = solver.IntVar(0,1,'W_'+t+'->'+r)
        w_aux.append({str(r):variable_w})
        
    w_conexionesTerminalesRouterWPAN.append(w_aux)


print("\nDefiniendo variables conexión terminal -> routers WPAN:\n")
print("La estructura es la siguiente:")
print(" - Cada fila contiene las conexiones candidatas de un terminal con todos" + 
      " los routers a su alcance.")
print(" - La referencia {Rxx : W_yy->R_xx} sirve para posteriormente recuperar" + 
      " las conexiones de un router con todos los terminales haciendo uso de" +
      " la referencia R_xx\n")

imprimir_tabla_cortada(w_conexionesTerminalesRouterWPAN,"W")



# Creamos las variables de conexión terminales-router GPRS
# Solamente crearemos las fisicamente posibles para cada terminal
v_conexionesTerminalesRouterGPRS = []

print("\nDefiniendo variables conexión terminal -> routers GPRS:\n")
for conexionCandidata in conn_c_term_rout:
    v_aux = []
    for routerCandidato in conexionCandidata["Vecinos"]:    
        t = str(conexionCandidata['Referencia'][0])
        r = routerCandidato[0]
        variable_v = solver.IntVar(0,1,'V_'+t+'->'+r)
        v_aux.append({str(r):variable_v})   #Lo agregamos como diccionario para
                                            # poder recuperarlo por routers después.
    
    v_conexionesTerminalesRouterGPRS.append(v_aux)

imprimir_tabla_cortada(v_conexionesTerminalesRouterGPRS,"V")



# Creamos las variables de conexión router WPAN-Concentrador
# Solamente crearemos las fisicamente posibles para cada router
u_conexionesRoutersWPANConcentradores = []

print("\nDefiniendo variables conexión routers GPRS -> Concentradores:\n")
for conexionCandidata in conn_c_rout_conc:
    u_aux = []
    for concentradorCandidato in conexionCandidata["Vecinos"]:
        r = str(conexionCandidata['Referencia'][0])
        c = concentradorCandidato[0]
        variable_u = solver.IntVar(0,1,'U_'+r+'->'+c) 
        u_aux.append({str(c):variable_u})
        
    u_conexionesRoutersWPANConcentradores.append(u_aux)


imprimir_tabla_cortada(u_conexionesRoutersWPANConcentradores,"U")



# Creamos las variables routers gprs, wpan y concentradores. 1 por cada uno.
# Las almacenamos en diccionarios para que sean facilmente recuperables usando
# su nombre
r_WPAN = {}
for routerWPAN in routers:
    r_WPAN_VAR = solver.IntVar(0,1,str(routerWPAN[0])+"_WPAN")
    r_WPAN[routerWPAN[0]] = r_WPAN_VAR

r_GPRS = {}
for routerGPRS in routers:
    r_GPRS_VAR = solver.IntVar(0,1,str(routerGPRS[0])+"_GPRS")
    r_GPRS[routerGPRS[0]] = r_GPRS_VAR
    
c_CONCENTRADORES = {}
for concentrador in concentradores:
    c_CONCENTRADOR_VAR = solver.IntVar(0,1,concentrador[0])
    c_CONCENTRADORES[concentrador[0]] = c_CONCENTRADOR_VAR


print(str(len(r_WPAN)) + " posiciones candidatas para routers WPAN")
print(str(len(r_GPRS)) + " posiciones candidatas para routers GPRS")
print(str(len(c_CONCENTRADORES)) + " posiciones candidatas para concentradores")





#%% Creamos algunas listas y diccionarios que nos serán útiles después para
#   crear variables y restricciones


# Almacenamos los nombres de todos los routers para realizar la suma de
# conexiones a cada uno de los routers
routersNombres = [fila[0] for fila in routers]
concentradorNombres = [fila[0] for fila in concentradores]



# Agrupamos las conexiones que llegan a cada router WPAN en un diccionario
conexiones_terminales_to_routerWPAN = {}

for terminal in w_conexionesTerminalesRouterWPAN:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in terminal:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for router, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if router in conexiones_terminales_to_routerWPAN:
                conexiones_terminales_to_routerWPAN[router].append(valorConexion)
            else:
                conexiones_terminales_to_routerWPAN[router] = []
                conexiones_terminales_to_routerWPAN[router].append(valorConexion)
                



# Agrupamos las conexiones que llegan a cada router GPRS en un diccionario
conexiones_terminales_to_routerGPRS = {}

for terminal in v_conexionesTerminalesRouterGPRS:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in terminal:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for router, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if router in conexiones_terminales_to_routerGPRS:
                conexiones_terminales_to_routerGPRS[router].append(valorConexion)
            else:
                conexiones_terminales_to_routerGPRS[router] = []
                conexiones_terminales_to_routerGPRS[router].append(valorConexion)



# Agrupamos las conexiones que llegan a cada router Concentrador en un diccionario
conexiones_routersWPAN_to_concentradores = {}

for router in u_conexionesRoutersWPANConcentradores:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in router:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for concentrador, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if concentrador in conexiones_routersWPAN_to_concentradores:
                conexiones_routersWPAN_to_concentradores[concentrador].append(valorConexion)
            else:
                conexiones_routersWPAN_to_concentradores[concentrador] = []
                conexiones_routersWPAN_to_concentradores[concentrador].append(valorConexion)

#%% Definimos las restricciones
'''
- R1: Cada terminal solo puede estar
'''

# Cada terminal solo puede (Y DEBE) estar conectado a un router (GPRS o WPAN)
for terminal_WPAN, terminal_GPRS in zip(w_conexionesTerminalesRouterWPAN, 
                                        v_conexionesTerminalesRouterGPRS):
    sum_conex_terminal_RWPAN = 0
    sum_conex_terminal_RGPRS = 0
    
    for conexionCandidata in terminal_WPAN:
        sum_conex_terminal_RWPAN += list(conexionCandidata.values())[0]
    
    for conexionCandidata in terminal_GPRS:
        sum_conex_terminal_RGPRS += list(conexionCandidata.values())[0]
    
    suma = sum_conex_terminal_RWPAN + sum_conex_terminal_RGPRS
    solver.Add(suma == 1)
    
    
# Cada router WPAN solo puede (Y DEBE) estar conectado a un concentrador
for routerWPAN in u_conexionesRoutersWPANConcentradores:
    
    suma_conex_RWPAN_Concentrador = 0
    
    for conexionCandidata in routerWPAN:
        suma_conex_RWPAN_Concentrador += list(conexionCandidata.values())[0]
    
    solver.Add(suma_conex_RWPAN_Concentrador == 1)    


# Añadimos las restricciones de capacidad de los routers y concentradores
for router in routersNombres:
    solver.Add(sum(conexiones_terminales_to_routerGPRS[router]) <= capacidadMaxGPRS)
    
for router in routersNombres:
    solver.Add(sum(conexiones_terminales_to_routerWPAN[router]) <= capacidadMaxWPAN)
    
for concentrador in concentradorNombres:
    solver.Add(sum(conexiones_routersWPAN_to_concentradores[concentrador]) <= capacidadMaxConcentradores)

#%% Un router solo existirá si cualquiera de sus conexiones existe
# Es decir cada router debe ser >= a cualquiera de sus conexiones
# EJEMPLO: 
#   R1 >= W1->1
#   R1 >= W2->1
#   R1 >= W3->1
#   R1 >= W...->1
for router in routersNombres:
    for conexion in conexiones_terminales_to_routerWPAN[router]:
        solver.Add(r_WPAN[router] >= conexion)
        
for router in routersNombres:
    for conexion in conexiones_terminales_to_routerGPRS[router]:
        solver.Add(r_GPRS[router] >= conexion)


#%% Un concentrador solo existirá si cualquiera de sus conexiones entrantes existe
for concentrador in concentradorNombres:
    for conexion in conexiones_routersWPAN_to_concentradores[concentrador]:
        solver.Add(c_CONCENTRADORES[concentrador] >= conexion)
        

#%% Definimos la función obejtivo y resolvemos

Z = (costeWPAN * sum(r_WPAN.values()) + costeGPRS * sum(r_GPRS.values()) 
                             + costeConcentrador * sum(c_CONCENTRADORES.values()))

solver.Minimize(Z)
status = solver.Solve()


if status == pywraplp.Solver.OPTIMAL:
    
    print("\nSe ha encontrado la solución óptima")
    objective = solver.Objective()
    
    print()
    for router in routersNombres:
        r = r_GPRS[router]
        if r.solution_value() > 0:
            print(r.name() + " = " + str(r.solution_value()))
    
    print()
    for router in routersNombres:
        r = r_WPAN[router]
        if r.solution_value() > 0:
            print(r.name() + " = " + str(r.solution_value()))
     
    print()
    for concentrador in concentradorNombres:
        c= c_CONCENTRADORES[concentrador]
        if c.solution_value() > 0:
            print(c.name() + " = " + str(c.solution_value()))
            
    print()
    conexiones_term_routersWPAN = {}
    for conexionTerminalRouter in w_conexionesTerminalesRouterWPAN:
        for conn in conexionTerminalRouter:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                print(c.name() + " = " + str(c.solution_value()))
                conexiones_term_routersWPAN[c.name()] = c.solution_value()
                
    print()
    conexiones_term_routersGPRS = {}
    for conexionTerminalRouter in v_conexionesTerminalesRouterGPRS:
        for conn in conexionTerminalRouter:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                print(c.name() + " = " + str(c.solution_value()))
                conexiones_term_routersGPRS[c.name()] = c.solution_value()
                
    print()
    conexiones_routers_concentradores = {}
    for conexionRouterConcentrador in u_conexionesRoutersWPANConcentradores:
        for conn in conexionRouterConcentrador:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                print(c.name() + " = " + str(c.solution_value()))
                conexiones_routers_concentradores[c.name()] = c.solution_value()
    
    
    
    
    #%% DIBUJAMOS LOS NODOS CON MATPLOTLIB
    # Extraer las posiciones de los nodos (routers, terminales y concentradores)
    posiciones = {nodo[0]: [nodo[1], nodo[2]] for nodo in (routers + 
                                                           terminales + 
                                                           concentradores)}
    
    # Crear el gráfico con las mismas dimensiones y dpi que los anteriores
    plt.figure(5)
    plt.figure(figsize=(10, 8),dpi=150)
    plt.xlim(-110, 110)
    plt.ylim(-110, 110)
    
    
    # Dibujar los nodos
    for nodo, (x, y) in posiciones.items():
        if nodo.startswith('T'):
            plt.scatter(x, y, marker='*', color='red', label=nodo)
        elif nodo.startswith('R'):
            plt.scatter(x, y, marker='s', color='purple', label=nodo)
            ''' CREAR DISTINCION POR TIPO DE ROUTER
            elif nodo.startswith('R') and nodo in routersWPAN:
                plt.scatter(x, y, marker='s', color='purple', s=200, label=nodo)
            elif nodo.startswith('R') and nodo in routersGPRS:
                plt.scatter(x, y, marker='s', color='green', s=200, label=nodo)
            '''
        elif nodo.startswith('C'):
            plt.scatter(x, y, marker='o', color='blue', label=nodo)
        
        
    
    # Dibujar las conexiones entre terminales y routers
    for conexion, valor in conexiones_term_routersWPAN.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            terminal, router = resto.split('->')
            x1, y1 = posiciones[terminal][0], posiciones[terminal][1]
            x2, y2 = posiciones[router][0], posiciones[router][1]
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                            arrowstyle='->', color='green', linestyle='dashed'))
            
    # Dibujar las conexiones entre routers y concentradores
    for conexion, valor in conexiones_routers_concentradores.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            router, concentrador = resto.split('->')
            x1, y1 = posiciones[router][0], posiciones[router][1]
            x2, y2 = posiciones[concentrador][0], posiciones[concentrador][1]
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                arrowstyle='->', color='blue', linestyle='dashed'))
    
    #Creamos leyenda
    concentradores_patch = mpatches.Patch(color='blue', label='Concentradores')
    routers_patch = mpatches.Patch(color='purple', label='Routers')
    terminal_patch = mpatches.Patch(color='red', label='Routers')
    plt.legend(handles=[concentradores_patch, routers_patch, terminal_patch])

    # Configuraciones del gráfico
    plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
    plt.title('Ubicaciones concentradores candidatas para conectarse con router '+ nombreRouterEjemplo)
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    #%% Dibujamos los nodos con networkx y matplotlib 
    '''
    # Crear un grafo
    G = nx.Graph()
    
    # Agregar nodos al grafo con atributos
    for nodo, pos in posiciones.items():
        if nodo.startswith('T'):
            G.add_node(nodo, pos=pos, node_type='terminal', color='red')
        elif nodo.startswith('R'):
            G.add_node(nodo, pos=pos, node_type='router', color='purple')
        elif nodo.startswith('C'):
            G.add_node(nodo, pos=pos, node_type='concentrador', color='blue')
    
    # Agregar conexiones al grafo
    for conexion, valor in conexiones_term_routersWPAN.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            terminal, router = resto.split('->')
            G.add_edge(terminal, router, connection_type='term_router_W')
            
    
    # Dibujar el grafo
    plt.figure(7)
    plt.figure(figsize=(10, 8),dpi=150)
    plt.xlim(-110, 110)
    plt.ylim(-110, 110)
    
    # Dibujar nodos
    node_color = [G.nodes[n]['color'] for n in G.nodes()]
    node_types = nx.get_node_attributes(G, 'node_type')
    
    for nt in set(node_types.values()):
        nodes = [n for n, t in node_types.items() if t == nt]
        nx.draw_networkx_nodes(G, posiciones, nodelist=nodes, node_color=node_color, node_shape='o' if nt == 'concentrador' else 's' if nt == 'routerWPAN' or nt == 'routerGPRS' else '*')
    
    # Dibujar conexiones
    nx.draw_networkx_edges(G, posiciones, edge_color='gray')
    
    # Añadir leyenda
    legend_labels = {'terminal': 'Terminal', 'routerWPAN': 'Router WPAN', 'routerGPRS': 'Router GPRS', 'concentrador': 'Concentrador'}
    legend_handles = [plt.Line2D([0], [0], marker='o' if nt == 'concentrador' else 's' if nt == 'routerWPAN' or nt == 'routerGPRS' else '*', color='w', markerfacecolor=c, label=l) for nt, c, l in zip(set(node_types.values()), node_color, legend_labels.values())]
    plt.legend(handles=legend_handles, loc='best')
    
    plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
    plt.title('Grafo de conexiones de red')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    '''
    
    '''
    # Crear un grafo
    G = nx.Graph()
    
    # Agregar nodos al grafo con atributos
    for nodo, pos in posiciones.items():
        if nodo.startswith('T'):
            G.add_node(nodo, pos=pos, node_type='terminal', color='red')
        elif nodo.startswith('R'):
            G.add_node(nodo, pos=pos, node_type='routerWPAN', color='purple')
        elif nodo.startswith('C'):
            G.add_node(nodo, pos=pos, node_type='concentrador', color='blue')
    
    # Agregar conexiones al grafo
    for conexion, valor in conexiones_term_routersWPAN.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            terminal, router = resto.split('->')
            G.add_edge(terminal, router, connection_type='term_router_W')
            
    # Dibujar las conexiones entre routers y concentradores
    for conexion, valor in conexiones_routers_concentradores.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            router, concentrador = resto.split('->')
            G.add_edge(router, concentrador, connection_type='router_concentrador')
            
    
    # Dibujar el grafo
    plt.figure(figsize=(50, 50),dpi=150)
    plt.xlim(-110, 110)
    plt.ylim(-110, 110)
    
    # Dibujar nodos
    node_color = [G.nodes[n]['color'] for n in G.nodes()]
    node_types = nx.get_node_attributes(G, 'node_type')
    
    for nt in set(node_types.values()):
        nodes = [n for n, t in node_types.items() if t == nt]
        nx.draw_networkx_nodes(G, posiciones, nodelist=nodes, node_color=node_color, node_shape='o' if nt == 'concentrador' else 's' if nt == 'router' else '*')
    
    # Dibujar conexiones
    nx.draw_networkx_edges(G, posiciones, edge_color='gray')
    
    # Añadir leyenda
    legend_labels = {'terminal': 'Terminal', 'routerWPAN': 'Router WPAN', 'routerGPRS': 'Router GPRS', 'concentrador': 'Concentrador'}
    legend_handles = [plt.Line2D([0], [0], marker='o' if nt == 'concentrador' else 's' if nt == 'routerWPAN' or nt == 'routerGPRS' else '*', color='w', markerfacecolor=c, label=l) for nt, c, l in zip(set(node_types.values()), node_color, legend_labels.values())]
    plt.legend(handles=legend_handles, loc='best')
    
    plt.title('Grafo de conexiones de red')
    plt.tight_layout()
    plt.show()
    '''
    # Crear un grafo
    G = nx.Graph()
    
    # Agregar nodos al grafo con atributos
    for nodo in posiciones.keys():
        if nodo.startswith('T'):
            G.add_node(nodo, node_type='terminal', color='red')
        elif nodo.startswith('R'):
            G.add_node(nodo, node_type='router', color='purple')
    
    # Agregar conexiones al grafo
    for conexion, valor in conexiones_term_routersWPAN.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            terminal, router = resto.split('->')
            G.add_edge(terminal, router, connection_type='term_router_W')
            
    # Filtrar las aristas que conectan terminales con routers
    term_router_edges = [(u, v) for u, v, d in G.edges(data=True) if d['connection_type'] == 'term_router_W']
    
    # Dibujar el grafo
    plt.figure(figsize=(8, 6))
    
    # Dibujar los nodos
    node_types = nx.get_node_attributes(G, 'node_type')
    colors = ['red' if node_types[n] == 'terminal' else 'purple' for n in G.nodes()]
    nx.draw_networkx_nodes(G, posiciones, node_color=colors, node_size=300)
    
    # Dibujar las aristas entre terminales y routers
    nx.draw_networkx_edges(G, posiciones, edgelist=term_router_edges, edge_color='gray')
    
    plt.title('Conexiones entre terminales y routers')
    plt.show()
else:
    print("El estado de la solución no es óptimo, es = " + str(status))




#%% Exportamos modelo
lp_model=solver.ExportModelAsLpFormat(False)
with open('modeloExportadoCasoFinal.txt', 'w') as f:
    print(lp_model, file=f) 

print("\nFin de la ejecución\n")






