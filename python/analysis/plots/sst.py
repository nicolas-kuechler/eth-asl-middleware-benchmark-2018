import matplotlib.pyplot as plt
import numpy as np

from plots import const

def nc(ax, df):
    clients = df.loc[:,'num_clients'].values
    sst_means = df.loc[:,'sst_rep_mean'].values
    sst_stds = df.loc[:,'sst_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    ax.errorbar(clients, sst_means, sst_stds, capsize=5, marker='.', markersize=10 ,label="server service time")


    ax.legend()
    ax.set_ylabel('Server Service Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+1)
    ax.set_ylim(0, max(sst_means)*1.1)
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
        sst_means = dfw.loc[:,'sst_rep_mean'].values
        sst_stds = dfw.loc[:,'sst_rep_std'].values

        ax.errorbar(clients, sst_means, sst_stds, capsize=const.capsize,
                                                    color=const.n_worker_color[n_worker],
                                                    marker='.',
                                                    markersize=const.markersize,
                                                    label=const.n_worker_label[n_worker])

        max_y.append(max(sst_means))
        max_x.append(max(clients))


    ax.legend()
    ax.set_ylabel(const.axis_label['sst'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)
    ax.set_xticks(clients)

def detail_nc(ax, df):
    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)
    max_y = []
    max_x = []


    clients = df.loc[:,'num_clients'].values
    sst0_means = df.loc[:,'sst0_rep_mean'].values
    sst0_stds = df.loc[:,'sst0_rep_std'].values

    sst1_means = df.loc[:,'sst1_rep_mean'].values
    sst1_stds = df.loc[:,'sst1_rep_std'].values

    sst2_means = df.loc[:,'sst2_rep_mean'].values
    sst2_stds = df.loc[:,'sst2_rep_std'].values

    ax.errorbar(clients, sst0_means, sst0_stds, capsize=const.capsize,
                                                color=const.sst_color["sst0"],
                                                marker='.',
                                                markersize=const.markersize,
                                                label=const.sst_label["sst0"])

    ax.errorbar(clients, sst1_means, sst1_stds, capsize=const.capsize,
                                                color=const.sst_color["sst1"],
                                                marker='.',
                                                markersize=const.markersize,
                                                label=const.sst_label["sst1"])

    ax.errorbar(clients, sst2_means, sst2_stds, capsize=const.capsize,
                                                color=const.sst_color["sst2"],
                                                marker='.',
                                                markersize=const.markersize,
                                                label=const.sst_label["sst2"])


    max_y = max(max(sst0_means),max(sst1_means),max(sst2_means))
    ax.legend()
    ax.set_ylabel(const.axis_label['sst'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+1)
    ax.set_ylim(0, max_y*1.1)
    ax.set_xticks(clients)


def mget(ax, df):
    mget_sizes = df.loc[:,'multi_get_size'].values
    sst_means = df.loc[:,'sst_rep_mean'].values
    sst_stds = df.loc[:,'sst_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    ax.errorbar(mget_sizes, sst_means, sst_stds, capsize=5, marker='.', markersize=10 ,label="server service time")

    ax.legend()
    ax.set_ylabel('Server Service Time [ms]')
    ax.set_xlabel('Multi Get Size')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, mget_sizes[-1]+1)
    ax.set_ylim(0, max(sst_means)*1.1)
    ax.set_xticks(mget_sizes)

def detail_mget(ax, df):
    mget_sizes = df.loc[:,'multi_get_size'].values
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)
    max_y = []
    max_x = []


    clients = df.loc[:,'num_clients'].values

    tsst_means = df.loc[:,'tsst_rep_mean'].values
    tsst_stds = df.loc[:,'tsst_rep_std'].values

    sst0_means = df.loc[:,'sst0_rep_mean'].values
    sst0_stds = df.loc[:,'sst0_rep_std'].values

    sst1_means = df.loc[:,'sst1_rep_mean'].values
    sst1_stds = df.loc[:,'sst1_rep_std'].values

    sst2_means = df.loc[:,'sst2_rep_mean'].values
    sst2_stds = df.loc[:,'sst2_rep_std'].values

    ax.errorbar(mget_sizes, tsst_means, tsst_stds, capsize=const.capsize,
                                                color=const.sst_color["tsst"],
                                                marker='.',
                                                markersize=const.markersize,
                                                label=const.sst_label["tsst"])

    ax.errorbar(mget_sizes, sst0_means, sst0_stds, capsize=const.capsize,
                                                color=const.sst_color["sst0"],
                                                marker='.',
                                                markersize=const.markersize,
                                                label=const.sst_label["sst0"])

    ax.errorbar(mget_sizes, sst1_means, sst1_stds, capsize=const.capsize,
                                                color=const.sst_color["sst1"],
                                                marker='.',
                                                markersize=const.markersize,
                                                label=const.sst_label["sst1"])

    ax.errorbar(mget_sizes, sst2_means, sst2_stds, capsize=const.capsize,
                                                color=const.sst_color["sst2"],
                                                marker='.',
                                                markersize=const.markersize,
                                                label=const.sst_label["sst2"])


    max_y = max(max(sst0_means),max(sst1_means),max(sst2_means), 10)
    ax.legend()
    ax.set_ylabel(const.axis_label['sst'])
    ax.set_xlabel(const.axis_label['mget_size'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, mget_sizes[-1]+1)
    ax.set_ylim(0, max_y*1.1)
    ax.set_xticks(mget_sizes)

def time(ax, df, server=None):
    for rep in np.unique(df.loc[:,'rep'].values):
        df_rep = df[df['rep']==rep]

        slots = df_rep.loc[:,'slot'].values
        assert(slots.shape[0] == np.unique(slots).shape[0])

        if server is None:
            means = df_rep.loc[:,'sst_mean'].values
            stds = df_rep.loc[:,'sst_std'].values
        elif server == 0:
            means = df_rep.loc[:,'sst0_mean'].values
            stds = df_rep.loc[:,'sst0_std'].values
        elif server == 1:
            means = df_rep.loc[:,'sst1_mean'].values
            stds = df_rep.loc[:,'sst1_std'].values
        elif server == 2:
            means = df_rep.loc[:,'sst2_mean'].values
            stds = df_rep.loc[:,'sst2_std'].values
        ax.errorbar(slots, means, stds, marker='.', markersize=const.markersize, capsize=const.capsize, label=f"rep={rep}")

    ax.legend()
    if server is None:
        ax.set_ylabel('Server Service Time [ms]')
        print('here1')
    else:
        print('here2')
        ax.set_ylabel(f'Server {server} Service Time [ms]')

    ax.set_xlabel(const.axis_label['slot'])

    ax.axvspan(0, const.min_slot_inclusive-0.5, alpha=0.5, color='grey')
    ax.axvspan(const.max_slot_inclusive+0.5, slots[-1]+2, alpha=0.5, color='grey')
    ax.set_xlim(0, slots[-1]+2)
    ax.set_ylim(0, max(means)+20)
    ax.set_xticks(slots)
