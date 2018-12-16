import matplotlib.pyplot as plt
import numpy as np

from plots import const

def nc(ax, df):
    clients = df.loc[:,'num_clients'].values
    queue_means = df.loc[:,'queue_rep_mean'].values
    queue_stds = df.loc[:,'queue_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    ax.errorbar(clients, queue_means, queue_stds, capsize=const.capsize,
                                                    color=const.color_d['qwt'][1],
                                                    marker='.',
                                                    markersize=const.markersize)


    ax.set_ylabel(const.axis_label['queue_size'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(max(0, min(clients)-2), clients[-1]+2)
    ax.set_ylim(0, max(6, max(queue_means)*1.1))
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
        queue_means = dfw.loc[:,'queue_rep_mean'].values
        queue_stds = dfw.loc[:,'queue_rep_std'].values

        ax.errorbar(clients, queue_means, queue_stds, capsize=const.capsize,
                                                        color=const.n_worker_color[n_worker],
                                                        marker='.',
                                                        markersize=const.markersize,
                                                        label=const.n_worker_label[n_worker])

        max_y.append(max(queue_means))
        max_x.append(max(clients))


    ax.legend()
    ax.set_ylabel(const.axis_label['queue_size'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(max(0, min(clients)-2), max(max_x)+2)
    ax.set_ylim(0, max(6, max(max_y)*1.1))
    ax.set_xticks(clients)

def mget(ax, df):
    mget_sizes = df.loc[:,'multi_get_size'].values
    queue_means = df.loc[:,'queue_rep_mean'].values
    queue_stds = df.loc[:,'queue_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    ax.errorbar(mget_sizes, queue_means, queue_stds, capsize=5, marker='.', markersize=10 ,label="queue size")

    ax.legend()
    ax.set_ylabel('Queue Size')
    ax.set_xlabel('Multi Get Size')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(max(0, min(mget_sizes)-1), mget_sizes[-1]+1)
    ax.set_ylim(0, max(6,max(queue_means)*1.1))
    ax.set_xticks(mget_sizes)

def queueing_model(ax, df):
    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    assert(n_workers.shape[0]==1)

    clients = df.loc[:,'num_clients'].values

    meas_queue = 2 * df.loc[:,'meas_n_jobs_queue'].values
    mm1_queue = df.loc[:,'mm1_n_jobs_queue'].values
    mmm_queue = df.loc[:,'mmm_n_jobs_queue'].values

    ax.plot(clients, meas_queue,  color=const.queueing_color["meas"],
                                            marker='.',
                                            markersize=const.markersize,
                                            label=const.queueing_label["meas"])

    ax.plot(clients, mm1_queue,  color=const.queueing_color["mm1"],
                                            linestyle='None',
                                            marker='x',
                                            markersize=const.markersize+2,
                                            label=const.queueing_label["mm1"])

    ax.plot(clients, mmm_queue,  color=const.queueing_color["mmm"],
                                            linestyle='None',
                                            marker='x',
                                            markersize=const.markersize+2,
                                            label=const.queueing_label["mmm"].replace("m", f"{n_workers[0]*2}"))

    ax.legend()

    ax.set_ylabel(const.axis_label['queue_size'])
    ax.set_xlabel(const.axis_label['number_of_clients'])


    ax.set_xlim(max(0, min(clients)-2), max(clients)+2)
    ax.set_ylim(0, max(50,max(np.concatenate([meas_queue, mm1_queue, mmm_queue]))*1.1))
    ax.set_xticks(clients)

def time(ax, df):
    for rep in np.unique(df.loc[:,'rep'].values):
        df_rep = df[df['rep']==rep]

        slots = df_rep.loc[:,'slot'].values
        assert(slots.shape[0] == np.unique(slots).shape[0])

        means = df_rep.loc[:,'queue_size_mean'].values
        ax.plot(slots, means, marker='.', markersize=const.markersize, label=f"rep={rep}")

    ax.legend()
    ax.set_ylabel('Queue Size')
    ax.set_xlabel(const.axis_label['slot'])

    ax.axvspan(0, const.min_slot_inclusive- 0.5, alpha=0.5, color='grey')
    ax.axvspan(const.max_slot_inclusive+ 0.5, slots[-1]+2, alpha=0.5, color='grey')
    ax.set_xlim(0, slots[-1]+2)
    ax.set_ylim(0, max(means)+20)
    ax.set_xticks(slots)
