
from compatibility_functions import comp_T
from collections import defaultdict
from model_functions import distance, len_trip


def create_nodes(Travels, Depots, Stations_chrg_time, num_travels, num_depots, num_charge_stations, Stations_chrg_time_low_res, lowres):
    '''
    Construye los nodos del grafo
    '''

    num_charge_time_stations = len(Stations_chrg_time)
    Stations_chrg_time_dic = { num_travels+num_depots+num_charge_stations+1+i: Stations_chrg_time[i] for i in range(len(Stations_chrg_time))}
    Stations_chrg_time_dic_inv = {Stations_chrg_time_dic[i]:i for i in Stations_chrg_time_dic}

    #print(Stations_chrg_time_dic_inv)

    Stations_chrg_time_dic_inv_low_res = { i: Stations_chrg_time_dic_inv[i] for i in  Stations_chrg_time_low_res} if lowres == True else []

    #print(Stations_chrg_time_dic_inv_low_res)

    H_list = [(travel_depot, ch_station_time) for travel_depot in Travels+Depots for ch_station_time in Stations_chrg_time ]

    h = {element: num_travels+num_depots+num_charge_stations+num_charge_time_stations+1+i for i,element in enumerate(H_list)} # el +1 es porque i empieza desde 0
    h_inv = {h[i]:i for i in h} # aux para los costos
    # como cada elemento de H_list es un nodo, se le asigna un índice a partir de num_travels+num_depots+num_charge_stations+1
    H_list_inv = list(h_inv.keys())

    V = Travels +  Depots + list(h.values())                                                           # V usado para el grafo
    V_visual = [f'T_{i}' for i in Travels] + [f'D_{k}' for k in Depots] + [f'{h1}' for h1 in H_list]   # V_visual es usado para visualizar en el grafo


    return H_list, H_list_inv, h, h_inv, V, V_visual, Stations_chrg_time_dic, Stations_chrg_time_dic_inv, Stations_chrg_time_dic_inv_low_res



