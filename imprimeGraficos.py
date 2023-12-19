# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 17:25:08 2023

@author: jaime
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


#%% Funciones para la creación de gráficos

def crea_grafico(figura):
    """
    Crea un gráfico con un tamaño y unos dpi prefijados dado un número de 
    figura. 
    Se usa para que todos los gráficos tengan las mismas dimensiones y dpi.
    
    Parámetros:
        - figura (int): Número de figura a imprimir.
    """
    plt.figure(figura)
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
                                 distanciaMax = 0, devolver_figura=False):
    """
    Esta función visualiza en un gráfico los dispositivos que están en el rango 
    de conexión de un dispositivo de referencia específico en la red.

    Parámetros:
        - numFigura: Identificador numérico para la figura del gráfico.
        - indiceDispositivo:    Índice del dispositivo de referencia en el 
                                conjunto de conexiones.
        - conn_c_D1_D2: Estructura de datos que contiene información sobre 
                        las conexiones entre dispositivos y sus vecinos.
        - distanciaMax (opcional):  Distancia máxima de conexión. Si es 0, se 
                                    obtiene del dispositivo de referencia.
        - devolver_figura (bool, opcional): Si es True, la función devuelve la 
                                            figura creada en lugar de mostrarla 
                                            directamente. Por defecto es False.

    Proceso:
        1.  Inicialización del gráfico con el número de figura proporcionado.
        2.  Determinación del dispositivo de referencia y de sus dispositivos 
            compatibles (vecinos) dentro del rango.
        3.  Si no se proporciona una distancia máxima, se obtiene del cuarto 
            campo del dispositivo de referencia.
        4.  Manejo de excepciones para casos donde no hay dispositivos 
            compatibles, estableciendo un enfoque predeterminado en 'Router' 
            si ocurre un IndexError.
        5.  Visualización de los dispositivos compatibles y el dispositivo de 
            referencia en el gráfico, con diferentes colores y marcadores para 
            distinguirlos.
        6.  Creación y adición de leyendas para facilitar la interpretación del
            gráfico.
        7.  Dibujo del rango de conexión del dispositivo de referencia.
        8.  Configuración final del gráfico, incluyendo el título que refleja 
            la relación entre el dispositivo de referencia y sus vecinos.

    La función proporciona una herramienta visual para analizar cómo los 
    diferentes dispositivos dentro de una red están interconectados y cuáles 
    están dentro del alcance de conexión de un dispositivo específico, 
    resaltando la importancia de las distancias y tipos de conexiones en la 
    configuración de la red.
    """
    

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
    
    # Manejamos la excepción por si no hay dispositivos compatibles
    try:
        if nombreDispositivo.startswith('R'):
            tipoDisp = "Router"
            
            if dispositivosCompatibles[0][0].startswith('R'):
                nomDisps = "routers"
                D_compatibles_patch = mpatches.Patch(color='blue', 
                                                     label='Routers (Candidatos)')
            elif dispositivosCompatibles[0][0].startswith('C'):
                nomDisps = "concentradores"
                D_compatibles_patch = mpatches.Patch(color='blue', 
                                                     label='Concentradores (Candidatos)')
            
            
            D_ref_patch = mpatches.Patch(color='red', label=tipoDisp)
            
            
        
        elif nombreDispositivo.startswith('T'):
            tipoDisp = "Terminal"
            nomDisps = "routers"
            D_compatibles_patch = mpatches.Patch(color='blue', 
                                                 label='Routers (Candidatos)')
            D_ref_patch = mpatches.Patch(color='red', label=tipoDisp)
            
    
        # Pintamos gráfica con dispositivos
        pintar_plano(dispositivosCompatibles, 'blue', tipoDisp, marcador='o') 
        plt.legend(handles=[D_compatibles_patch, D_ref_patch]) 
    
    
    except IndexError:
        tipoDisp  = "Router" # La excepción solo se puede producir para routers
        nomDisps = "routers"
        D_ref_patch = mpatches.Patch(color='red', label=tipoDisp)
        plt.legend(handles=[D_ref_patch]) 
        
    
    
    # El nodo referencia y su rango lo pintamos aunque no existan vecinos
    pintar_nodo_rango(dispositivoReferencia, distanciaMax)    
       
    configurar_grafico("Ubicaciones " + nomDisps + " candidatos para " + 
                       "conectarse con " + str(nombreDispositivo))
    
    if devolver_figura:
        return plt.gcf()
    else:
        plt.show()

    
    
    
    
    
    
    
    
    
    
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
            
            
 
    
 
    
def dibujar_conexiones(conexiones, tipo, posiciones, color, estilo):
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
    for (dispositivo1, dispositivo2), valor in conexiones.items():
        if valor == 1.0:
            
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





