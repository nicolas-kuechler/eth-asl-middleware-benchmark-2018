import matplotlib.pyplot as plt
import numpy as np



def nc(ax, df):
    clients = df.loc[:,'num_clients'].values
    qwt_means = df.loc[:,'qwt_rep_mean'].values
    qwt_stds = df.loc[:,'qwt_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    ax.errorbar(clients, qwt_means, qwt_stds, capsize=5, marker='.', markersize=10 ,label="queue waiting time")


    ax.legend()
    ax.set_ylabel('Queue Waiting Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+1)
    ax.set_ylim(0, max(qwt_means)*1.1)
    ax.set_xticks(clients)


def nc_w(ax, df):
    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)
    max_y = []
    max_x = []

    for n_worker in n_workers:
        dfw = df[df["n_worker_per_mw"]==n_worker]

        clients = dfw.loc[:,'num_clients'].values
        qwt_means = dfw.loc[:,'qwt_rep_mean'].values
        qwt_stds = dfw.loc[:,'qwt_rep_std'].values

        ax.errorbar(clients, qwt_means, qwt_stds, capsize=5, marker='.', markersize=10, label=f"w={n_worker}")

        max_y.append(max(qwt_means))
        max_x.append(max(clients))


    ax.legend()
    ax.set_ylabel('Queue Waiting Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)
    ax.set_xticks(clients)
