import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages

from TryPy.Calculations import ExtractCycles
from TryPy.LoadData import Loadfiles
from TryPy.PlotData import GenFigure

import seaborn as sns

mpl.use("QtAgg")
plt.close('all')
plt.ion()

DataDir = './Data/'
ExpDef = './Data/Experimentss.ods'
CapDef = './Data/CapacitorDescription1.ods'

PDF = PdfPages('./Reports/LoadReport.pdf')
OutFile = './DataSets/Cycles.pkl'

FindCyclesBy = 'Position'

# %% Load Experiments
dfExp = pd.read_excel(ExpDef)
dfLoads = pd.read_excel(CapDef)
dfLoads.Cap = (dfLoads.Cap * 10**(-9) )  # to convert into Ohms
dfExps = dfExp.query("TribuId == ('SwTENG-CB')")
# dfExps = dfExp.query("ExpId == '0803-")
# dfExps = dfExp.query("ExpId == '0403-RL034'")




# %% Add Loads Fields
LoadsFields = ('Cap', 'Gain')
for lf in LoadsFields:
    if lf not in dfExps.columns:
        dfExps.insert(1, lf, None)

for index, r in dfExps.iterrows():
    if r.Capacitorid in dfLoads.Capacitorid.values:
        for lf in LoadsFields:
            dfExps.loc[index, lf] = dfLoads.loc[dfLoads.Capacitorid == r.Capacitorid, lf].values
    else:
        print(f'Warning Load {r.Capacitorid} not found !!!!')
        dfExps.drop(index, inplace=True)
        print("Deleted")

# %% load data files

# create abs path
for index, r in dfExps.iterrows():
    dfExps.loc[index, 'DaqFile'] = os.path.join(DataDir, r.DaqFile)
    dfExps.loc[index, 'MotorFile'] = os.path.join(DataDir, r.MotorFile)

# %% Extract Cycles

plt.ioff()
dfCycles = pd.DataFrame()
for index, r in dfExps.iterrows():
    print(f'Processing: {r.ExpId}')

    dfData = Loadfiles(r)
    # Reference position and force
    dfData.Position = dfData.Position - dfData.Position.min()
    dfData.Force = -dfData.Force
    dfData = dfData[dfData['Voltage'] <= 10]


    # dfData = dfData.query('Voltage < 10')
    # dfData = dfData.query('Time > 1')

    # Calculate Contact Position
    if FindCyclesBy == 'Position':
        CyclesList = ExtractCycles(dfData,
                                   ContactPosition=r.ContactPosition,
                                   Latency=r.Latency,
                                   # CurrentTh=r.CurrentTh,
                                   CurrentTh=None,
                                   )
    else:
        CyclesList = ExtractCycles(dfData,
                                   ContactPosition=None,
                                   ContactForce=r.ContactForce,
                                   Latency=r.Latency,
                                   # CurrentTh=r.CurrentTh,
                                   CurrentTh=None,
                                   )

    # stack cycles
    for cy in CyclesList:
        cy.update(r.to_dict())
    dfCycle = pd.DataFrame(CyclesList)
    dfCycles = pd.concat([dfCycles, dfCycle])
    dfCycles = dfCycles.query("Cycle > 0")
    dfCycles = dfCycles.query("Cycle < 2")

    #  dfCycle = dfCycle.query("Cycle > 1")
    # dfFilteredCycle = dfCycle.query('Cycle > 0')
    filtered_cycles = [cy for cy in CyclesList if cy['Cycle'] > 0]
    last_cycle = CyclesList[-1]
    if last_cycle['Cycle'] > 0:
        filtered_cycles.append(last_cycle)
    #    filtered_cycles = [cy for cy in CyclesList if cy['Cycle'] > 0]

    # Generate Debug Figures
    XVar = 'Time'
    AxsDict, PlotCols = GenFigure(dfData, xVar=XVar, axisFactor=0.1, figsize=(12, 5))
    for col, ax in AxsDict.items():
        ax.set_xlabel(XVar)
        ax.plot(dfData[XVar], dfData[col], PlotCols[col])

    for cy in filtered_cycles:
        ax.axvline(x=cy['tStart'], color='y', linewidth=2)
        ax.axvline(x=cy['tEnd'], color='y', linestyle='-.', linewidth=2)
        ax.axvline(x=cy['tStart'] , color='y', linestyle='--', linewidth=1)
    fig = ax.get_figure()
    fig.suptitle(r.ExpId)
    fig.tight_layout()
    PDF.savefig(fig)

    XVar = 'Position'
    AxsDict, PlotCols = GenFigure(dfData, xVar=XVar, figsize=(10, 5))
    for col, ax in AxsDict.items():
        ax.set_xlabel(XVar)
        ax.plot(dfData[XVar], dfData[col], PlotCols[col])
    ax.set_xlim(0, np.mean([cy['PosStart'] for cy in filtered_cycles]))
    fig = ax.get_figure()
    fig.suptitle(r.ExpId)
    fig.tight_layout()
    PDF.savefig(fig)
    plt.close('all')

plt.ion()
PDF.close()
dfCycles['Imp'] = 1/(dfCycles['Cap'] )
dfCycles = dfCycles.astype({'Gain': float,
                            'Cap': float,
                            })

dfCycles.to_pickle(OutFile)

