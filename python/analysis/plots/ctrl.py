import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from plots import rt, tp, qwt, ntt, wtt, sst, queue

pd.options.display.max_columns = None
output_folder = "./../../exp_plots"

def generate(plot_func, df, suite=None, name=None):
    plt.rc('font', family='serif', serif='Times')
    plt.rc('text', usetex=False)
    plt.rc('xtick', labelsize=12)
    plt.rc('ytick', labelsize=12)
    plt.rc('axes', labelsize=12)

    fig, ax = plt.subplots()
    plot_func(ax, df)

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
    generate(qwt.mget, df)
    generate(ntt.mget, df)
    generate(wtt.mget, df)
    generate(sst.mget, df)
    generate(queue.mget, df)