def crea_grafico_conexiones_1(numFigura, posiciones,
                              w_TerminalesRWPAN_Solucion,
                              v_TerminalesRGPRS_Solucion, 
                              u_RWPANConcentradores_Solucion,
                              r_RWPAN_RWPAN_Solucion,
                              s_RWPAN_RGPRS_Solucion):
    """
    Esta función se encarga de crear y configurar un gráfico visual que representa
    las conexiones entre diferentes tipos de nodos en una red.

    Parámetros:
        - numFigura: Un identificador numérico para la figura del gráfico.
        - posiciones:   Un diccionario que mapea cada nodo con su posición en
                        el gráfico.
        - w_TerminalesRWPAN_Solucion, v_TerminalesRGPRS_Solucion, 
          u_RWPANConcentradores_Solucion, r_RWPAN_RWPAN_Solucion, s_RWPAN_RGPRS_Solucion:
          Listas de conexiones entre diferentes tipos de nodos en la red (terminales,
          routers WPAN, routers GPRS, etc.).

    La función realiza lo siguiente:
        1.  Inicializa un gráfico con dimensiones y dpi estandar.
        2.  Dibuja los nodos y sus conexiones en el gráfico utilizando 
            diferentes colores y estilos para representar distintos tipos de 
            conexiones.
        3.  Añade una leyenda al gráfico para facilitar la interpretación de 
            los colores y los estilos de las líneas.
        4.  Configura parámetros estándar del gráfico, como el título.
    
    El gráfico resultante ofrece una representación visual de la estructura de 
    la red, mostrando cómo los diferentes tipos de nodos están conectados entre 
    sí.
    """
    
            
    
        
    # Crear el gráfico con las mismas dimensiones y dpi que los anteriores
    crea_grafico(numFigura)
    
    
    # Dibujar los nodos y las conexiones
    dibujar_nodos_con_texto(posiciones)    
    dibujar_conexiones(w_TerminalesRWPAN_Solucion, 'W', posiciones, 
                       'red', 'dashed')    
    dibujar_conexiones(v_TerminalesRGPRS_Solucion, 'V', posiciones, 
                       'green', 'dashed')    
    dibujar_conexiones(u_RWPANConcentradores_Solucion, 'U', posiciones, 
                       'blue', 'dashed')    
    dibujar_conexiones(r_RWPAN_RWPAN_Solucion, 'R', posiciones, 
                       'brown', 'dashed')    
    dibujar_conexiones(s_RWPAN_RGPRS_Solucion, 'S', posiciones, 
                       'orange', 'dashed')

    
    #Creamos leyenda
    routers_WPAN_patch = mpatches.Patch(color='plum', label='Routers WPAN')
    routers_GPRS_patch = mpatches.Patch(color='LightGreen', label='Routers GPRS')
    concentradores_patch = mpatches.Patch(color='skyblue', label='Concentraodres')
    terminal_patch = mpatches.Patch(color='salmon', label='Terminal')
    plt.legend(handles=[terminal_patch, routers_WPAN_patch, 
                        routers_GPRS_patch, concentradores_patch])
    
    
    # Configuraciones estandar del gráfico
    configurar_grafico("Grafo de conexiones 1")
    


