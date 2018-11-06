import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

pd.options.display.max_columns = None
output_folder = "./../../exp_plots"


def generate(plot_func, df, suite=None, name=None):
    fig, ax = plt.subplots()
    plot_func(ax, df)

    if name is not None:
        assert(suite is not None)
        path = f"{output_folder}/{suite}"
        try:
            os.makedirs(path)
        except OSError:
            pass

        fig.savefig(f"{path}/{name}.pdf")
    plt.show()

def t1(ax, df):

    clients = df.loc[:,'num_clients'].values
    throughput_means = df.loc[:,'throughput_rep_mean'].values
    throughput_stds = df.loc[:,'throughput_rep_std'].values

    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    rt_means = df.loc[:,'rt_rep_mean'].values


    throughput_interactive_law = clients / rt_means * 1000

    ax.errorbar(clients, throughput_means, throughput_stds, capsize=5, marker='.', markersize=10 ,label="throughput")
    ax.plot(clients, throughput_interactive_law, linestyle='--', label="interactive law")

    ax.legend()
    ax.set_ylabel('Throughput [req/sec]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+1)
    ax.set_ylim(0, max(throughput_means+throughput_interactive_law)*1.1)

def rt1(ax, df):

    clients = df.loc[:,'num_clients'].values
    throughput_means = df.loc[:,'throughput_rep_mean'].values
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)


    rt_means = df.loc[:,'rt_rep_mean'].values
    rt_stds = df.loc[:,'rt_rep_std'].values

    rt_interactive_law = clients / throughput_means * 1000

    ax.errorbar(clients, rt_means, rt_stds, capsize=5, marker='.', markersize=10,label="response time")
    ax.plot(clients, rt_interactive_law, linestyle='--', label="interactive law")



    ax.legend()
    ax.set_ylabel('Response Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, clients[-1]+1)
    ax.set_ylim(0, max(rt_means+rt_interactive_law)*1.1)

def t2(ax,df):

    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)
    max_y = []
    max_x = []

    for n_worker in n_workers:
        dfw = df[df["n_worker_per_mw"]==n_worker]

        clients = dfw.loc[:,'num_clients'].values
        throughput_means = dfw.loc[:,'throughput_rep_mean'].values
        throughput_stds = dfw.loc[:,'throughput_rep_std'].values

        rt_means = dfw.loc[:,'rt_rep_mean'].values

        throughput_interactive_law = clients / rt_means * 1000

        ax.plot(clients, throughput_interactive_law, linestyle='--',label=f"w={n_worker}")
        ax.errorbar(clients, throughput_means, throughput_stds, capsize=5, marker='.', markersize=10, label=f"w={n_worker}")

        max_y.append(max(throughput_means + throughput_interactive_law))
        max_x.append(max(clients))


    ax.legend()
    ax.set_ylabel('Throughput [req/sec]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)

def rt2(ax,df):
    n_workers = np.unique(df.loc[:,'n_worker_per_mw'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    max_y = []
    max_x = []

    for n_worker in n_workers:
        dfw = df[df["n_worker_per_mw"]==n_worker]

        clients = dfw.loc[:,'num_clients'].values
        throughput_means = dfw.loc[:,'throughput_rep_mean'].values


        rt_means = dfw.loc[:,'rt_rep_mean'].values
        rt_stds = dfw.loc[:,'rt_rep_std'].values

        rt_interactive_law = clients / throughput_means * 1000

        ax.errorbar(clients, rt_means, rt_stds, capsize=5, marker='.', markersize=10, label=f"w={n_worker}")
        ax.plot(clients, rt_interactive_law, linestyle='--',label=f"w={n_worker}")

        max_y.append(max(rt_means+rt_interactive_law))
        max_x.append(max(clients))

    ax.legend()
    ax.set_ylabel('Response Time [ms]')
    ax.set_xlabel('Number of Clients')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)

def rt3(ax,df):
    stats = np.unique(df.loc[:,'stat'].values)
    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    max_y = []
    max_x = []

    for stat in stats:
        dfs = df[df["stat"]==stat]

        mget_sizes = dfs.loc[:,'multi_get_size'].values
        rts = dfs.loc[:,'rt'].values

        ax.plot(mget_sizes, rts, marker='.', markersize=10, label=f"{stat}")


        max_y.append(max(rts))
        max_x.append(max(mget_sizes))

    ax.legend()
    ax.set_ylabel('Response Time [ms]')
    ax.set_xlabel('Multi Get Size')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_xlim(0, max(max_x)+1)
    ax.set_ylim(0, max(max_y)*1.1)


def rt4(ax,df):

    bins =  np.arange(0.0, 20.0, 0.5)

    ylim = 28000

    rts = df.loc[:,'rt'].values
    rt_freqs = df.loc[:,'rt_freq'].values


    data_origin = np.unique(df.loc[:,'data_origin'].values)
    assert(data_origin.shape[0]==1)

    plt.hist(rts, weights=rt_freqs, bins=bins)

    ax.set_ylabel('Frequency')
    ax.set_xlabel('Response Time [ms]')

    ax.text(0.95, 0.05, data_origin[0], ha='center', va='center', transform=ax.transAxes, color='grey')

    ax.set_ylim(0, ylim)