def create_archs(Travels, Depots, h, H_list, dic_comp, dic_comp_F, T_ab, time_dic, t, Hk, fuel_per_distance, T_passenger_stations, coord_passenger_stations, Stations_chrg, coord_depots, coord_charge_stations, cost_per_distance ):
    '''
    Crea los arcos del grafo
    '''

    delta_mas = defaultdict(list)
    delta_menos = defaultdict(list)
    Ak = []
    Ak_with_i_in_DH = []
    Ak_with_i_not_in_DH = []


    fuel_requirement = {i:fuel_per_distance*len_trip(i,T_passenger_stations, coord_passenger_stations) for i in Travels}
    cost = {}
    fuel = {}
    delta_mas_i = [] #lista de arcos para optimizar el hallar el costo reducido (1ra restr, forall Travels)
    delta_mas_k = [] #(2da restr, forall Depots)
    delta_mas_h = [] #(3ra restr, forall )


    #A1 = [(i, j) for i in Travels for j in Travels if i!=j and j in dic_comp[i]]
    A1 = []
    for i in Travels:
        for j in Travels:
            if j in dic_comp[i]:
                #A1.append((i,j))
                cost[(i,j)] = cost_per_distance*distance(i,j, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                fuel[(i,j)] = fuel_requirement[i] + fuel_per_distance*distance(i,j, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                delta_mas_i.append((i,j))
                for k in Depots:
                    delta_mas[(i,k)] += [ j ]
                    delta_menos[(j,k)] += [ i ]
                    #Ak.append((i,j,k))
                    #Ak_with_i_not_in_DH.append((i,j,k))


    #A2 = [(i, k) for i in Travels for k in Depots]
    A2 = []
    for i in Travels:
        for k in Depots:
            #A2.append((i,k))
            cost[(i,k)] = cost_per_distance*distance(i,k, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            fuel[(i,k)] = fuel_requirement[i] + fuel_per_distance*distance(i,k, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            delta_mas_i.append( (i,k) )

            delta_mas[(i,k)] += [ k ]
            delta_menos[(k,k)] += [ i ]
            #Ak.append((i,k,k))
            #Ak_with_i_not_in_DH.append((i,k,k))



    #A3 = [(i, h[node]) for i in Travels for node in H_list if node[0]==i and comp_T(i, node[1], Travels, Depots, T_ab, t, time_dic)] # node[0]  = tau_i, node[1] = sigma_kt                                     
    A3 = []
    for i in Travels:
        for node in H_list:
            if node[0]==i and  comp_T(i, node[1], Travels, Depots, T_ab, t, time_dic):
                #A3.append((i, h[node]))
                cost[(i, h[node])] = cost_per_distance*distance(node[0],node[1][0], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                fuel[(i, h[node])] = fuel_requirement[node[0]] +  fuel_per_distance*distance(node[0],node[1][0], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                delta_mas_i.append( (i, h[node]) )

                for k in Depots:
                    delta_mas[(i,k)]  += [ h[node] ]
                    delta_menos[(h[node],k)] += [ i ]
                    #Ak.append((i,h[node],k)) 
                    #Ak_with_i_not_in_DH.append((i,h[node],k))   


    #A4 = [(h[node], i) for node in H_list for i in Travels if node[1][0] in dic_comp_F[node[0],i] and comp_T(node[0], node[1], Travels, Depots, T_ab, t,  time_dic) and comp_T(node[1], i,Travels, Depots, T_ab, t, time_dic) ]           
    A4 = []
    A4_prepared = []
    A4_dic_preparated = defaultdict(list)

    for node in H_list:
        for i in Travels:
            if node[1][0] in dic_comp_F[node[0],i] and comp_T(node[0], node[1], Travels, Depots, T_ab, t,  time_dic) and comp_T(node[1], i,Travels, Depots, T_ab, t, time_dic):
                #A4.append((h[node],i))
                #los preparated son para la séptima restricción del programa de arcos ujuju
                #A4_prepared.append((h[node],i,node[1]))
                cost[(h[node],i)] = cost_per_distance*distance(node[1][0],i, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                fuel[(h[node],i)] = fuel_per_distance*distance(node[1][0],i, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                delta_mas_h.append((h[node],i))

                for k in Depots:
                    if h[node] in Hk[k]:
                        delta_mas[(h[node], k)] += [ i ]
                        delta_menos[(i, k)] += [ h[node] ]
                        #Ak.append((h[node], i,k))
                        #A4_dic_preparated[(h[node],i)] += [ k ]
                        #Ak_with_i_in_DH.append((h[node],i,k))

    #A5 = [(h[node], k) for node in H_list for k in Depots if node[0] not in Depots and comp_T(node[0], node[1],Travels, Depots, T_ab, t, time_dic)]   
    A5 = []
    for node in H_list:
        for k in Depots:
            if node[0] not in Depots and comp_T(node[0], node[1],Travels, Depots, T_ab, t, time_dic):
                #A5.append((h[node], k))
                cost[(h[node],k)] = cost_per_distance*distance(node[1][0],k, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                fuel[(h[node],k)] = fuel_per_distance*distance(node[1][0],k, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                delta_mas_h.append((h[node],k))

                if h[node] in Hk[k]:
                    delta_mas[(h[node], k)] += [ k ]
                    delta_menos[(k,k)] += [ h[node] ]
                    #Ak.append((h[node], k, k))
                    #Ak_with_i_in_DH.append((h[node],k,k))


    #A6 = [(k, i) for i in Travels for k in Depots]
    A6 = []
    for i in Travels:
        for k in Depots:
            #A6.append((k,i))
            cost[(k,i)] = cost_per_distance*distance(k,i, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            fuel[(k,i)] = fuel_per_distance*distance(k,i, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            delta_mas_k.append((k,i))

            delta_mas[(k,k)] += [ i ]
            delta_menos[(i,k)] += [ k ]
            #Ak.append((k,i,k))
            #Ak_with_i_in_DH.append((k,i,k))


    #A7 = [(k, h[node]) for k in Depots for node in H_list if node[0]==k]
    A7 = []
    for k in Depots:
        for node in H_list:
            if node[0] == k:
                #A7.append((k, h[node]))
                cost[(k, h[node])] = cost_per_distance*distance(node[0],node[1][0], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                fuel[(k, h[node])] = fuel_per_distance*distance(node[0],node[1][0], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
                delta_mas_k.append((k, h[node]))

                delta_mas[(k,k)] += [ h[node] ]
                delta_menos[(h[node], k)] += [ k ]
                #Ak.append((k,h[node],k))
                #Ak_with_i_in_DH.append((k,h[node],k))

    A_list =[] #[A1, A2, A3, A4, A5, A6, A7] # Usado para graficar arcos con distinto color
    A =[] #A1 + A2 + A3 + A4 + A5 + A6 + A7

    return A1, A2, A3, A4, A5, A6, A7, A, A_list, delta_mas, delta_menos, Ak, cost, fuel, A4_prepared, A4_dic_preparated, Ak_with_i_in_DH, Ak_with_i_not_in_DH, delta_mas_i, delta_mas_k, delta_mas_h
