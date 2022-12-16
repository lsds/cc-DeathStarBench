from os.path import join
from tasks.env import PROJ_ROOT

BENCH_ROOT = join(PROJ_ROOT, "bench")
BENCH_BIN_DIR = join(BENCH_ROOT, "bin")

WRK2_ROOT = join(BENCH_ROOT, "wrk2")
WRK2_BINARY = join(BENCH_BIN_DIR, "wrk")
WRK2_SCRIPTS_DIR = join(WRK2_ROOT, "scripts")
