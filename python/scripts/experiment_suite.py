import experiment



experiment_suite_id = "abc"

try:
    # BASELINE WITHOUT MIDDLEWARE
    # One Server
    #experiment.run(experiment_suite_id=id, experiment_name="exp21")
    # Two Server
    #experiment.run(experiment_suite_id=id, experiment_name="exp22")

    # BASELINE WITH MIDDLEWARE
    # One Middleware
    experiment.run(experiment_suite_id=id, experiment_name="exp31")

    raise ValueError("Throughput Maximizing Number of Worker Threads not Implemented")

    # Two Middleware
    experiment.run(experiment_suite_id=id, experiment_name="exp32")

    # THROUGHPUT FOR WRITES
    # Full System
    experiment.run(experiment_suite_id=id, experiment_name="exp41")


    # TODO [nku] implement mechanism to determine highest throughput of system and use here as number of workers
    raise ValueError("Throughput Maximizing Number of Worker Threads not Implemented")
    # GETS AND MULTI-GETS
    # Sharded Case
    experiment.run(experiment_suite_id=id, experiment_name="exp51")
    # Non-Sharded Case
    experiment.run(experiment_suite_id=id, experiment_name="exp52")

    # 2K Analysis
    experiment.run(experiment_suite_id=id, experiment_name="exp60")
finally:
    print("NOT IMPLEMENTED YET -> Stopping all VM's")
