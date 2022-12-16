from invoke import Collection

from . import timing
from . import wrk2
from . import xput

ns = Collection(
    timing,
    wrk2,
    xput,
)
