from os import environ


def get_consul_ui_port_string():
    if "CONSUL_DISABLE_UI" in environ:
        return "8501"
    return "8501:8501"
