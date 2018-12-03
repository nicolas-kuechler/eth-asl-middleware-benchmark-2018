from queries.query_util import utility, const

def stats(suite, exp):
    results = utility.get_result_collection(suite)

    d = results.find_one({"exp": exp})
    return d['network_stats']
