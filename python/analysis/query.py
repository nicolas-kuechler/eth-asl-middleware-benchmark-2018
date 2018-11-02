import pymongo
from bson.son import SON
import pandas as pd
import numpy as np


def load_pd(suite, exp):

    # connect to mongo db
    ip = "localhost"
    port = "27017"
    client = pymongo.MongoClient(f"mongodb://{ip}:{port}/")
    db = client[suite]
    results = db.collection['results']

    pipeline = _build_pipeline(exp)

    # create dataframe
    cursor = results.aggregate(pipeline, allowDiskUse=True)



    df =  pd.DataFrame(list(cursor))

    config_cols = ["rep", "slot", "op_type", "num_clients", "n_server_vm", "n_client_vm", "n_vc", "workload", "workload_ratio",
        "multi_get_behaviour", "multi_get_size", "n_worker_per_mw", "n_middleware_vm", "n_instances_mt_per_machine", "n_threads_per_mt_instance"]
    value_cols = ["throughput_mean", "rt_mean", "rt_std", "qwt_mean", "qwt_std", "ntt_mean", "ntt_std", "wtt_mean", "wtt_std",
        "sst0_mean", "sst0_std", "sst1_mean", "sst1_std", "sst2_mean", "sst2_std", "sst_mean", "sst_std"]
    df = df.set_index(config_cols, drop=False)

    df_slot, config_cols_slot, value_cols_slot = _aggregate_slots(df, config_cols=config_cols, value_cols=value_cols)

    df_rep, config_cols_rep, value_cols_rep = _aggregate_repetitions(df_slot, config_cols=config_cols_slot, value_cols=value_cols_slot)

    return df_rep.reset_index()



