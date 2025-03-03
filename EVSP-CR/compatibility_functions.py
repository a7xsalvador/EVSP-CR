def comp(i, j, T_passenger_stations, T_ab, t, deadhead = False):
    '''
    i,j son elementos de Travels
    deadhead=True toma que el final de un viaje obligatoriamente debe ser el inicio de otro
    '''
    if T_passenger_stations[i][1] != T_passenger_stations[j][0] and deadhead: # Asegurar deadhead
        aux = False
    else: 
        aux = True
    aj = T_ab[j][0]
    bi = T_ab[i][1]
    assert (i,j) in t.keys() 
    tij = t[(i,j)]
    return bi + tij < aj and aux



def comp_F(i, j, s, Depots, T_ab, t):
    ''' 
    Devuelve la factibilidad que se de el viaje i, vaya a la estación s, continue en el viaje j.
    i,j son elementos de Travels, s es elemento de Stations_chrg
    
    Al definir los arcos (A4) se asume que también pueden ser elementos de Depots por ello el condicional 'if'
    '''
    if i in Depots or j in Depots:
        return True
    return T_ab[i][1] + t[i,s] + t[s,j] <= T_ab[j][0]



def comp_T(first_node, second_node, Travels, Depots, T_ab, t, time_dic):
    if first_node in Depots or second_node in Depots:
        return True
    elif first_node in Travels:             # en este caso es (tau_i, sigma_kt)
        x1 = T_ab[first_node][1]            # instante de finalización del viaje de Travels 
        x2 = t[first_node, second_node[0]]  # tiempo de desplazamiento entre el final de ese viaje y sigma_k
        x3 = time_dic[second_node[1]][0]    # instante de inicio del intervalo t
        return  x1 + x2 <= x3
    
    elif second_node in Travels:            # en este caso es (sigma_kt, tau_i)
        y1 = time_dic[first_node[1]][1]     # instante de finalización del intervalo t 
        y2 = t[first_node[0], second_node]  # tiempo de desplazamiento entre sigma_k y el viaje (de Travels) 
        y3 = T_ab[second_node][0]           # instante de inicio de viaje (de Travels)
        return y1 + y2  <= y3
 

def comp_FT(first_node, ch_station_time, second_node, Travels, Depots, T_ab, t, time_dic):
    return comp_F(first_node, second_node, ch_station_time[0], Depots, T_ab, t) and comp_T(first_node, ch_station_time, Travels, Depots, T_ab, t, time_dic) and comp_T(ch_station_time, second_node, Travels, Depots, T_ab, t, time_dic)



def comp_T_forward(i, sigma_kt, t, time_dic, T_ab, Travels):

    '''
    Devuelve para el viaje i las estaciones de carga compatibles hacia adelante en el tiempo.
    Se considera el tiempo que toma en viajar desde i hasta la estación de carga k en el tiempo t
    '''
    if i in Travels:

        t_discrete_h = sigma_kt[1]  # intervalo discreto de sigma_kt

        val_k = sigma_kt[0] # identificación de la estación de carga

        t_interval_h = time_dic[t_discrete_h]

        begin_h = t_interval_h[0]   # hora real en la que empieza a trabajar la estación de carga

        t_interval_trip = T_ab[i]

        end_i = t_interval_trip[1] # hora real en la que termina a el viaje i

        if end_i + t[i,val_k] < begin_h:
            return True
        else:
            return False        
    else:
        return True


def comp_T_backward(i, sigma_kt, t, time_dic, T_ab, Travels):

    '''
    Devuelve para el viaje i las estaciones de carga compatibles hacia atrás en el tiempo.
    Se considera el tiempo que toma en viajar desde i hasta la estación de carga k en el tiempo t
    '''
    if i in Travels:
        t_discrete_h = sigma_kt[1]  # intervalo discreto de sigma_kt

        val_k = sigma_kt[0] # identificación de la estación de carga

        t_interval_h = time_dic[t_discrete_h]

        end_h = t_interval_h[1] # hora real en la que termina de trabajar la estación de carga

        t_interval_trip = T_ab[i]

        begin_i = t_interval_trip[0] # hora real en la que empieza a el viaje i

        if end_h + t[val_k,i] < begin_i:
            return True
        else:
            return False

    else:
        return True


def compatibility(Travels, Depots, Stations_chrg, Stations_chrg_time, T_passenger_stations, T_ab, t, time_dic):
    '''
    Crea diccionarios con compatibilidades
    '''
    dic_comp = { i:[j for j in Travels if i!=j and comp(i, j, T_passenger_stations, T_ab, t, deadhead = True) ] for i in Travels } #le hago diccionario
    dic_comp_F = {(i,j):[s for s in Stations_chrg  if comp_F(i, j, s, Depots, T_ab, t) ] for i in Travels+Depots for j in Travels + Depots } 

    list_comp_FT = [(i,kt,j)  for i in Travels+Depots for j in Travels+Depots for kt in Stations_chrg_time if comp_FT(i, kt, j, Travels, Depots, T_ab, t, time_dic) ]

    return dic_comp, dic_comp_F, list_comp_FT


    