import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from plots import const
from queries import query_mw
from plots import rt, tp, qwt, ntt, wtt, sst, queue

pd.options.display.max_columns = None
output_folder = "./../../exp_plots"

def generate(plot_func, df, suite=None, name=None, figsize=2, opt=None, n_fig=2):


    width_pt = 452.9679 # measured from latex
    inches_per_pt = 1.0/72.27
    golden_mean = (np.sqrt(5)-1.0)/2.0         # Aesthetic ratio
    fig_width2 = 0.49 * width_pt*inches_per_pt  # width in inches
    fig_height2 = fig_width2*golden_mean       # height in inches

    #plt.rc('font', family='serif', serif='Times')
    #plt.rc('text', usetex=False, size=6)
    #plt.rc('xtick', labelsize=4.5)
    #plt.rc('ytick', labelsize=4.5)
    #plt.rc('legend', fontsize=5)
    #plt.rc('axes', labelsize=8)

    #print(plt.rcParams.keys())

    params = {'backend': 'ps',
                'axes.labelsize': 12,
                'font.size': 9,
                'legend.fontsize': 9,
                'xtick.labelsize': 8,
                'ytick.labelsize': 8,
                'text.usetex': False,
                'figure.figsize': (7, 4)}
    plt.rcParams.update(params)

    if n_fig == 3:
        params = {'backend': 'ps',
                    'axes.labelsize': 14,
                    'font.size': 12,
                    'legend.fontsize': 10,
                    'xtick.labelsize': 10,
                    'ytick.labelsize': 10,
                    'text.usetex': False,
                    'figure.figsize': (7, 4)}
        plt.rcParams.update(params)


    #fig, ax = plt.subplots()
    fig, ax = plt.subplots()#const.figsize[figsize]) # figsize width, height in inches
    if opt is None:
        plot_func(ax, df)
    else:
        plot_func(ax, df, opt)

    if name is not None:
        assert(suite is not None)
        path = f"{output_folder}/{suite}"
        try:
            os.makedirs(path)
        except OSError:
            pass

        fig.savefig(f"{path}/{name}.pdf", bbox_inches='tight')
    plt.show()

def generate_latex(latex_str, suite=None, name=None):
    path = f"{output_folder}/{suite}"
    try:
        os.makedirs(path)
    except OSError:
        pass

    with open(f"{path}/{name}.tex", "w+") as f:
        f.write(latex_str)


def dashboard_nc(df):
    generate(qwt.nc_w, df)
    generate(ntt.nc_w, df)
    generate(wtt.nc_w, df)
    generate(sst.nc_w, df)
    generate(queue.nc_w, df)

def dashboard_mget(df):
    generate(tp.mget, df)
    generate(rt.mget, df)
    generate(qwt.mget, df)
    generate(ntt.mget, df)
    generate(wtt.mget, df)
    generate(sst.mget, df)
    generate(queue.mget, df)

def export(df, dir, exp_name, suffix=""):
    path = f"./../../data/{exp_name}/{dir}"
    try:
        os.makedirs(path)
    except OSError:
        pass
    file = f"{path}/processed{suffix}.log"
    df.to_csv(file, sep=',')

    print(f"Saved Data: {file}")

def dashboard_time(suite, exp_name, n_worker=None, n_clients=None):
    df = query_mw.load_df_by_slot(suite=suite ,exp=exp_name)
    for n_mw in np.unique(df.loc[:,'n_middleware_vm'].values):
        for n_server in np.unique(df.loc[:,'n_server_vm'].values):
            for n_w in np.unique(df.loc[:,'n_worker_per_mw'].values):
                if n_worker is not None and n_worker != n_w:
                    continue
                for op_type in np.unique(df.loc[:,'op_type'].values):
                    for num_clients in np.unique(df.loc[:,'num_clients'].values):
                        if n_clients is not None and n_clients != num_clients:
                            continue
                        for mget_size in np.unique(df.loc[:,'multi_get_size'].values):
                            df_filtered = df[(df['n_middleware_vm']==n_mw)&(df['n_server_vm']==n_server)&(df['n_worker_per_mw']==n_w) & (df['op_type']==op_type) & (df['num_clients']==num_clients) & (df['multi_get_size']==mget_size)]
                            if df_filtered.shape[0]== 0:
                                continue
                            print(f"n_w={n_w}   op_type={op_type}  num_clients={num_clients}   mget_size={mget_size}")
                            generate(tp.time, df_filtered)
                            generate(rt.time, df_filtered)
                            generate(qwt.time, df_filtered)
                            generate(ntt.time, df_filtered)
                            generate(wtt.time, df_filtered)
                            generate(sst.time, df_filtered)
                            generate(sst.time, df_filtered, opt=0)
                            generate(sst.time, df_filtered, opt=1)
                            generate(sst.time, df_filtered, opt=2)
                            generate(queue.time, df_filtered)