def _build_pipeline(exp):
    stats_window_size = 5.0 #seconds

    pipeline = [
        {"$match": {"exp": exp}},
        {"$addFields":{"num_clients": {"$multiply": ["$exp_config.n_client",
                                                     "$exp_config.n_instances_mt_per_machine",
                                                     "$exp_config.n_threads_per_mt_instance",
                                                     "$exp_config.n_vc"
                                                    ]},
                        "workload": {"$switch": {"branches": [  { "case": {"$eq":["$exp_config.workload_ratio", "1:0"]}, "then": "write-only" },
                                                                { "case": {"$eq":["$exp_config.workload_ratio", "0:1"]}, "then": "read-only" },],
                                                "default": "read-write"}}
                      }
        },
        {"$unwind":"$mw_stats"},
        {"$unwind":"$mw_stats.op"},
        {"$group": {"_id" : {"rep":"$repetition",
                             "slot": "$mw_stats.op.slot",
                             "op_type": "$mw_stats.op.op_type",
                             "num_clients": "$num_clients",
                             "n_server": "$exp_config.n_server",
                             "n_client": "$exp_config.n_client",
                             "n_vc": "$exp_config.n_vc",
                             "workload": "$workload",
                             "workload_ratio": "$exp_config.workload_ratio",
                             "multi_get_behaviour":"$exp_config.multi_get_behaviour",
                             "multi_get_size":"$exp_config.multi_get_size",
                             "n_worker_per_mw": "$exp_config.n_worker_per_mw",
                             "n_middleware" : "$exp_config.n_middleware",
                             "n_instances_mt_per_machine":"$exp_config.n_instances_mt_per_machine",
                             "n_threads_per_mt_instance":"$exp_config.n_threads_per_mt_instance"},
                   "count" : {"$sum" :  1},
                   "sum_rt_count" : {"$sum": "$mw_stats.op.rt_count"},
                   "rt_arr" :  {"$push": {"m2":"$mw_stats.op.rt_m2", "mean":"$mw_stats.op.rt_mean", "count":"$mw_stats.op.rt_count"}},
                   "qwt_arr" : {"$push": {"m2":"$mw_stats.op.qwt_m2", "mean":"$mw_stats.op.qwt_mean", "count":"$mw_stats.op.qwt_count"}},
                   "ntt_arr" : {"$push": {"m2":"$mw_stats.op.ntt_M2", "mean":"$mw_stats.op.ntt_mean", "count":"$mw_stats.op.ntt_count"}},
                   "wtt_arr" : {"$push": {"m2":"$mw_stats.op.wtt_M2", "mean":"$mw_stats.op.wtt_mean", "count":"$mw_stats.op.wtt_count"}},
                   "sst0_arr" : {"$push": {"m2":"$mw_stats.op.sst0_M2", "mean":"$mw_stats.op.sst0_mean", "count":"$mw_stats.op.sst0_count"}},
                   "sst1_arr" : {"$push": {"m2":"$mw_stats.op.sst1_M2", "mean":"$mw_stats.op.sst1_mean", "count":"$mw_stats.op.sst1_count"}},
                   "sst2_arr" : {"$push": {"m2":"$mw_stats.op.sst2_M2", "mean":"$mw_stats.op.sst2_mean", "count":"$mw_stats.op.sst2_count"}},
                   }
        },
        {"$addFields":{ "rt": {"$reduce":  _reduce_stat("rt_arr")},
                        "qwt": {"$reduce": _reduce_stat("qwt_arr")},
                        "ntt": {"$reduce": _reduce_stat("ntt_arr")},
                        "wtt": {"$reduce": _reduce_stat("wtt_arr")},
                        "sst0": {"$reduce": _reduce_stat("sst0_arr")},
                        "sst1": {"$reduce": _reduce_stat("sst1_arr")},
                        "sst2": {"$reduce": _reduce_stat("sst2_arr")}
                     }
        },
        {"$addFields": {"throughput": {"$divide" : ["$sum_rt_count", stats_window_size]},
                        "rt_mean" : "$rt.mean",
                        "rt_std":{"$sqrt": {"$divide": ["$rt.m2", {"$subtract":["$rt.count", 1]}]}},
                        "qwt_mean" : "$qwt.mean",
                        "qwt_std":{"$sqrt": {"$divide": ["$qwt.m2", {"$subtract":["$qwt.count", 1]}]}},
                        "ntt_mean" : "$ntt.mean",
                        "ntt_std":{"$sqrt": {"$divide": ["$ntt.m2", {"$subtract":["$ntt.count", 1]}]}},
                        "wtt_mean" : "$wtt.mean",
                        "wtt_std":{"$sqrt": {"$divide": ["$wtt.m2", {"$subtract":["$wtt.count", 1]}]}},
                        "sst0_mean" : "$sst0.mean",
                        "sst0_std":{"$sqrt": {"$divide": ["$sst0.m2", {"$subtract":["$sst0.count", 1]}]}},
                        "sst1_mean" : "$sst1.mean",
                        "sst1_std":{"$sqrt": {"$divide": ["$sst1.m2", {"$subtract":["$sst1.count", 1]}]}},
                        "sst2_mean" : "$sst2.mean",
                        "sst2_std":{"$sqrt": {"$divide": ["$sst2.m2", {"$subtract":["$sst2.count", 1]}]}},
                        "sst_arr":{"$setUnion":[["$sst0"],["$sst1"],["$sst2"]]}
                       }},
        {"$addFields":{ "sst": {"$reduce":  _reduce_stat("sst_arr")}}},
        {"$project": {"_id": 0,
                        "rep":"$_id.rep",
                        "slot": "$_id.slot",
                        "op_type": "$_id.op_type",
                        "num_clients": "$_id.num_clients",
                        "n_server_vm": "$_id.n_server",
                        "n_client_vm": "$_id.n_client",
                        "n_vc": "$_id.n_vc",
                        "workload": "$_id.workload",
                        "workload_ratio": "$_id.workload_ratio",
                        "multi_get_behaviour": { "$cond": { "if": { "$eq": ["$_id.multi_get_behaviour", None]}, "then": "-", "else": "$_id.multi_get_behaviour" }},
                        "multi_get_size": { "$cond": { "if": { "$eq": ["$_id.multi_get_size", None]}, "then": "-", "else": "$_id.multi_get_size" }},
                        "n_worker_per_mw": "$_id.n_worker_per_mw",
                        "n_middleware_vm" : "$_id.n_middleware",
                        "n_instances_mt_per_machine":"$_id.n_instances_mt_per_machine",
                        "n_threads_per_mt_instance":"$_id.n_threads_per_mt_instance",
                        "count": 1,
                        "throughput_mean":"$throughput",
                        "rt_mean" : "$rt_mean",
                        "rt_std": "$rt_std",
                        "qwt_mean" : "$qwt_mean",
                        "qwt_std": "$qwt_std",
                        "ntt_mean" : "$ntt_mean",
                        "ntt_std": "$ntt_std",
                        "wtt_mean" : "$wtt_mean",
                        "wtt_std": "$wtt_std",
                        "sst0_mean" : "$sst0_mean",
                        "sst0_std": "$sst0_std",
                        "sst1_mean" : "$sst1_mean",
                        "sst1_std": "$sst1_std",
                        "sst2_mean" : "$sst2_mean",
                        "sst2_std": "$sst2_std",
                        "sst_mean": "$sst.mean",
                        "sst_std": {"$sqrt": {"$divide": ["$sst.m2", {"$subtract":["$sst.count", 1]}]}}
                     }
        },
        {"$match":{ "throughput_mean": { "$gt": 0 }}},
        {"$sort":SON([("n_client_vm",1),
                        ("n_middleware_vm",1),
                        ("n_server_vm",1),
                        ("workload",1),
                        ("multi_get_behaviour",1),
                        ("multi_get_size",1),
                        ("n_worker_per_mw",1),
                        ("num_clients", 1),
                        ("rep",1),
                        ("slot", 1)])},
    ]

    return pipeline

