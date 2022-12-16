from configparser import ConfigParser
from datetime import datetime
from os.path import exists, join
from tasks.env import PROJ_ROOT

DSB_CONFIG_FILE = join(PROJ_ROOT, "dsb.ini")


def get_dsb_config():
    """
    Parse the deployent config file
    """
    config = ConfigParser()

    if not exists(DSB_CONFIG_FILE):
        print("Creating config file at {}".format(DSB_CONFIG_FILE))

        with open(DSB_CONFIG_FILE, "w") as fh:
            config.write(fh)
    else:
        config.read(DSB_CONFIG_FILE)

    return config


def get_config_value(key):
    """
    Get a value from the config file
    """
    config = get_dsb_config()

    if config.has_section("DSB"):
        return config["DSB"].get(key)
    else:
        print("Config file does not have DSB section")
        raise RuntimeError("Malformed config file")


def write_config_file(kwargs):
    print("\n----- INI file -----\n")
    print("Overwriting config file at {}\n".format(DSB_CONFIG_FILE))

    with open(DSB_CONFIG_FILE, "w") as fh:
        fh.write("[DSB]\n")

        # This comment line can't be outside of the Faasm section
        fh.write("# Auto-generated at {}\n".format(datetime.now()))
        fh.write("kind = {}\n".format(kwargs["kind"]))
        fh.write("k8s_namespace = {}\n".format(kwargs["k8s_namespace"]))
        fh.write("frontend_host = {}\n".format(kwargs["frontend_host"]))
        fh.write("frontend_port = {}\n".format(kwargs["frontend_port"]))

    # Print the generated contents to stdout
    with open(DSB_CONFIG_FILE, "r") as fh:
        print(fh.read())
