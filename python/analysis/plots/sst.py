import matplotlib.pyplot as plt
import numpy as np



def nc(ax, df):
    clients = df.loc[:,'num_clients'].values
    stt_means = df.loc[:,'stt_rep_mean'].values
    sst_stds = df.loc[:,'stt_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    ax.errorbar(clients, stt_means, stt_stds, capsize=5, marker='.', markersize=10 ,label="server service time")


    ax.legend()
    ax.set_ylabel('Server Service Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+1)
    ax.set_ylim(0, max(sst_means)*1.1)


def nc_w(ax, df):
    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)
    max_y = []
    max_x = []

    for n_worker in n_workers:
        dfw = df[df["n_worker_per_mw"]==n_worker]

        clients = dfw.loc[:,'num_clients'].values
        sst_means = dfw.loc[:,'sst_rep_mean'].values
        sst_stds = dfw.loc[:,'sst_rep_std'].values

        ax.errorbar(clients, sst_means, sst_stds, capsize=5, marker='.', markersize=10, label=f"w={n_worker}")

        max_y.append(max(sst_means))
        max_x.append(max(clients))


    ax.legend()
    ax.set_ylabel('Server Service Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)