def crea_grafico_conexiones_2(numFigura, posiciones, 
                              w_TerminalesRWPAN_Solucion,
                              v_TerminalesRGPRS_Solucion, 
                              u_RWPANConcentradores_Solucion,
                              r_RWPAN_RWPAN_Solucion,
                              s_RWPAN_RGPRS_Solucion):
    """
    Esta función genera un gráfico detallado de las conexiones en una red, 
    utilizando networkx y matplotlib para visualizar nodos y sus 
    interconexiones.

    Parámetros:
        - numFigura: Identificador numérico para la figura del gráfico.
        - posiciones: Diccionario con las posiciones de los nodos en el gráfico.
        - w_TerminalesRWPAN_Solucion, v_TerminalesRGPRS_Solucion, 
          u_RWPANConcentradores_Solucion, r_RWPAN_RWPAN_Solucion, s_RWPAN_RGPRS_Solucion:
          Conjuntos de conexiones entre distintos tipos de nodos en la red.

    Proceso:
        1.  Inicialización de un grafo con networkx.
        2.  Agregación de nodos al grafo, clasificándolos en diferentes tipos 
            (terminales, routers WPAN, routers GPRS, concentradores) y 
            asignándoles colores distintivos.
        3.  Agregación de conexiones entre nodos basándose en los conjuntos de 
            soluciones proporcionados, identificando y diferenciando cada tipo 
            de conexión.
        4.  Configuración y dibujo del grafo con networkx y matplotlib, 
            utilizando colores y tamaños específicos para nodos y conexiones, 
            así como etiquetas para una fácil identificación.
        5.  Configuración de aspectos adicionales del gráfico, como ejes y 
            títulos.
        6.  Creación y adición de una leyenda al gráfico para facilitar la 
            interpretación de los elementos visuales.

    El resultado es un gráfico colorido y bien estructurado que muestra la 
    complejidad de la red y las interconexiones entre los diferentes tipos de 
    nodos, proporcionando una herramienta visual efectiva para analizar la 
    estructura de la red.
    """
    
    
    
    #%% Dibujamos los nodos con networkx y matplotlib 
    
    # Crear un grafo
    G = nx.Graph()
    
    # Agregar nodos al grafo con atributos
    for nodo in posiciones.keys():
        if nodo.startswith('T'):
            G.add_node(nodo, node_type='terminal', color='salmon')
        elif nodo.startswith('R'):
            if nodo.endswith('W'):
                G.add_node(nodo, node_type='router_W', color='plum')
            elif nodo.endswith('G'):
                G.add_node(nodo, node_type='router_G', color='LightGreen')
        elif nodo.startswith('C'):
            G.add_node(nodo, node_type='concentrador', color='skyblue')
            
    
    
    # Agregar conexiones al grafo
    for (terminal, router), valor in w_TerminalesRWPAN_Solucion.items():
        if valor == 1.0:
            tipo='W'
            router = router + "W"
            G.add_edge(terminal, router, connection_type='term_router_W')
            
    for (terminal, router), valor in v_TerminalesRGPRS_Solucion.items():
        if valor == 1.0:
            tipo = 'V'
            router = router + "G"
            G.add_edge(terminal, router, connection_type='term_router_G')
            
    for (router, concentrador), valor in u_RWPANConcentradores_Solucion.items():
        if valor == 1.0:
            tipo = 'U'
            router = router + "W"
            G.add_edge(router, concentrador, connection_type='router_W_concentrador')
            
    for (router, routerG), valor in s_RWPAN_RGPRS_Solucion.items():
        if valor == 1.0:
            tipo = 'S'
            router = router + "W"
            routerG = routerG + "G"
            G.add_edge(router, routerG, connection_type='router_W_router_G')
            
    for (router, router2), valor in r_RWPAN_RWPAN_Solucion.items():
        if valor == 1.0:
            tipo = 'R'
            router = router + "W"
            router2 = router2 + "W"
            G.add_edge(router, router2, connection_type='router_W_router_W')
       
    
    # Dibujar el grafo
    crea_grafico(numFigura)

    
    # Cambiamos los colores de los nodos
    node_types = nx.get_node_attributes(G, 'node_type')
    colores_nodos = []
    tam_nodos = []
    
    for nodo in G.nodes():
        if node_types[nodo] == 'terminal':
            colores_nodos.append('salmon')
            tam_nodos.append(100)
        elif node_types[nodo] == 'router_W':
            colores_nodos.append('plum')
            tam_nodos.append(400)
        elif node_types[nodo] == 'router_G':
            colores_nodos.append('LightGreen') 
            tam_nodos.append(400)
        elif node_types[nodo] == 'concentrador':
            colores_nodos.append('skyblue')
            tam_nodos.append(800)
    
            
            
    # Obtenemos los tipos de conexión para cada conexion
    connection_types = nx.get_edge_attributes(G, 'connection_type')
    # Definir colores para cada tipo de conexión
    colores_lineas = []
    for edge in G.edges():
        tipo_conexion = connection_types.get(edge, '')  #Obtiene tipo conexión
        if tipo_conexion == 'term_router_W':
            colores_lineas.append('red')
        elif tipo_conexion == 'term_router_G':
            colores_lineas.append('green')
        elif tipo_conexion == 'router_W_concentrador':
            colores_lineas.append('blue')
        elif tipo_conexion == 'router_W_router_G':
            colores_lineas.append('orange')
        elif tipo_conexion == 'router_W_router_W':
            colores_lineas.append('brown')
            
                      
        
    # Dibujar el grafo con los nodos que tienen posición definida
    nx.draw(G, posiciones, nodelist=posiciones, edge_color= colores_lineas, 
                node_color=colores_nodos, node_size=tam_nodos,
                with_labels=True)
    

    plt.axis('on') # Forzamos que se muestren los ejes para que se vea como el resto
    configurar_grafico("Grafo de conexiones 2",0)
    
    #Creamos leyenda
    routers_WPAN_patch = mpatches.Patch(color='plum', label='Routers WPAN')
    routers_GPRS_patch = mpatches.Patch(color='LightGreen', label='Routers GPRS')
    concentradores_patch = mpatches.Patch(color='skyblue', label='Concentraodres')
    terminal_patch = mpatches.Patch(color='salmon', label='Terminal')
    plt.legend(handles=[terminal_patch, routers_WPAN_patch, 
                        routers_GPRS_patch, concentradores_patch])



