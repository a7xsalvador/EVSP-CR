infty = 1e6

'''
from math import ceil
def fgamma(time, delta):
    return ceil(time/delta)
'''

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


def delete_labels(label_i,w):
    # label_i es label[i] = [[c1,f1,sch1],..., [cn,fn,schn]]
    L = [etiqueta for etiqueta in label_i if etiqueta[1]<=w] # Retiro las etiquetas con combustible remanente mayor a w

    # Ordenar la lista de listas por el segundo elemento de cada sublista
    L = sorted(L, key=lambda x: (x[1],x[0]))
    # L = sorted(L, key=lambda x: x[0])

    L1 = []
    c_bar = infty
    for r in L:
        if r[0] >= c_bar:
            L1.append(r)
        else:
            c_bar = r[0]

    result = [etiqueta for etiqueta in L if etiqueta not in L1]
    return result

def shortest_path_with_replenishment(list_comp_FT, K, Travels, depot_j, caa, h, Stations_chrg_time_dic_inv, dic_comp, w, fuel, dic_comp_F, T_ab, delta, time_window, t, Depots, time_dic):
    # Algoritmo de function shortest path with replenishment
    # label[i] tiene una lista de etiquetas, cada etiqueta es una lista de 3 elementos
    # label[i] = [[1,2,3],..., [c,f,sch]]

    h_values = list(h.values())
    best_sch = ()
    best_cost = infty
    label = {i : [] for i in Travels + h_values}
    Stations_chrg_time = list(Stations_chrg_time_dic_inv.keys())
    Stations_chrg = list(set([s for s,_ in Stations_chrg_time]))
    list_time = list(set([time for _,time in Stations_chrg_time]))

    for s in Stations_chrg: # Inicializa las etiquetas para estaciones que vienen desde desde el deposito
        if fuel[depot_j, h[depot_j,(s,1)]] <= w:
            for time in list_time:
                label[h[depot_j,(s,time)]].append([caa[depot_j, h[depot_j,(s,time)]], fuel[depot_j, h[depot_j,(s,1)]], (depot_j,Stations_chrg_time_dic_inv[s,time])]) #se agrega una etiqueta

    for i in Travels: 
        label[i].append([caa[depot_j,i], fuel[depot_j, i], (depot_j,i)])
        for s,time in Stations_chrg_time:
            
            '''
            if time > fgamma(T_ab[i][0] - time_window[0], delta): # Para no recorrer todos los tiempos (Si supero el instante al que empieza el viaje i, ya no hago nada de nada)
                # T_ab[i][0] el instante de inicio del viaje i, 
                # time_window[0] instante de inicio de la jornada 
                break
            '''
            
            for a in [depot_j] + Travels[:Travels.index(i)]:
                for r1 in label[h[a, (s, time)]]:
                    if T_ab[i][0] >= delta*(time+1) + time_window[0] + K*r1[1] + t[s,i]: #and (a,(s,time), i) in list_comp_FT:
                    #if  T_ab[a][1] + t[a,s] + K*r1[1] + t[s,i] <= T_ab[i][0] and (a,(s,time), i) in list_comp_FT: ##otro caso (para ests se debe poner T_ab[deposito][0]=0, T_ab[deposito][1]=999 )
                        label[i].append([r1[0] + caa[h[a,(s,time)], i], fuel[h[a,(s,time)],i], r1[2] + (i,) ])
                        


        for i1 in Travels[:Travels.index(i)]:
            if i in dic_comp[i1]:
                for r1 in label[i1]:
                    label[i].append([r1[0] + caa[i1, i], r1[1] + fuel[i1,i], r1[2] + (i,)])


        label[i] = delete_labels(label[i], w)


       
        for s,time in Stations_chrg_time: 

            '''
            if time < fgamma(T_ab[i][0] - time_window[0], delta): 
                # Si el tiempo es menor a cuando termina el viaje, no hago el siguiente conjunto de instrucciones. 
                # Estas las hago solo cuando el tiempo es mayor al instante cuando se acaba el viaje
                continue
            '''
            
            for r1 in label[i]:
                if comp_T(i,(s,time), Travels, Depots, T_ab, t, time_dic) and r1[1] + fuel[i,h[i,(s,time)]]<= w:
                    label[h[i,(s,time)]].append([r1[0] + caa[ i, h[i,(s,time)]], r1[1] + fuel[i,h[i,(s,time)]], r1[2] + (Stations_chrg_time_dic_inv[s,time],)])
                    

            label[h[i,(s,time)]] = delete_labels(label[h[i,(s,time)]], w)

            for r1 in label[h[i,(s,time)]]:
                if fuel[h[i,(s,time)],depot_j] <= w and r1[0] + caa[ h[i,(s,time)],depot_j]<= best_cost:
                    best_sch = (r1[2],depot_j)
                    best_cost = r1[0] +  caa[h[i,(s,time)],depot_j]
            

        dic_aux = {tuple(r1):r1[0] for r1 in label[i] if r1[1] + fuel[i, depot_j]<= w}
        if dic_aux:
            r = min(dic_aux, key=dic_aux.get)
            if r[0] + caa[i,depot_j] < best_cost:
                best_sch = (r[2],depot_j)
                best_cost = r[0] +  caa[i,depot_j]

    return best_cost, best_sch