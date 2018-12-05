import pymongo,re
from bson.son import SON
import pandas as pd
import numpy as np

from queries.query_util import utility, df_aggregate, const
from  queries import weighted_stats

def load_df_by_rep(suite, exp):
    results = utility.get_result_collection(suite)

    pipeline = _build_pipeline(exp)

    # create dataframe
    cursor = results.aggregate(pipeline, allowDiskUse=True)

    df =  pd.DataFrame(list(cursor))

    return df


def load_df(suite, exp):

    df = load_df_by_rep(suite, exp)

    quantiles = [0.25, 0.50, 0.75, 0.90, 0.99]
    df_quantiles = weighted_stats.weighted_quantiles_mean(df=df, value_col='rt', weight_col='rt_freq', quantiles=quantiles)

    config_cols = ["rep", "stat", "num_clients", "data_origin", "op_type", "n_server_vm", "n_client_vm", "n_vc", "workload", "workload_ratio",
        "multi_get_behaviour", "multi_get_size", "n_worker_per_mw", "n_middleware_vm", "n_instances_mt_per_machine", "n_threads_per_mt_instance"]
    value_cols = ['rt']

    df_quantiles = df_quantiles.set_index(config_cols, drop=False)
    df_quantiles_rep, _ , _ = df_aggregate.aggregate_repetitions(df_quantiles, config_cols, value_cols)
    df_quantiles_rep = df_quantiles_rep.reset_index()

    return df, df_quantiles_rep

def _build_pipeline(exp):

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
        {"$project": {"client_stats":0, "mw_stats.op":0}},
        {"$unwind": "$mw_stats"},
        {"$unwind": "$mw_stats.rt_hist"},
        # TODO [nku] decide what to do with slot filtering -> if apply this filtering numbers don't match with client measurements
        #{"$match":{"mw_stats.rt_hist.slot":{"$gte":const.min_slot_inclusive},
        #        "mw_stats.rt_hist.slot": {"$lte":const.max_slot_inclusive}
        #        }
        #},
        {"$unwind": "$mw_stats.rt_hist.hist"},
        {"$group": {"_id" : {"rep":"$repetition",
                             "op_type": "$mw_stats.rt_hist.op_type",
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
                             "n_threads_per_mt_instance":"$exp_config.n_threads_per_mt_instance",
                             "rt": "$mw_stats.rt_hist.hist.key"},
                   "rt_freq" : {"$sum" :  "$mw_stats.rt_hist.hist.val"}
                   }
        },
        {"$project": {"_id": 0,
                        "rep":"$_id.rep",
                        "op_type": {"$switch": {"branches": [  { "case": {"$eq":["$_id.op_type", "get"]}, "then": "get" },
                                                    { "case": {"$eq":["$_id.op_type", "mget"]}, "then": "get" }, # rename mget to get here
                                                    { "case": {"$eq":["$_id.op_type", "set"]}, "then": "set" }],
                                                    "default": "unknown"}},
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
                        "rt": {"$divide" : ["$_id.rt", 10.0]},
                        "data_origin":"mw",
                        "rt_freq":1,
                     }
        },
        {"$sort":SON([("n_client_vm",1),
                        ("n_middleware_vm",1),
                        ("n_server_vm",1),
                        ("workload",1),
                        ("multi_get_behaviour",1),
                        ("multi_get_size",1),
                        ("n_worker_per_mw",1),
                        ("rt",1)])}
    ]

    return pipeline
