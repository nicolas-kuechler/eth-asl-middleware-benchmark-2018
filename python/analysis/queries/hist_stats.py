import re
import pandas as pd
import numpy as np

def aggregate_hist(df, bin_size=0.5, bin_max=20.0):

    bins = np.arange(0.0, bin_max, bin_size)
    bins = np.concatenate([bins, np.array([df['rt'].max()])])

    d = {}

    data_origin = df['data_origin'].unique()

    for rep in df.rep.unique():
        df_rep = df[df["rep"]==rep]

        cuts = pd.cut(df_rep["rt"], bins)
        d[rep] = df_rep.groupby(cuts).agg({"rt_freq":'sum'}).rename(index=str, columns={"rt_freq": f"rt_freq_rep{rep}"})

    df = pd.concat([d[0], d[1], d[2]], axis=1, sort=False)

    df['rt_freq_mean'] = df.loc[: , "rt_freq_rep0":"rt_freq_rep2"].mean(axis=1)
    df['rt_freq_std'] = df.loc[: , "rt_freq_rep0":"rt_freq_rep2"].std(axis=1)
    df = df.reset_index()
    df = df.rename(index=str, columns={"rt":"rt_bin"})

    df['rt_bin_low'] = df.apply(lambda row: float(re.split('\(|,\s|\]',row["rt_bin"])[1]) ,axis=1)
    df['rt_bin_high'] = df.apply(lambda row: float(re.split('\(|,\s|\]',row["rt_bin"])[2]) ,axis=1)
    df['rt_bin_avg'] = df.loc[: , "rt_bin_low":"rt_bin_high"].mean(axis=1)

    df['data_origin'] = df.apply(lambda row: data_origin[0] ,axis=1)

    return df
