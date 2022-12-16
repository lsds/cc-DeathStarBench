from glob import glob
from invoke import task
import matplotlib.pyplot as plt
from os import makedirs
from os.path import join
import pandas as pd
from subprocess import run as sp_run
from tasks.env import PROJ_ROOT
from tasks.bench.env import BENCH_ROOT, WRK2_BINARY, WRK2_SCRIPTS_DIR
from tasks.utils.config import get_config_value
from time import sleep


def time_str_to_ms(time_str):
    if time_str.endswith("ms"):
        return float(time_str[:-2])
    if time_str.endswith("s"):
        return float(time_str[:-1]) * 1000


def do_wrk2_run(
    num_threads,
    num_connections,
    duration,
    script,
    url,
    port,
    num_reqs,
):
    cmd = [
        "{}".format(WRK2_BINARY),
        "-t {}".format(num_threads),
        "-c {}".format(num_connections),
        "-d {}".format(duration),
        "-L -s {}".format(script),
        "http://{}:{}".format(url, port),
        "-R {}".format(num_reqs),
    ]

    cmd = " ".join(cmd)
    # TODO: work out why sometimes the requests don't hit the frontend
    while True:
        out = (
            sp_run(
                cmd, shell=True, check=True, cwd=PROJ_ROOT, capture_output=True
            )
            .stdout.decode("utf-8")
            .split("\n")
        )
        percentile = (
            [line for line in out if "99.000%" in line][0]
            .strip()
            .split(" ")[-1]
        )
        if percentile == "0.00us":
            print("Something went wrong, running again...")
        else:
            break
    percentile_ms = time_str_to_ms(percentile)
    return percentile_ms


@task(default=True)
def run(ctx, runtime="native"):
    """
    Run latency-throughput benchmark using wrk2
    """
    # Hard-coded experiment variables
    num_threads = 2
    num_connections = 2
    script = join(WRK2_SCRIPTS_DIR, "hotel_reservation.lua")

    # Duration of each run
    duration = 5
    # Number of requests (X axis)
    num_reqs = [100, 150, 200, 250, 300, 350, 400, 450, 500]

    # Get URL and port
    url = get_config_value("frontend_host")
    port = get_config_value("frontend_port")
    kind = get_config_value("kind")

    print("Running xput-latency experiment on: {}-{}".format(kind, runtime))
    # CSV file to write results in
    data_dir = join(BENCH_ROOT, "throughput-latency", "data")
    makedirs(data_dir, exist_ok=True)
    data_file = join(data_dir, "{}_{}.csv".format(kind, runtime))
    with open(data_file, "w") as f:
        f.write("Throughput,99thPercentile(ms)\n")

    for req in num_reqs:
        print("\tStart\tMode: {}\tNum reqs: {}".format(runtime, req))
        time = do_wrk2_run(
            num_threads, num_connections, duration, script, url, port, req
        )
        print("\tFinish\tMode: {}\tNum reqs: {}".format(runtime, req))
        sleep(3)
        with open(data_file, "a") as f:
            f.write("{},{}\n".format(req, time))


def read_results(kind="compose"):
    result_dict = {}

    results_dir = join(BENCH_ROOT, "throughput-latency", "data")
    for csv in glob(join(results_dir, "*.csv")):
        csv_base = csv.split(".")[0]
        workload = csv_base.split("_")[1]
        result_dict[workload] = []

        # Read results
        results = pd.read_csv(csv)
        result_dict[workload] = [
            results["Throughput"].to_list(),
            results["99thPercentile(ms)"].to_list(),
        ]

        if "None" in result_dict[workload][1]:
            for num, v in enumerate(result_dict[workload][1]):
                if v == "None":
                    result_dict[workload][1][num] = float("NaN")
                else:
                    result_dict[workload][1][num] = float(v)

    return result_dict


@task
def plot(ctx, kind="compose"):
    """
    Plot throughput-latency figure
    """
    plot_dir = join(BENCH_ROOT, "throughput-latency", "plot")
    plot_file = join(plot_dir, "xput_latency.pdf")
    makedirs(plot_dir, exist_ok=True)

    results = read_results(kind)
    fig, ax = plt.subplots(figsize=(6, 4))

    for workload in results:
        xs = results[workload][0]
        ys = results[workload][1]
        ax.plot(xs, ys, label=workload, linestyle="-", marker=".")

    # Plot aesthetics
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=10, top=10000)
    ax.legend(loc="lower right")
    ax.set_xlabel("Throughput [RPS]")
    ax.set_ylabel("Latency [ms]")
    ax.set_yscale("log")
    ax.set_title(
        "Throughput-Latency on docker-compose \nw/ different enclave runtimes"
    )

    # Save multiplot to file
    fig.tight_layout()
    plt.savefig(plot_file, format="pdf", bbox_inches="tight")
    plt.savefig(plot_file[:-4] + ".png", format="png", bbox_inches="tight")