def _aggregate_slots(df, config_cols, value_cols, start_slot=1, end_slot=13):
    # filter slots (warmup and cooldown phase)
    df = df.loc[(df.slot>=start_slot) & (df.slot<=end_slot)]

    # want to group over slots -> remove slots from config columns
    config_cols.remove('slot')
    # create a dict to aggregate all value columns ending with mean and calc the mean and sample std
    # e.g.{'throughput_mean': ['mean', 'std'], 'rt_mean:['mean', 'std'], ...}
    agg_dict = {col: ['mean', 'std'] for col in value_cols if col.endswith('mean')}

    # group over different selected slots
    df = df.groupby(level=config_cols).agg(agg_dict)

    # column renaming and level flattening
    value_cols = [x[0].split("_")[0] + "_slot_" + x[1] for x in df.columns.ravel()]
    df.columns = value_cols

    return df, config_cols, value_cols


def _aggregate_repetitions(df, config_cols, value_cols):

    # want to group over repetitions -> remove rep from config columns
    config_cols.remove('rep')
    # create a dict to aggregate all value columns ending with mean and calc the mean and sample std
    # e.g.{'throughput_slot_mean': ['mean', 'std'], 'rt_slot_mean:['mean', 'std'], ...}
    agg_dict = {col: ['mean', 'std'] for col in value_cols if col.endswith('mean')}

    # group over repetitions
    df = df.groupby(level=config_cols).agg(agg_dict)

    # column renaming and level flattening
    value_cols = [x[0].split("_")[0] + "_rep_" + x[1] for x in df.columns.ravel()]
    df.columns = value_cols

    return df, config_cols, value_cols



def _reduce_stat(arr):
    """
    builds a dictionary for the pymongo $reduce operation to reduce a list of (mean, count, m2) triples
    according to the algorithm described in:
    https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Parallel_algorithm
    """
    d = {"input": {"$filter": {"input": f"${arr}",
                                                                    "as":"x",
                                                                    "cond":{"$gt":["$$x.count", 0.0]}
                                                                   }
                                                       },
                                            "initialValue": {"mean": 0.0,
                                                             "count": 0,
                                                             "m2":0.0},
                                            "in": {"mean":{"$sum":["$$value.mean",
                                                                    {"$multiply":[{"$subtract": [{"$toDouble":"$$this.mean"}, "$$value.mean"]},
                                                                                  {"$divide":["$$this.count",
                                                                                              {"$sum":["$$this.count","$$value.count"]}]}
                                                                                 ]
                                                                    }
                                                                  ]},
                                                   "m2" : {"$sum" : ["$$value.m2",
                                                                        "$$this.m2",
                                                                        {"$multiply": [
                                                                                        {"$pow":[
                                                                                            {"$subtract": [
                                                                                                "$$this.mean",
                                                                                                "$$value.mean"]
                                                                                            }, 2]
                                                                                        },
                                                                                       {"$divide": [
                                                                                           {"$multiply": [
                                                                                               "$$value.count",
                                                                                               "$$this.count"
                                                                                           ]},
                                                                                            {"$sum": [
                                                                                                "$$value.count",
                                                                                                "$$this.count"
                                                                                            ]}
                                                                                       ]}
                                                                        ]}
                                                                  ]},
                                                   "count": {"$sum":["$$value.count", "$$this.count"]},
                                                  }
                                             }
    return d
