from itertools import combinations
import pandas as pd
import numpy as np

from queries import query_mw, query_client

pd.options.mode.chained_assignment = None  # default='warn'

def load_2k_base_df(suite, exp_name, r_rep, factor_map, data_origin='mw'):

    """
    Example factor map with 3 factors:
    factor_map = {
    'n_server_vm':('S', {'1':-1, '3':1}),
    'n_middleware_vm':('M', {'1':-1, '2':1}),
    'n_worker_per_mw':('W', {'8':-1, '32':1})
    }

    """

    k_factors = len(factor_map)

    # load data by rep
    if data_origin=='mw':
        df, config_cols, _ = query_mw.load_df_by_rep(suite=suite, exp=exp_name)
        df = df.rename(index=str, columns={"throughput_slot_mean": "throughput", "rt_slot_mean": "rt"})
    elif data_origin == 'client':
        df, config_cols, _ = query_client.load_df_by_rep(suite=suite, exp=exp_name)
        df = df.rename(index=str, columns={"throughput_mean": "throughput", "rt_mean": "rt"})
    else:
        raise ValueError(f"Unknown data origin: {data_origin}")

    # aggregate over repetitions by packing the individual measurements in a list
    config_cols.remove("rep")
    df = df.groupby(level=config_cols).agg({'throughput':(lambda x: list(x)),
                                           'rt':(lambda x: list(x))})
    df = df.reset_index()


    # create column headers
    tp_cols = [f"tp_y{i}" for i in range(1, k_factors+1)]
    rt_cols = [f"rt_y{i}" for i in range(1, k_factors+1)]
    tp_error_cols = [f"tp_e{i}" for i in range(1,k_factors+1)]
    rt_error_cols = [f"rt_e{i}" for i in range(1,k_factors+1)]
    factor_base_cols = [i[0] for i in factor_map.values()]
    factor_interaction_cols= ['-'.join(x) for i in range(2, k_factors+1) for x in combinations(factor_base_cols, i)]

    # add individual measurements as mew columns
    df[tp_cols] = pd.DataFrame(df.throughput.values.tolist(), index= df.index)
    df['tp_y_avg'] = df[tp_cols].mean(axis=1)

    df[rt_cols] = pd.DataFrame(df.rt.values.tolist(), index= df.index)
    df['rt_y_avg'] = df[rt_cols].mean(axis=1)

    # create base factor (bias)
    df['I'] = df.apply(lambda row: 1, axis=1)

    # copy columns defined in factor_map
    for k,v in factor_map.items():
        df[v[0]] = df[k]

    # apply factor level mapping
    df[factor_base_cols] = df[factor_base_cols].applymap(str).replace(dict(factor_map.values()))

    # create factor interaction columns
    for interaction_col in factor_interaction_cols:
        df[interaction_col] = df.apply(lambda row: _prod(interaction_col,row), axis=1)

    # create tp and rt error columns
    for i, error_col in enumerate(tp_error_cols):
         df[error_col] = df[tp_cols[i]] - df["tp_y_avg"]

    for i, error_col in enumerate(rt_error_cols):
         df[error_col] = df[rt_cols[i]] - df["rt_y_avg"]


    # apply sorting such that order matches order in book
    df = df.sort_values(by=list(reversed(factor_base_cols)))

    # define projection cols
    cols = ['data_origin', 'workload', 'n_server_vm', "n_middleware_vm", "n_worker_per_mw", "I"] + factor_base_cols + factor_interaction_cols + rt_cols + ['rt_y_avg'] + rt_error_cols + tp_cols + ['tp_y_avg'] + tp_error_cols

    return df[cols]

def _get_t_value(k_factors, r_rep, confidence_interval=0.9):
    return 1.746


