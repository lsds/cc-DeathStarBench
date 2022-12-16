from invoke import task
import matplotlib.pyplot as plt
from numpy import argmax
from os import makedirs
from os.path import join
import pandas as pd
from scipy.interpolate import UnivariateSpline
from tasks.bench.env import BENCH_ROOT
from tasks.utils.config import get_config_value
from tasks.utils.requests import (
    do_login_request,
    do_recommendations_request,
    do_reservation_request,
    do_search_request,
)
from time import time

colors = [
    (0, 104 / 256, 181 / 256),
    (139 / 256, 174 / 256, 70 / 256),
    (0, 199 / 256, 253 / 256),
    (188 / 256, 158 / 256, 199 / 256),
    (240 / 256, 195 / 256, 172 / 256),
]


def do_request(data_file, req_func, req_name):
    start = time()
    req_func()
    time_elapsed_ms = (time() - start) * 1000
    with open(data_file, "a") as f:
        f.write("{},{}\n".format(req_name, time_elapsed_ms))


@task(default=True)
def run(ctx, runtime="native"):
    """
    Plot the histogram of the time elapsed of running different request, where
    each endpoint is hit with the same probability.
    """
    reqs_per_endpoint = 10000

    # Get URL and port
    kind = get_config_value("kind")

    print("Running request timing experiment on: {}-{}".format(kind, runtime))
    # CSV file to write results in
    data_dir = join(BENCH_ROOT, "request-timing", "data")
    makedirs(data_dir, exist_ok=True)
    data_file = join(data_dir, "{}_{}.csv".format(kind, runtime))
    with open(data_file, "w") as f:
        f.write("Endpoint,Time(ms)\n")

    for _ in range(reqs_per_endpoint):
        do_request(data_file, do_login_request, "user")
        do_request(data_file, do_reservation_request, "reservation")
        do_request(data_file, do_recommendations_request, "recommendation")
        do_request(data_file, do_search_request, "search")


def read_results(kind="compose"):
    result_dict = {}
    raw_results = []

    results_file = join(
        BENCH_ROOT, "request-timing", "data", "{}_native.csv".format(kind)
    )
    results = pd.read_csv(results_file)
    for endpoint in ["user", "reservation", "recommendation", "search"]:
        results_per_ep = results.groupby("Endpoint").get_group(endpoint)
        result_dict[endpoint] = results_per_ep["Time(ms)"].to_list()
        raw_results = results["Time(ms)"].to_list()

    return result_dict, raw_results


@task
def plot(ctx, kind="compose"):
    """
    Plot throughput-latency figure
    """
    plot_dir = join(BENCH_ROOT, "request-timing", "plot")
    plot_file = join(plot_dir, "request_timing_{}.pdf".format(kind))
    makedirs(plot_dir, exist_ok=True)

    results, raw_results = read_results(kind)
    fig, ax = plt.subplots(figsize=(6, 4))

    combined_data = []
    nreqs = len(raw_results)
    for endpoint in results:
        combined_data.append(results[endpoint])

    # Plot histograms with high transparency
    left_lim = 3
    right_lim = 12
    nbins = 500
    vals_ax1, bins_ax1, _ = ax.hist(
        raw_results, bins=nbins, alpha=0.05, color=colors[0]
    )
    vals_ax2, bins_ax2, _ = ax.hist(
        combined_data, bins=nbins, stacked=False, alpha=0.4, color=colors[1:]
    )

    # Add smooth curves on top of the histograms
    bins_ax1 = bins_ax1[:-1] + (bins_ax1[1] - bins_ax1[0]) / 2
    f_ax1 = UnivariateSpline(bins_ax1, vals_ax1, s=nbins)
    ax.plot(bins_ax1, f_ax1(bins_ax1), color=colors[0], label="stacked")
    bins_ax2 = bins_ax2[:-1] + (bins_ax2[1] - bins_ax2[0]) / 2
    for ind, val_ax2 in enumerate(vals_ax2):
        f_ax2 = UnivariateSpline(bins_ax2, val_ax2, s=nbins)
        ax.plot(
            bins_ax2,
            f_ax2(bins_ax2),
            color=colors[ind + 1],
            label="endpoint {}".format(ind + 1),
        )

    # Lastly, add vertical lines at each endpoint's mode
    for ind, cd in enumerate(vals_ax2):
        mode_x = bins_ax2[argmax(cd)]
        ax.vlines(x=mode_x, ymin=0, ymax=f_ax1(mode_x), color=colors[ind + 1])

    ax.legend()
    ax.set_xlabel("Request Time [ms]")
    ax.set_ylabel("Frequency")
    ax.set_xlim(left=left_lim, right=right_lim)
    ax.set_ylim(bottom=0)
    ax.set_title(
        (
            "Histogram of the time elapsed to serve {} requests\n"
            "(vertical lines are the mode per endpoint)".format(nreqs)
        )
    )

    # Save multiplot to file
    fig.tight_layout()
    plt.savefig(plot_file, format="pdf", bbox_inches="tight")
    # Also save to `.png` file to include in the Github documentation
    plt.savefig(plot_file[:-4] + ".png", format="png", bbox_inches="tight")
