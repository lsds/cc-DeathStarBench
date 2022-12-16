from random import randint
from requests import get, post
from tasks.utils.config import get_config_value


def get_lat_lon_str():
    lat = 38.0235 + (randint(0, 480) - 240.5) / 1000.0
    lon = -122.095 + (randint(0, 324) - 157.0) / 1000.0
    return "{}".format(lat), "{}".format(lon)


def get_frontend_host_port():
    return get_config_value("frontend_host"), get_config_value("frontend_port")


def _do_request(req_func, login_path, args):
    args_string = ["{}={}".format(k, args[k]) for k in args]
    args_string = "&".join(args_string)
    url = login_path + "?" + args_string
    r = req_func(url)
    if not r.ok:
        print("Error running request with URL: {}".format(url))
        raise RuntimeError("Error running request")


def _get_url_prefix():
    protocol = "http"
    host, port = get_frontend_host_port()

    # In an RKE deployment we must use an Ingress service with a special prefix
    # path in order to hit the cluster
    kind = get_config_value("kind")
    if kind == "rke":
        ns = get_config_value("k8s_namespace")
        return "{}://{}:{}/{}".format(protocol, host, port, ns)
    return "{}://{}:{}".format(protocol, host, port)


def get_user_passwd():
    user_id = randint(0, 499)
    return "Cornell_{}".format(user_id), "{}".format(user_id) * 10


def get_inout_date_str():
    in_date = randint(1, 23)
    out_date = randint(in_date + 1, 24)

    if in_date <= 9:
        in_date_str = "2015-04-0{}".format(in_date)
    else:
        in_date_str = "2015-04-{}".format(in_date)
    if out_date <= 9:
        out_date_str = "2015-04-0{}".format(out_date)
    else:
        out_date_str = "2015-04-{}".format(out_date)

    return in_date_str, out_date_str


def do_login_request():
    login_path = _get_url_prefix() + "/user"
    user, password = get_user_passwd()
    args = {
        "username": user,
        "password": password,
    }
    _do_request(get, login_path, args)


def do_reservation_request():
    login_path = _get_url_prefix() + "/reservation"
    user, password = get_user_passwd()
    lat_str, lon_str = get_lat_lon_str()
    in_date_str, out_date_str = get_inout_date_str()
    args = {
        "username": user,
        "password": password,
        "number": "1",
        "inDate": in_date_str,
        "outDate": out_date_str,
        "lat": lat_str,
        "lon": lon_str,
        "hotelId": randint(1, 79),
        "customerName": user,
    }
    _do_request(post, login_path, args)


def do_recommendations_request():
    login_path = _get_url_prefix() + "/recommendations"
    coin = randint(1, 3)
    if coin == 1:
        crit = "dis"
    elif coin == 2:
        crit = "rate"
    else:
        crit = "price"
    lat_str, lon_str = get_lat_lon_str()
    args = {
        "require": crit,
        "lat": lat_str,
        "lon": lon_str,
    }
    _do_request(get, login_path, args)


def do_search_request():
    login_path = _get_url_prefix() + "/hotels"
    lat_str, lon_str = get_lat_lon_str()
    in_date_str, out_date_str = get_inout_date_str()
    args = {
        "inDate": in_date_str,
        "outDate": out_date_str,
        "lat": lat_str,
        "lon": lon_str,
    }
    _do_request(get, login_path, args)
