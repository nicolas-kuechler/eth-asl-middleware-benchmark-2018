import utility

exp_ids = ['exp21', 'exp22', 'exp31', 'exp32', 'exp41', 'exp51', 'exp52', 'exp60']

n_experiments = 0
n_repetitions = 4
sec_per_exp = 90

for experiment_name in exp_ids:
    configurations = utility.get_config(f"./configs/{experiment_name}.json")
    n_experiments += n_repetitions * len(configurations)

sec = n_experiments * sec_per_exp
print(f"Number of Experiments: {n_experiments}")
print(f"  with {sec_per_exp} seconds per experiment and {n_repetitions} repetitions")
print(f"=> Expected Test Time: {sec/3600} hours")
