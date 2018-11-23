import matplotlib.pyplot as plt
import numpy as np

from plots import const

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

def mget(ax, df):
    mget_sizes = df.loc[:,'multi_get_size'].values
    qwt_means = df.loc[:,'qwt_rep_mean'].values
    qwt_stds = df.loc[:,'qwt_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    ax.errorbar(mget_sizes, qwt_means, qwt_stds, capsize=5, marker='.', markersize=10 ,label="queue waiting time")

    ax.legend()
    ax.set_ylabel('Queue Waiting Time [ms]')
    ax.set_xlabel('Multi Get Size')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, mget_sizes[-1]+1)
    ax.set_ylim(0, max(qwt_means)*1.1)
    ax.set_xticks(mget_sizes)

def time(ax, df):
    for rep in np.unique(df.loc[:,'rep'].values):
        df_rep = df[df['rep']==rep]

        slots = df_rep.loc[:,'slot'].values
        assert(slots.shape[0] == np.unique(slots).shape[0])

        means = df_rep.loc[:,'qwt_mean'].values
        stds = df_rep.loc[:,'qwt_std'].values
        ax.errorbar(slots, means, stds, marker='.', markersize=const.markersize, capsize=const.capsize, label=f"rep={rep}")

    ax.legend()
    ax.set_ylabel('Queue Waiting Time [ms]')
    ax.set_xlabel(const.axis_label['slot'])

    ax.axvspan(0, const.min_slot_inclusive- 0.5, alpha=0.5, color='grey')
    ax.axvspan(const.max_slot_inclusive+ 0.5, slots[-1]+2, alpha=0.5, color='grey')
    ax.set_xlim(0, slots[-1]+2)
    ax.set_ylim(0, max(means)+20)
    ax.set_xticks(slots)
