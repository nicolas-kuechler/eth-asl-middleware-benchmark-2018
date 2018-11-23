from queries.query_util import const

def aggregate_slots(df, config_cols, value_cols):
    # filter slots (warmup and cooldown phase)
    df = df.loc[(df.slot>=const.min_slot_inclusive) & (df.slot<=const.max_slot_inclusive)]

    # want to group over slots -> remove slots from config columns
    config_cols.remove('slot')
    # create a dict to aggregate all value columns ending with mean and calc the mean and sample std
    # e.g.{'throughput_mean': ['mean', 'std'], 'rt_mean:['mean', 'std'], ...}
    agg_dict = {col: ['mean', 'std'] for col in value_cols if not col.endswith('std')}

    # group over different selected slots
    df = df.groupby(level=config_cols).agg(agg_dict)

    # column renaming and level flattening
    value_cols = [x[0].split("_")[0] + "_slot_" + x[1] for x in df.columns.ravel()]
    df.columns = value_cols

    return df, config_cols, value_cols


def aggregate_repetitions(df, config_cols, value_cols):

    # want to group over repetitions -> remove rep from config columns
    config_cols.remove('rep')
    # create a dict to aggregate all value columns ending with mean and calc the mean and sample std
    # e.g.{'throughput_slot_mean': ['mean', 'std'], 'rt_slot_mean:['mean', 'std'], ...}
    agg_dict = {col: ['mean', 'std'] for col in value_cols if not col.endswith('std')}

    # group over repetitions
    df = df.groupby(level=config_cols).agg(agg_dict)

    # column renaming and level flattening
    value_cols = [x[0].split("_")[0] + "_rep_" + x[1] for x in df.columns.ravel()]
    df.columns = value_cols

    return df, config_cols, value_cols
