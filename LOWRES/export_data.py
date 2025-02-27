import pandas as pd

def export_data(num_travels, time_dic, w, seed, V, T_ab, D_v,h_inv, rs_kt, cost, fuel, A1, A2, A3, A4, A5, A6, A7, single_file = False):
    dataTime = pd.DataFrame(time_dic)
    num_columnas = len(dataTime.columns)

    # Generar nombres de columnas y filas
    nombres_columnas = {i: f'tiempo {i+1}' for i in range(num_columnas)}
    nombres_filas = {0: 'hora_inicio', 1: 'hora_final'}

    # Cambiar nombres de las columnas y filas
    dataTime.rename(columns=nombres_columnas, index=nombres_filas, inplace=True)


    dataTravels = {'id': list(T_ab.keys()), 
                    'Hora_inicio': [a[0] for a in list(T_ab.values())], 
                    'Hora_final': [b[1] for b in list(T_ab.values())],
                    'Tipo': ['Viajes' for _ in list(T_ab.values())] }
    dataTravels = pd.DataFrame(dataTravels)


    dataDepots = {'id': list(D_v.keys()),
                'Capacidad': list(D_v.values()),
                'Tipo': ['Depositos' for _ in list(D_v.values())]}
    dataDepots = pd.DataFrame(dataDepots)


    dataH = {'id': list(h_inv.keys()), 
            'z': [z[0] for z in list(h_inv.values())], 
            's': [s[1][0] for s in list(h_inv.values())], 
            't': [t[1][1] for t in list(h_inv.values())],
            'Capacidad': [rs_kt[st[1][0], st[1][1]] for st in list(h_inv.values())],
            'Tipo': ['H(z,(st))' for _ in list(h_inv.values())] }

    dataH = pd.DataFrame(dataH)

    dataNodes = pd.concat([dataTravels, dataDepots, dataH]).fillna('-')
    dataNodes['id'] = dataNodes['id'].astype(int) 
    dataA1 = {'i': [i[0] for i in A1], 'j': [j[1] for j in A1], 'c_ij': [cost[ij] for ij in A1], 'f_ij': [fuel[ij] for ij in A1], 'tipo': ['A1' for _ in A1] }
    dataA2 = {'i': [i[0] for i in A2], 'j': [j[1] for j in A2], 'c_ij': [cost[ij] for ij in A2], 'f_ij': [fuel[ij] for ij in A2], 'tipo': ['A2' for _ in A2] }
    dataA3 = {'i': [i[0] for i in A3], 'j': [j[1] for j in A3], 'c_ij': [cost[ij] for ij in A3], 'f_ij': [fuel[ij] for ij in A3], 'tipo': ['A3' for _ in A3] }
    dataA4 = {'i': [i[0] for i in A4], 'j': [j[1] for j in A4], 'c_ij': [cost[ij] for ij in A4], 'f_ij': [fuel[ij] for ij in A4], 'tipo': ['A4' for _ in A4] }
    dataA5 = {'i': [i[0] for i in A5], 'j': [j[1] for j in A5], 'c_ij': [cost[ij] for ij in A5], 'f_ij': [fuel[ij] for ij in A5], 'tipo': ['A5' for _ in A5] }
    dataA6 = {'i': [i[0] for i in A6], 'j': [j[1] for j in A6], 'c_ij': [cost[ij] for ij in A6], 'f_ij': [fuel[ij] for ij in A6], 'tipo': ['A6' for _ in A6] }
    dataA7 = {'i': [i[0] for i in A7], 'j': [j[1] for j in A7], 'c_ij': [cost[ij] for ij in A7], 'f_ij': [fuel[ij] for ij in A7], 'tipo': ['A7' for _ in A7] }

    dataA1 = pd.DataFrame(dataA1)
    dataA2 = pd.DataFrame(dataA2)
    dataA3 = pd.DataFrame(dataA3)
    dataA4 = pd.DataFrame(dataA4)
    dataA5 = pd.DataFrame(dataA5)
    dataA6 = pd.DataFrame(dataA6)
    dataA7 = pd.DataFrame(dataA7)


    dataA = pd.concat([dataA1,dataA2,dataA3,dataA4,dataA5,dataA6,dataA7])
    dataA['i'] = dataA['i'].astype(int) 
    dataA['j'] = dataA['j'].astype(int) 

    if single_file == True:
        with open(f'salida_{num_travels}_{seed}.csv', 'w') as archivo:
            archivo.write(f'w = {w}, semilla = {seed}\n')
            archivo.write(f'V = {V}\n')
            archivo.write(f'\n')
            archivo.write(f'Data_Time\n')
            dataTime.to_csv(archivo, index=True)
            archivo.write(f'\n')

            archivo.write(f'Travels\n')
            dataTravels[['id','Hora_inicio','Hora_final']].to_csv(archivo, index=False)

            archivo.write(f'\n')

            archivo.write(f'Depots\n')
            dataDepots[['id','Capacidad']].to_csv(archivo, index=False)
            
            archivo.write(f'\n')

            archivo.write(f'h-nodes\n')
            dataH[['id','z','s','t','Capacidad']].to_csv(archivo, index=False)

            archivo.write(f'\n')

            archivo.write(f'Arcos\n')
            dataA[['i','j','c_ij', 'f_ij']].to_csv(archivo, index=False)
            
    else:
        with open(f'arcos_{num_travels}_{seed}.csv', 'w') as archivo:
            archivo.write(f'w = {w}, semilla = {seed}\n')
            dataA.to_csv(archivo, index=False)

        with open(f'nodos_{num_travels}_{seed}.csv', 'w') as archivo:
            archivo.write(f'w = {w}, semilla = {seed}\n')
            dataNodes.to_csv(archivo, index=False)

        with open(f'tiempos_{num_travels}_{seed}.csv', 'w') as archivo:
            archivo.write(f'w = {w}, semilla = {seed}\n')
            dataTime.to_csv(archivo, index=True)

    print("oki")
