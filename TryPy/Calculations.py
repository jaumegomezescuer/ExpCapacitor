# Import library
import numpy as np
from scipy.integrate import simpson


def ExtractCycles(dfData, ContactPosition=8, ContactForce=None, Latency=10e-3, CurrentTh=None):
    """
    Extracts cycles from the given dataframe based on the specified ContactPosition or ContactForce.
    Calculates various parameters for each cycle and returns a list of dictionaries containing the cycle data.

    Parameters:
    - dfData: DataFrame, the input data
    - ContactPosition: int, optional, the position for contact detection
    - ContactForce: float, optional, the force for contact detection
    - Latency: float, the latency threshold
    - CurrentTh: float, optional, the current threshold for transition time calculation

    Returns:
    - CyclesList: list of dicts, containing data for each cycle
    """


    # Calculate Contact Position
    if ContactPosition is not None:
        dt = dfData.Time[dfData['Position'] < ContactPosition].diff()
        StartInds = np.where(dt > Latency)[0]
        StartInds = np.hstack((0, StartInds))
        Indexs = dt.index.values
        StartIndexs = Indexs[StartInds]
        EndIndexs = Indexs[StartInds - 1][1:]
        EndIndexs = np.hstack((EndIndexs, Indexs[-1]))
    elif ContactForce is not None:
        dt = dfData.Time[dfData['Force'] > ContactForce].diff()
        StartInds = np.where(dt > Latency)[0]
        StartInds = np.hstack((0, StartInds))
        Indexs = dt.index.values
        StartIndexs = Indexs[StartInds]
        EndIndexs = Indexs[StartInds - 1][1:]
        EndIndexs = np.hstack((EndIndexs, Indexs[-1]))
    else:
        print('Please specify ContactForce or ContactPosition')
        return None

    # Calculate Duration
    Duration = dfData.Time[EndIndexs].values - dfData.Time[StartIndexs].values
    nSampsCycle = EndIndexs - StartIndexs
    print('Cycles Duration')
    print(Duration)
    print('Cycles Samples')
    print(nSampsCycle)
    nSampsCycle = np.max(nSampsCycle)

    CyclesList = []
    for ic, st in enumerate(StartIndexs):
        ed = st + nSampsCycle
        if ed > dfData.shape[0]:
            ed = dfData.shape[0]-1
        data = dfData[st:ed].copy()
        data.reset_index(inplace=True, drop=True)
        data.loc[:, 'Time'] = data.Time.values - data.Time[0]
        # Obtiene el valor de voltaje en el índice de inicio del ciclo

        # Calculate sign transition time
        if CurrentTh is None:
            IndHalf = int(data.shape[0] / 2)
            #pos=data.Time[data.Position == data.Position.min()]
            #min_position_value = dfData['Position'].min()  # Obtiene el valor mínimo de la columna 'Position'
            # min_time = dfData.loc[dfData['Position'] == min_position_value, 'Time'].iloc[0]  # Obtiene el tiempo correspondiente al valor mínimo de la posición
            # min_position_index = data.Position.idxmin()  # Obtiene el índice donde la posición es mínima

            # pos = data.loc[min_position_index, 'Duration']
            # IndHalf = int(pos)
            #   print(min_position_index)
            #print(IndHalf)

        else:
            hindexes = data[data.Current > CurrentTh].index
            if len(hindexes) == 0:
                print('No Current Threshold crossed')
                IndHalf = int(data.shape[0] / 2)
            else:
                IndHalf = hindexes[-1]
            print(f'Time Transition {data.Time[IndHalf]} {IndHalf}')
        imax = data.Current.idxmax()
        imin = data.Current.idxmin()
        Cycle = {'Data': data,  # Dataframe with recorded data
                 'Cycle': ic,  # Cycle number
                 'tStart': dfData.Time[st],  # Cycle Start time
                 'PosStart': dfData.Position[st],  # Cycle Start position
                 'tEnd': dfData.Time[ed],  # Cycle End time
                 'PosEnd': dfData.Position[ed],  # Cycle End position
                 'IMax': data.Current[imax],  # Max current
                 'PosIMax': dfData.Position[imax],  # Position of max current
                 'IMin': data.Current[imin],  # Min current
                 'PosIMin': dfData.Position[imin],  # Position of min current
                 'VMax': data.Voltage.max(),  # Max voltage
                 'VMin': data.Voltage.min(),  # Min voltage
                 #  'tTransition': data.Time[IndHalf],  # Transition time between positive and negative current
                 #  'PosPMax': dfData.Power[:IndHalf].max(),  # Max positive power
                 # 'NegPMax': dfData.Power[IndHalf:].max(),  # Max negative power
                 #    'PosEnergy': simpson(y=data.Power[:IndHalf], x=data.Time[:IndHalf]),  # Positive energy
                 #   'NegEnergy': simpson(y=data.Power[IndHalf:], x=data.Time[IndHalf:]),  # Negative energy
                 'Energy': simpson(y=data.Power, x=data.Time),  #Total energy
                 }
        CyclesList.append(Cycle)

    return CyclesList
