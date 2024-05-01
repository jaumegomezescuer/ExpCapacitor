from math import ceil

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from TryPy.PlotData import PlotScalarValues, GenFigure

PDF = PdfPages('./Reports/DataSetsAnalysis.pdf')

# %% Load data

FileIn = './DataSets/Cycles.pkl'

dfDatass = pd.read_pickle(FileIn)
dfDatas = dfDatass.query("Cycle > 0")
dfData = dfDatas.query("Cycle <3")

# %% Plot experiments comparison

PlotPars = ('IMax',
            'VMax',
           )

fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='Imp',
                            hueVar='TribuId',
                            PltFunt=sns.scatterplot)
fig.suptitle('Tribu Comparison')
fig.tight_layout()
PDF.savefig(fig)

PlotPars = ('IMax',
            'PosIMax',
            'VMax',

            )
fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='Imp',
                            hueVar='Cycle',
                            PltFunt=sns.scatterplot)
fig.suptitle('Maximum peak Data')
fig.tight_layout()
PDF.savefig(fig)

PlotPars = ('IMin',
            'PosIMin',
            'VMin',

           )

fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='Imp',
                            hueVar='Cycle',
                            PltFunt=sns.scatterplot)
fig.suptitle('Minimum peak Data')
fig.tight_layout()
PDF.savefig(fig)

# %% compare positive and negative peaks

dSel = dfData
fig, ax1 = plt.subplots()

sns.lineplot(data=dSel,
             x='Imp',
             y='Energy',
             ax=ax1,
             marker='o')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('Impedance (Ohm)')
ax1.set_ylabel('Energy (J)')
ax1.legend()
ax2 = ax1.twiny()
ax2.invert_xaxis()
ax2.set_xlabel('Capacitance (Farads)')


sns.lineplot(data=dSel,
             x='Cap',
             y='Energy',
             ax=ax2,
             marker='o',
             color='orange',
             label='Energy')
ax2.set_xscale('log')
ax2.set_yscale('log')

PDF.savefig(fig)



# %% Plot experiment time traces

VarColors = {
    'Voltage': 'r',
    'Current': 'b',
    'Position': 'k',
    'Force': 'g',
    'Power': 'purple'}

dSel = dfData

for ex, dExp in dSel.groupby('ExpId'):
    fig, (axtime, axpos) = plt.subplots(2, 1, figsize=(11, 7))
    for gn, df in dExp.groupby('Capacitorid'):
        # plot time traces
        AxsDict, _ = GenFigure(dfData=df.loc[1, 'Data'],
                               xVar='Time',
                               PlotColumns=VarColors,
                               axisFactor=0.15,
                               ax=axtime)
        for index, r in df.iterrows():
            Data = r.Data
            for col, ax in AxsDict.items():
                ax.plot(Data['Time'], Data[col], color=VarColors[col],
                        alpha=0.5)

                ax.set_xlabel('Time')

        # plot position traces
        AxsDict, _ = GenFigure(dfData=df.loc[1, 'Data'],
                               xVar='Position',
                               PlotColumns=VarColors,
                               axisFactor=0.15,
                               ax=axpos)
        for index, r in df.iterrows():
            Data = r.Data
            for col, ax in AxsDict.items():
                ax.plot(Data['Position'], Data[col], color=VarColors[col],
                        alpha=0.5)
                ax.set_xlabel('Position')
                ax.set_xlim(0, 2)

        fig.suptitle(f'Experiment: {r.ExpId}, Tribu: {r.TribuId}, Capacitance: {r.Cap},Impedance:{r.Imp}')
        fig.tight_layout()
        PDF.savefig(fig)
        plt.close(fig)

PDF.close()
