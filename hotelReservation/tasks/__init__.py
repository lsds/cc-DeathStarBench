from invoke import Collection

from . import dev
from . import docker
from . import git
from . import tests
from . import sgx

from tasks.bench import ns as bench_ns
from tasks.deploy import ns as deploy_ns

ns = Collection(
    dev,
    docker,
    git,
    tests,
    sgx,
)

ns.add_collection(bench_ns, name="bench")
ns.add_collection(deploy_ns, name="deploy")
