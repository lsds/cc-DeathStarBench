from json import dump, load
from os import chdir, environ, remove
from subprocess import run


def update_json(service_path, service_name):
    """
    Update JSON file generated as part of `ego sign` to include the trusted
    files and trusted environment variables
    """
    chdir(service_path)
    filename = "enclave.json"
    try:
        f = open(filename, "r")
    except OSError:
        print(
            "File {} not found. Have you signed the binaries?".format(filename)
        )
        exit(1)
    with f:
        data = load(f)
        data["env"] = [
            {
                "name": "DSB_CODE_DIR",
                "value": "/code/DeathStarBench/hotelReservation",
            },
            {
                "name": "ENABLE_CONSUL",
                "value": environ["ENABLE_CONSUL"],
            },
            {
                "name": "EDG_MARBLE_UUID_FILE",
                "value": "uuid",
            },
            {
                "name": "EDG_MARBLE_TYPE",
                "value": service_name,
            },
        ]
        data["files"] = [
            {
                "source": "/code/DeathStarBench/hotelReservation/config.json",
                "target": "/code/DeathStarBench/hotelReservation/config.json",
            }
        ]
    remove(filename)
    with open(filename, "w") as f:
        dump(data, f, indent=4)
    f.close()


def sign(binary_name, binary_path):
    """
    Sign ego-compiled binary. We sign each binary twice. The first time the
    signature generates a JSON file, we then update the JSON file to include
    the trusted files and environemnt variables, and then sign again to bind
    the new JSON measure to the binary.
    """
    cmd = [
        "{} sign".format("ego"),
        "{}".format(binary_name),
    ]
    cmd = " ".join(cmd)
    run(cmd, shell=True, check=True, cwd=binary_path)
    update_json(binary_path, binary_name)
    # Re-signing is necessary after updating the json
    run(cmd, shell=True, check=True, cwd=binary_path)