def load_2k_effect_df(df, r_rep, factor_map):

    workload = np.unique(df.loc[:,'workload'].values)
    assert(workload.shape[0]==1)

    k_factors = len(factor_map)
    n = 2**k_factors

    factor_base_cols = [i[0] for i in factor_map.values()]
    factor_interaction_cols= ['-'.join(x) for i in range(2, k_factors+1) for x in combinations(factor_base_cols, i)]

    t_value = _get_t_value(k_factors, r_rep, confidence_interval=0.9)
    print(f"Using t-value: {t_value}")

    rt_y_cols =     [f"rt_y{i}" for i in range(1,k_factors+1)]
    rt_error_cols = [f"rt_e{i}" for i in range(1,k_factors+1)]

    tp_y_cols =     [f"tp_y{i}" for i in range(1,k_factors+1)]
    tp_error_cols = [f"tp_e{i}" for i in range(1,k_factors+1)]

    factor_cols = ['I'] + factor_base_cols + factor_interaction_cols

    rt = {}
    rt['NAME'] = 'response time'
    rt['Y_MEAN_MEAN'] = df['rt_y_avg'].mean()
    rt['SSY'] = np.sum(df[rt_y_cols].values ** 2)
    rt['SST'] = np.sum((df[rt_y_cols].values - rt['Y_MEAN_MEAN'])**2)
    rt['SSE'] = np.sum(df[rt_error_cols].values ** 2)
    rt['STD_DEV_ERROR'] = (rt['SSE']/(2**k_factors *(r_rep-1)))**(1/2)
    rt['STD_DEV_EFFECT'] = rt['STD_DEV_ERROR'] / (2**k_factors * r_rep)**(1/2)
    rt['PERCENTAGE_OF_VARIATION_ERROR'] = rt['SSE'] / rt['SST'] * 100

    tp = {}
    tp['NAME'] = 'throughput'
    tp['Y_MEAN_MEAN'] = df['tp_y_avg'].mean()
    tp['SSY'] = np.sum(df[tp_y_cols].values ** 2)
    tp['SST'] = np.sum((df[tp_y_cols].values - tp['Y_MEAN_MEAN'])**2)
    tp['SSE'] = np.sum(df[tp_error_cols].values ** 2)
    tp['STD_DEV_ERROR'] = (tp['SSE']/(2**k_factors *(r_rep-1)))**(1/2)
    tp['STD_DEV_EFFECT'] = tp['STD_DEV_ERROR'] / (2**k_factors * r_rep)**(1/2)
    tp['PERCENTAGE_OF_VARIATION_ERROR']= tp['SSE'] / tp['SST'] * 100



    # Apply Sign Table Method to Calculate Effects

    agg_dict = {}
    for col in factor_cols:
        df[f"{col}_rt"] = df[col] * df['rt_y_avg']
        agg_dict[f"{col}_rt"] = ['count', 'sum', 'mean']

    for col in factor_cols:
        df[f"{col}_tp"] = df[col] * df['tp_y_avg']
        agg_dict[f"{col}_tp"] = ['count', 'sum', 'mean']

    df = df.agg(agg_dict)
    df = df.rename({"sum": "total","mean": "effect"})


    # Calculate Sum of Squared Effects
    df.loc['SSj'] = df.apply(lambda row: 2**k_factors * r_rep * row['effect']**2, axis=0)


    # Calculate Percentage of Variation:
    tp_cols = [f"{col}_tp" for col in factor_cols]
    tp_cols.remove('I_tp') # don't want to include bias

    rt_cols = [f"{col}_rt" for col in factor_cols]
    rt_cols.remove('I_rt') # don't want to include bias

    tp_variation = df[tp_cols].apply(lambda row: row['SSj']/tp['SST'] * 100, axis=0)
    rt_variation = df[rt_cols].apply(lambda row: row['SSj']/rt['SST'] * 100, axis=0)
    df.loc['percentage_of_variation_effect'] = tp_variation.combine_first(rt_variation) # merge rows


    # Calculate Confidence Interval
    tp_ci_low = df[tp_cols + ['I_tp']].apply(lambda row: row['effect']-t_value*tp['STD_DEV_EFFECT'], axis=0)
    rt_ci_low = df[rt_cols + ['I_rt']].apply(lambda row: row['effect']-t_value*rt['STD_DEV_EFFECT'], axis=0)
    df.loc['confidence_interval_low'] = tp_ci_low.combine_first(rt_ci_low)

    tp_ci_high = df[tp_cols + ['I_tp']].apply(lambda row: row['effect']+t_value*tp['STD_DEV_EFFECT'], axis=0)
    rt_ci_high = df[rt_cols + ['I_rt']].apply(lambda row: row['effect']+t_value*rt['STD_DEV_EFFECT'], axis=0)
    df.loc['confidence_interval_high'] = tp_ci_high.combine_first(rt_ci_high)

    # not significant if 0 is in the confidence interval
    df.loc['significant'] = df.apply(lambda row: not(row['confidence_interval_low']<=0 and row['confidence_interval_high']>=0))


    # Some basic assertion
    tp_ss_sum = df[tp_cols + ['I_tp']].loc['SSj'].sum()
    assert(int(tp['SSE'])==int(tp['SSY'] - tp_ss_sum))
    assert(int(tp['SST'])==int(tp['SSY'] -df['I_tp'].loc['SSj']))
    assert(100>=tp_variation.sum() and 99.5<=tp_variation.sum())

    rt_ss_sum = df[rt_cols + ['I_rt']].loc['SSj'].sum()
    assert(int(rt['SSE'])==int(rt['SSY'] - rt_ss_sum))
    assert(int(rt['SST'])==int(rt['SSY'] -df['I_rt'].loc['SSj']))
    assert(100>=rt_variation.sum() and 99.5<=rt_variation.sum())


    return df, rt, tp

def _prod(interaction_col, row, delim='-'):
    val = 1
    for v in interaction_col.split(delim):
        val *= row[v]
    return val