def imprime_html(tabla_w, tabla_v, tabla_u, tabla_r, tabla_s):
    """
    Genera un string con contenido HTML que incluye varias tablas.

    Esta función toma como entrada cinco tablas en formato HTML (como string) y 
    las inserta en una plantilla de documento HTML. Cada tabla se presenta en 
    una sección separada con su propio encabezado. Los estilos CSS incorporados 
    se aplican para mejorar la presentación visual de las tablas.

    Parámetros:
    - tabla_w: String con la tabla HTML de conexiones de Terminales a Routers WPAN.
    - tabla_v: String con la tabla HTML de conexiones de Terminales a Routers GPRS.
    - tabla_u: String con la tabla HTML de conexiones de Routers WPAN a Concentradores.
    - tabla_r: String con la tabla HTML de conexiones entre Routers WPAN.
    - tabla_s: String con la tabla HTML de conexiones de Routers WPAN a Routers GPRS.

    Retorna:
    - Un string que contiene un documento HTML completo con las tablas integradas.
    """

    html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tablas de Conexiones</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                    color: #333;
                }}
                .container {{
                    width: 50%;
                    margin: 20px auto;
                    overflow: hidden;
                }}
                table {{
                    border-collapse: collapse;
                    margin: 20px 0;
                    width: 100%;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: center;
                }}
                th {{
                    background-color: #be0f2e;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                tr:hover {{
                    background-color: #ddd;
                }}
                th:nth-child(3), td:nth-child(3) {{
                    width: 1%;
                    white-space: nowrap;
                }}
                th:nth-child(1), th:nth-child(2), td:nth-child(1), td:nth-child(2) {{
                    width: 49.5%;
                }}
                h2 {{
                    color: #333;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Tabla de Conexiones - Terminales a Routers WPAN</h2>
                {tabla_w}
                <h2>Tabla de Conexiones - Terminales a Routers GPRS</h2>
                {tabla_v}
                <h2>Tabla de Conexiones - Routers WPAN a Concentradores</h2>
                {tabla_u}
                <h2>Tabla de Conexiones - Routers WPAN a Routers WPAN</h2>
                {tabla_r}
                <h2>Tabla de Conexiones - Routers WPAN a Routers GPRS</h2>
                {tabla_s}
            </div>
        </body>
        </html>
        """.format(tabla_w=tabla_w, tabla_v=tabla_v, 
                    tabla_u=tabla_u, tabla_r=tabla_r, tabla_s=tabla_s)

    return html_content





    
    
    
    
    
    
    
    
    
    
    
    
    
    
    