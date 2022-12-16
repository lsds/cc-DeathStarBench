from invoke import task
from os.path import exists, join
from shutil import copy, rmtree
from subprocess import run
from tasks.bench.env import BENCH_BIN_DIR


@task(default=True)
def install(ctx):
    """
    Install the wrk2 binary
    """
    url = "https://github.com/giltene/wrk2"
    workdir = "/tmp/wrk2"

    if exists(workdir):
        rmtree(workdir)

    # Clone and build the wrk2 binary
    cmd = "git clone {} {}".format(url, workdir)
    run(cmd, shell=True, check=True)
    run("make", shell=True, check=True, cwd=workdir)

    # Copy the binary to the right path
    copy(join(workdir, "wrk"), join(BENCH_BIN_DIR, "wrk"))
    rmtree(workdir)
