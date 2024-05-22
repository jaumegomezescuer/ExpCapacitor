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

dfData = pd.read_pickle(FileIn)
#dfDatas = dfDatass.query("Cycle > 0")
dfData = dfData.query("Cycle <8")

for index, r in dfData.iterrows():
    cyData = r.Data
    pos = cyData.Position

# %% Plot experiments comparison
PlotPars = ('IMax',
            'VMax',
           )

fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='Cap',
                            hueVar='TribuId',
                            PltFunt=sns.scatterplot)
fig.suptitle('Tribu Comparison')
fig.tight_layout()
PDF.savefig(fig)

PlotPars = ('IMax',

            'VMax',

            )
fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='Cap',
                            hueVar='Cycle',
                            PltFunt=sns.scatterplot)
fig.suptitle('Maximum peak Data')
fig.tight_layout()
PDF.savefig(fig)

PlotPars = ('IMin',
            'VMin')

fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='Cap',
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
             y='PosEnergy',
             ax=ax1,
             label='PosEnergy')
sns.lineplot(data=dSel,
             x='Imp',
             y='NegEnergy',
             ax=ax1,
             label='NegEnergy')
sns.lineplot(data=dSel,
             x='Imp',
             y='Energy',
             ax=ax1,
             marker='o')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('Impedance (Ohm)')
ax1.set_ylabel('Energy per cycle (J)')
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


dfAverages = dfData.groupby('Imp').agg({
    #  'PosEnergy': 'mean',
    # 'NegEnergy': 'mean',
    'Energy': 'mean'
}).reset_index()

# Exportar el DataFrame a un archivo Excel
output_file = 'average_energy_values.xlsx'
dfAverages.to_excel(output_file, index=False)

# %% Plot experiment time traces


VarColors = {
    'Voltage': {'LineKwarg': {'color': 'r',
                              },
                'Limits': (-0.5, 8),
                'Label': 'Voltage [V]'
                },
    'Current': {'LineKwarg': {'color': 'b',
                              },
                'Limits': (-15, 15),
                'Factor': 1e6,
                'Label': 'Current [uA]'
                },
    'Position': {'LineKwarg': {'color': 'k',
                               'linestyle': 'dashed',
                               'linewidth': 0.5,
                               },
                 # 'Limits': (-5, 5),
                 'Label': 'Position [mm]'
                 },
    'Force': {'LineKwarg': {'color': 'g',
                            'linestyle': 'dashed',
                            'linewidth': 0.5,
                            },
              # 'Limits': (-5, 5),
              'Label': 'Force [N]'
              },

    'Power': {'LineKwarg': {'color': 'purple',
                            },
              'Factor': 1e6,
              'Limits': (0, 25),
              'Label': 'Power [uW]'},
}


dSel = dfData
#XLabel = 'Time (s)'
for ex, dExp in dSel.groupby('ExpId'):
    fig, (axtime, axpos) = plt.subplots(2, 1, figsize=(11, 7))
    for gn, df in dExp.groupby('Capacitorid'):
        # plot time traces
        AxsDict, _ = GenFigure(dfData=df.iloc[0].Data,
                               xVar='Time',
                               xLabel ='Time (s)',
                               PlotColumns=VarColors,
                               axisFactor=0.15,
                               ax=axtime)
        for index, r in df.iterrows():
            Data = r.Data
            for var, ax in AxsDict.items():
                if 'Factor' in VarColors[var]:
                    ptdata = Data[var] * VarColors[var]['Factor']
                else:
                    ptdata = Data[var]
                ax.plot(Data['Time'], ptdata, **VarColors[var]['LineKwarg'])
                ax.axvline(x=r.tTransition, color='y')
            ax.set_xlabel('Time')

        # plot position traces
        # XLabel = 'Position (mm)'
        AxsDict, _ = GenFigure(dfData=df.iloc[0].Data,
                               xVar='Position',
                               xLabel ='Position (mm)',
                               PlotColumns=VarColors,
                               axisFactor=0.15,
                               ax=axpos)
        for index, r in df.iterrows():
            Data = r.Data
            for var, ax in AxsDict.items():
                if 'Factor' in VarColors[var]:
                    ptdata = Data[var] * VarColors[var]['Factor']
                else:
                    ptdata = Data[var]
                ax.plot(Data['Position'], ptdata, **VarColors[var]['LineKwarg'])
            ax.set_xlabel('Position')
            ax.set_xlim(0, 2)

        fig.suptitle(f'Experiment: {r.ExpId}, Tribu: {r.TribuId}, Capacitance: {r.Cap},Impedance:{r.Imp}')
        fig.tight_layout()
        PDF.savefig(fig)
        plt.close(fig)




PDF.close()
