import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from plots import const

def nc(ax, df):

    n_workers = df.loc[:,'n_worker_per_mw'].unique()
    assert(n_workers.shape[0]==1)

    clients = df.loc[:,'num_clients'].values
    nt_utils = df.loc[:,'nt_util'].values * 100
    wt_utils = df.loc[:,'wt_util'].values * 100

    if df['workload'].unique()[0] == 'write-only':
        s0_utils = df.loc[:,'s0_util'].values * 100
        s1_utils = df.loc[:,'s1_util'].values * 100
        s2_utils = df.loc[:,'s2_util'].values * 100

        s_utils = np.maximum.reduce([s0_utils,s1_utils,s2_utils])
    else:
        s_utils = df.loc[:,'s_util'].values * 100

    # plot net-thread utilization
    ax.plot(clients, nt_utils, color=const.color_d['ntt'][0],
                                marker='.',
                                markersize=const.markersize,
                                label="net-thread decoding")

    ax.plot(clients, wt_utils, color=const.color_d['wtt'][0],
                                marker='.',
                                markersize=const.markersize,
                                label="worker-thread processing")

    ax.plot(clients, s_utils, color=const.color_d['sst'][0],
                                marker='.',
                                markersize=const.markersize,
                                label="worker-thread server service time")

    # TODO [nku] decide on legend
    ax.legend()
    ax.set_ylabel(const.axis_label['util'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.set_xlim(max(0, clients[0]-1), clients[-1]+1)
    ax.set_ylim(0, 102)
    ax.set_xticks(clients)

def detail_nc(ax, df):

    n_workers = df.loc[:,'n_worker_per_mw'].unique()
    assert(n_workers.shape[0]==1)

    clients = df.loc[:,'num_clients'].values
    nt_utils = df.loc[:,'nt_util'].values * 100

    wttotal_utils = df.loc[:,'wttotal_util'].values * 100

    if df['workload'].unique()[0] == 'write-only':
        s0_utils = df.loc[:,'s0_util'].values * 100
        s1_utils = df.loc[:,'s1_util'].values * 100
        s2_utils = df.loc[:,'s2_util'].values * 100

        s_utils = np.maximum.reduce([s0_utils,s1_utils,s2_utils])
        wt_utils = df.loc[:,'wt_sstmax_util'].values * 100

    else:
        wt_utils = df.loc[:,'wt_util'].values * 100
        s_utils = df.loc[:,'s_util'].values * 100

    # plot net-thread utilization
    # ax.plot(clients, nt_utils, color=const.rt_component_color['ntt'],
    #                             marker='.',
    #                             markersize=const.markersize,
    #                             label="net-thread decoding")
    #
    # ax.plot(clients, wt_utils, color=const.rt_component_color['wtt'],
    #                             marker='.',
    #                             markersize=const.markersize,
    #                             label="worker-thread processing")



    ax.plot(clients, s0_utils, color=const.sst_color['sst0'],
                                marker='.',
                                markersize=const.markersize,
                                label="worker-thread server 1 service time")

    ax.plot(clients, s1_utils, color=const.sst_color['sst1'],
                                marker='.',
                                markersize=const.markersize,
                                label="worker-thread server 2 service time")

    ax.plot(clients, s2_utils, color=const.sst_color['sst2'],
                                marker='.',
                                markersize=const.markersize,
                                label="worker-thread server 3 service time")

    ax.plot(clients, wttotal_utils, color="grey",
                                    marker='.',
                                    markersize=const.markersize,
                                    label="worker-thread total time")

     #	wt_util 	s_util 	s0_util 	s1_util 	s2_util

    # TODO [nku] decide on legend
    ax.legend()
    ax.set_ylabel(const.axis_label['util'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.set_xlim(0, clients[-1]+2)
    ax.set_ylim(0, 102)
    ax.set_xticks(clients)

def network_queue(ax, df):

    df = df[df['num_clients']<288]

    for mw in df.loc[:,'n_mw'].unique():
        dfmw = df[df['n_mw']==mw]
        for dev in sorted(dfmw.loc[:,'device'].unique(), reverse=True):
            df_dev = dfmw[dfmw['device']==dev]

            clients = df_dev.loc[:,'num_clients'].values
            utils = df_dev.loc[:,'utilization'].values * 100

            n_mw = df_dev['n_mw'].unique()[0]
            if n_mw > 1:
                label = f"{n_mw} MWs - {dev}"
                colors = const.noq_color['2mw']
            else:
                label = f"{n_mw} MW  - {dev}"
                colors = const.noq_color['1mw']

            if dev == 'net-thread':
                color = colors[0]
            else:
                color = colors[1]

            # plot net-thread utilization
            ax.plot(clients, utils, #color=const.rt_component_color['ntt'],
                                        marker='.',
                                        markersize=const.markersize,
                                        label=label, color=color)




    # TODO [nku] decide on legend
    ax.legend(loc='center right')
    #ax.legend(loc='upper left')
    ax.set_ylabel(const.axis_label['util'])
    ax.set_xlabel(const.axis_label['number_of_clients'])

    ax.set_xlim(0, clients[-1]+2)
    ax.set_ylim(0, 102)
    ax.set_xticks(clients)
