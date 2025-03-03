#para graficar
import networkx as nx
import ipycytoscape
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

def plot_city(T_passenger_stations, T_ab, coord_passenger_stations, coord_depots, coord_charge_stations, size_square):
    '''
    Grafica la ciudad, sus estaciones, viajes entre estaciones, depósitos y cargadores
    '''
    
    # Tamaño de la fuente
    tamano_fuente = 7
    
    # Extraer las coordenadas en listas separadas
    x_coords, y_coords = zip(*coord_passenger_stations.values())
    x_coordsD, y_coordsD = zip(*coord_depots.values())    
    x_coordsS, y_coordsS = zip(*coord_charge_stations.values())

    # Crear el gráfico de dispersión
    plt.scatter(x_coords, y_coords, c='b', marker='o', label='Estaciones')
    plt.scatter(x_coordsD, y_coordsD, c='r', marker='o', label='Depósitos')
    plt.scatter(x_coordsS, y_coordsS, c='g', marker='o', label='Estaciones de carga')
    
    plt.ylim(-1, size_square+1)
    plt.xlim(-1, size_square+1)

    # Coordenadas de los vértices del cuadrado
    xc = [0, 0, size_square, size_square, 0]  # Las primeras dos coordenadas son para el primer vértice, las siguientes para el segundo y así sucesivamente
    yc = [0, size_square, size_square, 0, 0]

    # Graficar el cuadrado
    plt.plot(xc, yc)

    # Etiquetar las coordenadas
    for i, coord in enumerate(coord_passenger_stations.values()):
        plt.annotate(f'e{i}', coord, textcoords="offset points", xytext=(0, -15), ha='center', fontsize=tamano_fuente)
    for i in coord_depots:
        plt.annotate(f'DEP{i}', coord_depots[i], textcoords="offset points", xytext=(0, 10), ha='center',fontsize=tamano_fuente)
    for i in coord_charge_stations:
        plt.annotate(f'CHRG{i}', coord_charge_stations[i], textcoords="offset points", xytext=(0, 10), ha='center',fontsize=tamano_fuente)

    # Crear un nuevo eje para las flechas
    ax = plt.gca()

    # Graficar las flechas de los viajes
    colores = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'white']

    for i in T_passenger_stations:
        station_i = T_passenger_stations[i][0]
        station_f = T_passenger_stations[i][1]
        x_ini = coord_passenger_stations[station_i][0]
        y_ini = coord_passenger_stations[station_i][1]
        x_fin = coord_passenger_stations[station_f][0]
        y_fin = coord_passenger_stations[station_f][1]

        # Cada viaje va a estar dentro de la malla. arrow1 -> eje x, arrow2 -> eje y
        indice = i % len(colores)

        arrow1 = patches.FancyArrow(x_ini, y_ini, x_fin - x_ini, 0,
                                        width = 0.2,
                                        color=colores[indice],      # Cambiar el color a rojo
                                        alpha=0.2,        # Cambiar la transparencia a 0.5 (valor entre 0 y 1)
                                        head_width=0,  # Ancho de la cabeza de la flecha
                                        head_length=0,  # Longitud de la cabeza de la flecha
                                        overhang=0.2)     # Extensión de la cabeza de la flecha

        arrow2 = patches.FancyArrow(x_fin, y_ini, 0, y_fin - y_ini,
                                        width = 0.2,
                                        color=colores[indice],      # Cambiar el color a rojo
                                        alpha=0.2,        # Cambiar la transparencia a 0.5 (valor entre 0 y 1)
                                        head_width=0.7,  # Ancho de la cabeza de la flecha
                                        head_length=0.5,  # Longitud de la cabeza de la flecha
                                        overhang=0.2)     # Extensión de la cabeza de la flecha
        
        ax.add_patch(arrow1)  # Agregar la flecha al eje
        ax.add_patch(arrow2)  # Agregar la flecha al eje

        # Calcular las coordenadas de la etiqueta a la mitad de la flecha
        x_label = (x_fin) + random.randint(0,1)
        y_label = (y_ini) + random.randint(0,1)

        # Agregar la etiqueta al gráfico
        #plt.text(x_label, y_label, f'T{i} ({T_ab[i][0]}-{T_ab[i][1]})', fontsize=tamano_fuente, ha='center', va='center')
        plt.text(x_label, y_label, f'T{i}', fontsize=tamano_fuente+3, ha='center', va='center')


    # Configurar etiquetas y título
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')

    # Mostrar la cuadrícula
    plt.grid(True)
    plt.xticks(range(1, size_square))
    plt.yticks(range(1, size_square))

    # Mostrar leyenda
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Mostrar el gráfico
    plt.show()



def plot_graph(V, V_visual, A_list, cost, fuel):
    '''
    Grafica el grafo.
    '''
    color_list = [
        '#87CEEB',  # Azul claro
        '#FFB6C1',  # Rosa suave
        '#98FB98',  # Verde menta
        '#FFDAB9',  # Naranja suave
        '#40E0D0',  # Turquesa
        '#E6E6FA',  # Lavanda
        '#FF6F61'   # Coral
    ]

    D1 = nx.MultiDiGraph()
    D1.add_nodes_from(V)
    for i, value in enumerate(V):
        D1.nodes[value]['demanda']= str(V_visual[i]) #+ '\n' + str(bb[i])

    for index in range(7): ##los 7 tipos de ARCOS A1, A2,..., A7
        for (i,j) in A_list[index]:
            D1.add_edge(i,j,key=(i,j))
            D1.edges[i,j,(i,j)]['color'] = color_list[index]
    grafo = ipycytoscape.CytoscapeWidget()
    grafo.graph.add_graph_from_networkx(D1, directed=True)
    
    
    for (i, j) in list(cost.keys()):
        D1.add_edge(i, j, key=(i, j))
        D1.edges[i, j, (i, j)]['color'] = color_list[index]
        D1.edges[i, j, (i, j)]['etiqueta'] = f'{cost[i,j]},{fuel[i,j]}'  # Puedes asignar un texto específico a cada arco

    grafo = ipycytoscape.CytoscapeWidget()
    grafo.graph.add_graph_from_networkx(D1, directed=True)

    grafo.set_style([
        {'selector': 'node', 'style': {'background-color': '#11479e', 'font-family': 'helvetica', 'font-size': '8px', 'color': 'white', 'label': 'data(demanda)', 'text-wrap': 'wrap', 'text-valign': 'center'}},
        {'selector': 'node:parent', 'css': {'background-opacity': 0.333}, 'style': {'font-family': 'helvetica', 'font-size': '5px', 'label': 'data(demanda)'}},
        {'selector': 'edge', 'style': {'width': 1, 'line-color': 'data(color)', 'font-size': '10px', 'label': 'data(etiqueta)', 'text-valign': 'top', 'text-margin-y': '-10px'}},
        {'selector': 'edge.directed', 'style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'target-arrow-color': 'data(color)'}}
    ])
    
    return grafo # Llamar a la función para visualizar el grafo