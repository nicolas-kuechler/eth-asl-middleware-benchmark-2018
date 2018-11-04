import pymongo
from bson.son import SON
import pandas as pd
import numpy as np

from queries.query_util import utility

def load_df(suite, exp):

    results = utility.get_result_collection(suite)

    pipeline = _build_pipeline(exp)

    # create dataframe
    cursor = results.aggregate(pipeline, allowDiskUse=True)

    df =  pd.DataFrame(list(cursor))

    return df

def _build_pipeline(exp, min_slot=1, max_slot=13):

    pipeline = [
        {"$match": {"exp": exp}},
        {"$addFields":{"workload": {"$switch": {"branches": [  { "case": {"$eq":["$exp_config.workload_ratio", "1:0"]}, "then": "write-only" },
                                                                { "case": {"$eq":["$exp_config.workload_ratio", "0:1"]}, "then": "read-only" },],
                                                "default": "read-write"}}
                      }
        },
        {"$project": {"client_stats":0, "mw_stats.op":0}},
        {"$unwind": "$mw_stats"},
        {"$unwind": "$mw_stats.rt_hist"},
        # TODO [nku] decide what to do with slot filtering -> if apply this filtering numbers don't match with client measurements
    #    {"$match":{"mw_stats.rt_hist.slot":{"$gte":min_slot},
    #            "mw_stats.rt_hist.slot": {"$lte":max_slot}
    #            }
    #    },
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
