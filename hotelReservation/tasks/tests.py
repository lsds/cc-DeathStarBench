from invoke import task
from os import environ
from tasks.utils.config import get_config_value
from tasks.deploy.utils.k8s import get_k8s_env_vars
from tasks.utils.requests import (
    do_login_request,
    do_recommendations_request,
    do_reservation_request,
    do_search_request,
)


def set_env_vars():
    """
    Set the right environment variables depending on the deployment kind
    """
    kind = get_config_value("kind")
    if kind == "uk8s":
        environ.update(get_k8s_env_vars(kind))


@task(default=True)
def e2e(ctx, req_type=None):
    """
    Run end-to-end tests of all the exposed endpoints
    """
    num_requests = 10

    # Set the env. variables for requests
    set_env_vars()

    if req_type:
        if req_type == "login":
            do_login_request()
        elif req_type == "reservation":
            do_reservation_request()
        elif req_type == "recommendation":
            do_recommendations_request()
        elif req_type == "search":
            do_search_request()
        else:
            print("Unrecognised req. type: {}".format(req_type))
            return
    else:
        for _ in range(num_requests):
            do_login_request()
            do_reservation_request()
            do_recommendations_request()
            do_search_request()

    print("E2E tests executed succesfully!")
