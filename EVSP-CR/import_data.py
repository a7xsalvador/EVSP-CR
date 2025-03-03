import pandas as pd

def import_data():
    with open('salida.csv', 'r') as archivo:
        lines = archivo.readlines()
        w, seed = [(x.split('=')[1].strip()) for x in lines[0].split(',')]
        V = int(lines[1].split('=')[1].strip())

    dataTime = pd.read_csv('tiempos.csv', index_col=0)

    dataTravels = pd.read_csv('nodos.csv')
    dataTravels = dataTravels[dataTravels['Tipo'] == 'Viajes'][['id', 'Hora_inicio', 'Hora_final']]
    T_ab = dict(zip(dataTravels['id'], zip(dataTravels['Hora_inicio'], dataTravels['Hora_final'])))

    dataDepots = pd.read_csv('nodos.csv')
    dataDepots = dataDepots[dataDepots['Tipo'] == 'Depositos'][['id', 'Capacidad']]
    D_v = dict(zip(dataDepots['id'], dataDepots['Capacidad']))

    dataH = pd.read_csv('nodos.csv')
    dataH = dataH[dataH['Tipo'] == 'H(z,(st))'][['id', 'z', 's', 't', 'Capacidad']]
    h_inv = {row['id']: (row['z'], (row['s'], row['t'])) for index, row in dataH.iterrows()}

    dataA = pd.read_csv('arcos.csv')
    A1 = [(row['i'], row['j']) for index, row in dataA[dataA['tipo'] == 'A1'].iterrows()]
    A2 = [(row['i'], row['j']) for index, row in dataA[dataA['tipo'] == 'A2'].iterrows()]
    A3 = [(row['i'], row['j']) for index, row in dataA[dataA['tipo'] == 'A3'].iterrows()]
    A4 = [(row['i'], row['j']) for index, row in dataA[dataA['tipo'] == 'A4'].iterrows()]
    A5 = [(row['i'], row['j']) for index, row in dataA[dataA['tipo'] == 'A5'].iterrows()]
    A6 = [(row['i'], row['j']) for index, row in dataA[dataA['tipo'] == 'A6'].iterrows()]
    A7 = [(row['i'], row['j']) for index, row in dataA[dataA['tipo'] == 'A7'].iterrows()]

    return w, seed, V, T_ab, D_v, h_inv, A1, A2, A3, A4, A5, A6, A7