def create_cost_double_apostrophe(a, b, gamma, Travels, h, Depots, cost, h_inv):
    '''
    Crea los costos para c'' definido   
                  / c'(v_1,v_2) - pi_i          para v_1 in Travels, v_2 in V
    c''(v_1,v_2)={  c'(v_1,v_2) + chi_{kt}      para v_1 in H, v_2 in V
                  \ c'(v_1,v_2) + rho_j         para v_1 in Depots, v_2 in V 
    '''
    # Se junta varios diccionarios: dic_juntos = {**dic1,**dic2,...,**dicn}
    cost_double_apostrophe = {**{(i,j):cost[i,j] - a[i] for (i,j) in cost.keys() if i in Travels},
                              **{(i,j):cost[i,j] + gamma[h_inv[i][1][0], h_inv[i][1][1]] for (i,j) in cost.keys() if i in list(h.values()) }, 
                              **{(i,j):cost[i,j] + b[i] for (i,j) in cost.keys() if i in Depots} } 
    return cost_double_apostrophe

    #h_inv[i] = (z, (s, t))
    #h_inv[i][1] = (s, t)
    #h_inv[i][1][0] = s
    #h_inv[i][1][1] = t


def create_cost_double_apostrophe_v2(a, b, gamma, cost, h_inv, delta_mas_i, delta_mas_k, delta_mas_h):
    cost_double_apostrophe = cost.copy()

    ######### si los deltas son listas
    for arch in delta_mas_i:
        cost_double_apostrophe[arch] -= a[arch[0]]
    for arch in delta_mas_k:
        cost_double_apostrophe[arch] += b[arch[0]]
    for arch in delta_mas_h:
        cost_double_apostrophe[arch] += gamma[h_inv[arch[0]][1][0], h_inv[arch[0]][1][1]]

    return cost_double_apostrophe


    

def flatten_tuple(t):
    '''
    Se requiere esta función porque best_sch viene en un formato de tuplas dentro de tuplas: ((((5,6),7),8),5)->[5,6,7,8,5]
    '''
    if isinstance(t, tuple):
        return [item for subtuple in t for item in flatten_tuple(subtuple)]
    else:
        return [t]
    




def calculate_cost(path_in_V, cost):
    '''
    Calculo el costo de un camino dado en V (Travels+Depots+H)
    Se recibe un path_in_V que se supone que empieza y termina en el mismo depósito
    '''
    if len(path_in_V)==1: # costo de las columnas ficticias cachai
        return 1e10

    initial_depot = path_in_V[0] # depósito inicial, se supone que el subproblema devuelve caminos que empiezan por un depósito
    total_cost = 0
    for i,j in enumerate(path_in_V):
        total_cost += cost[j,path_in_V[i+1]]

        if path_in_V[i+1]==initial_depot:# si el siguiente nodo del camino es el depósito, se termina pues ya calculó todos los costos
            break
    return total_cost



def calculate_fuel(path_in_V, fuel, H_list_inv):
    '''
    Calculo el combustible usado en un camino dado en V (Travels+Depots+H)
    si el camino pasa por un nodo H, reinicia la cuenta
    Se recibe un path_in_V que se supone que empieza y termina en el mismo depósito
    '''

    initial_depot = path_in_V[0] # depósito inicial, se supone que el subproblema devuelve caminos que empiezan por un depósito
    fuel_consumed = 0
    
    fuel_before_recharging = []
    for i,j in enumerate(path_in_V):
        fuel_consumed += fuel[j,path_in_V[i+1]]
        if path_in_V[i+1] in H_list_inv: 
            # si el siguiente nodo es un H-node entonces se almacena el valor del combustible
            # y se reinicia el contador pues el vehículo se recarga
            fuel_before_recharging.append(fuel_consumed) 
            fuel_consumed = 0
        elif path_in_V[i+1]==initial_depot:# si el siguiente nodo del camino es el depósito, se termina pues ya calculó todos los costos
            fuel_before_recharging.append(fuel_consumed) 
            break
    return fuel_before_recharging


def from_TDSt_to_V(path_TDS, Travels, Depots, Stations_chrg_time_dic, h):
    '''
    El subproblema devuelve una sucesión de nodos de Travels + Depots + Stations_chrg_time, pero 
    el problema máster trabaja en V que está dado por nodos de V = Travels + Depots + H_t
    '''
    path_in_V = []
    for i,j in enumerate(path_TDS):
        if j in Travels+Depots:
            path_in_V.append(j)
        else:
            path_in_V.append(h[path_TDS[i-1],Stations_chrg_time_dic[j]])
    return path_in_V

def from_V_to_TDS(path_V, Travels, Depots, Stations_chrg, h_inv, visible=False):
    '''
    Pasa de V = Travels + Depots + H ----> TDS = Travels + Depots + Stations_chrg
    '''
    path_in_TDS = []
    for j in path_V:
        if j in Travels+Depots:
            path_in_TDS.append(j)
        if j in list(h_inv.keys()):
            path_in_TDS.append(h_inv[j][1]) #devuelve sigma del elemento h(z,sigma)

    #para visibilizar que nodo es 
    if visible == True:
        for i,j in enumerate(path_in_TDS):
            if j in Travels:
                path_in_TDS[i] = f'T_{j}'
            if j in Depots:
                path_in_TDS[i] = f'D_{j}'
            if j in Stations_chrg:
                path_in_TDS[i] = f'S_{j}'

                
    return path_in_TDS