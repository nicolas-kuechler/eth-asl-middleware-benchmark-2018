import pymongo, copy
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
        {"$project": {"mw_stats":0}},
        {"$unwind": "$client_stats"},
        {"$addFields":{"n_gets": {"$ceil":{"$multiply":["$client_stats.runtime", "$client_stats.gets.Ops/sec"]}},
                        "n_sets": {"$ceil":{"$multiply":["$client_stats.runtime", "$client_stats.sets.Ops/sec"]}},
        }},
        {"$project": {"_id": 0,
                        "rep":"$repetition",
                        "num_clients": 1,
                        "n_server_vm": "$exp_config.n_server",
                        "n_client_vm": "$exp_config.n_client",
                        "n_vc": "$exp_config.n_vc",
                        "workload": 1,
                        "workload_ratio": "$exp_config.workload_ratio",
                        "multi_get_behaviour": { "$cond": { "if": { "$eq": ["$exp_config.multi_get_behaviour", None]}, "then": "-", "else": "$exp_config.multi_get_behaviour" }},
                        "multi_get_size": { "$cond": { "if": { "$eq": ["$exp_config.multi_get_size", None]}, "then": "-", "else": "$exp_config.multi_get_size" }},
                        "n_worker_per_mw": "$exp_config.n_worker_per_mw",
                        "n_middleware_vm" : "$exp_config.n_middleware",
                        "n_instances_mt_per_machine":"$exp_config.n_instances_mt_per_machine",
                        "n_threads_per_mt_instance":"$exp_config.n_threads_per_mt_instance",
                        "n_gets":1,
                        "n_sets":1,
                        "set_hist": {"$map": {"input": "$client_stats.set",
                                                "as": "row",
                                                "in": {
                                                        "rt": "$$row.<=msec",
                                                        "cum_rt_freq": {"$ceil":{"$multiply": ["$$row.percent", "$n_sets", 0.01]}},
                                                        "op_type": "set"
                                                        }}},
                        "get_hist": {"$map": {"input": "$client_stats.get",
                                                "as": "row",
                                                "in": {
                                                        "rt": "$$row.<=msec",
                                                        "cum_rt_freq": {"$ceil":{"$multiply": ["$$row.percent", "$n_gets", 0.01]}},
                                                        "op_type": "get"
                                                        }}}
                     }
        },
        {"$addFields": {
                "set_hist_with_idx": {"$zip": {"inputs": ["$set_hist", {"$range": [0, {"$size": "$set_hist"}]}]}},
                "get_hist_with_idx": {"$zip": {"inputs": ["$get_hist", {"$range": [0, {"$size": "$get_hist"}]}]}},
        }},
        {"$addFields":{"set_hist_pairs":{"$map": {"input": "$set_hist_with_idx",
                                                    "as": "row",
                                                    "in": {
                                                            "current": {"$arrayElemAt":["$$row", 0]},
                                                            "prev": {"$arrayElemAt":["$set_hist", {"$max":[0, {"$subtract":[{"$arrayElemAt":["$$row", 1]}, 1]}]}]}
                                                            }}},
                        "get_hist_pairs":{"$map": {"input": "$get_hist_with_idx",
                                                                    "as": "row",
                                                                    "in": {
                                                                            "current": {"$arrayElemAt":["$$row", 0]},
                                                                            "prev": {"$arrayElemAt":["$get_hist", {"$max":[0, {"$subtract":[{"$arrayElemAt":["$$row", 1]}, 1]}]}]}
                                                                            }}},
                    }
        },
        {"$addFields": {"op_pairs": { "$concatArrays": [ "$set_hist_pairs", "$get_hist_pairs" ]}}},
        {"$project": {"set_hist":0,
                        "get_hist":0,
                        "set_hist_with_idx":0,
                        "get_hist_with_idx":0,
                        "set_hist_pairs":0,
                        "get_hist_pairs":0}},
        {"$unwind": "$op_pairs"},
        {"$addFields": {"rt_freq":{"$subtract":["$op_pairs.current.cum_rt_freq", "$op_pairs.prev.cum_rt_freq"]}}},
        {"$group": {"_id" : {"num_clients": "$num_clients",
                             "n_server_vm": "$n_server_vm",
                             "n_client_vm": "$n_client_vm",
                             "n_vc": "$n_vc",
                             "workload": "$workload",
                             "workload_ratio": "$workload_ratio",
                             "multi_get_behaviour": "$multi_get_behaviour",
                             "multi_get_size": "$multi_get_size",
                             "n_worker_per_mw": "$n_worker_per_mw",
                             "n_middleware_vm" : "$n_middleware_vm",
                             "n_instances_mt_per_machine":"$n_instances_mt_per_machine",
                             "n_threads_per_mt_instance":"$n_threads_per_mt_instance",
                             "rep":"$rep",
                             "op_type":"$op_pairs.current.op_type",
                             "rt": "$op_pairs.current.rt"},
                   "rt_freq" : {"$sum" :  "$rt_freq"},
                   "n_gets_avg": {"$avg": "$n_gets"},
                   "n_sets_avg": {"$avg": "$n_sets"}
                   }
        },
        {"$project":{"_id": 0,
                        "num_clients": "$_id.num_clients",
                        "n_server_vm": "$_id.n_server",
                        "n_client_vm": "$_id.n_client",
                        "n_vc": "$_id.n_vc",
                        "workload": "$_id.workload",
                        "workload_ratio": "$_id.workload_ratio",
                        "multi_get_behaviour": "$_id.multi_get_behaviour",
                        "multi_get_size": "$_id.multi_get_size",
                        "n_worker_per_mw": "$_id.n_worker_per_mw",
                        "n_middleware_vm" : "$_id.n_middleware",
                        "n_instances_mt_per_machine":"$_id.n_instances_mt_per_machine",
                        "n_threads_per_mt_instance":"$_id.n_threads_per_mt_instance",
                        "data_origin":"client",
                        "n_gets_avg":"$_id.n_gets_avg",
                        "n_sets_avg":"$_id.n_sets_avg",
                        "rep":"$_id.rep",
                        "op_type":"$_id.op_type",
                        "rt": "$_id.rt",
                        "rt_freq": 1
                        }
        },
        {"$match":{ "rt_freq": { "$gt": 0 }}},
        {"$sort":SON([("n_client_vm",1),
                        ("n_middleware_vm",1),
                        ("n_server_vm",1),
                        ("op_type",1),
                        ("workload",1),
                        ("multi_get_behaviour",1),
                        ("multi_get_size",1),
                        ("n_worker_per_mw",1),
                        ("num_clients", 1),
                        ("rep",1),
                        ("rt",1)])},
    ]

    return pipeline
