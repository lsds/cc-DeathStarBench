from os import environ, makedirs
from os.path import exists, isfile, join
from subprocess import run
from tasks.env import GRAMINE_BUILD_DIR, PROJ_ROOT

GRAMINE_LOG_LEVEL = "error"
GRAMINE_MANIFEST_DIR = join(PROJ_ROOT, "gramine-manifests")
GRAMINE_KEY_PATH = join(GRAMINE_BUILD_DIR, "gramine_build_key.pem")


def generate_private_key(overwrite=False):
    """
    Generate private key to sign Gramine binaries
    """
    key_exists = isfile(GRAMINE_KEY_PATH)
    if key_exists and not overwrite:
        return
    if not exists(GRAMINE_BUILD_DIR):
        makedirs(GRAMINE_BUILD_DIR)

    keygen_cmd = [
        "gramine-sgx-gen-private-key",
        "-f" if key_exists else "",
        GRAMINE_KEY_PATH,
    ]
    keygen_cmd = " ".join(keygen_cmd)
    run(keygen_cmd, check=True, shell=True)


def sign(binary_name, binary_path, manifest_name="service"):
    """
    Sign binaries using gramine tools
    """
    binary_full_path = join(binary_path, binary_name)
    manifest_full_path = join(
        GRAMINE_MANIFEST_DIR, "{}.manifest.template".format(manifest_name)
    )
    # Generate the manifest files templating the required variables
    template_vars = {
        "log_level": GRAMINE_LOG_LEVEL,
        "entrypoint": binary_full_path,
        "enable_consul": environ["ENABLE_CONSUL"],
    }
    cmd_generate = [
        "gramine-manifest",
        "{}".format(
            " ".join(
                [
                    "-D{}={}".format(var, template_vars[var])
                    for var in template_vars
                ]
            )
        ),
        manifest_full_path,
        "{}.manifest".format(binary_full_path),
    ]
    cmd_generate = " ".join(cmd_generate)
    run(cmd_generate, shell=True, check=True, cwd=PROJ_ROOT)

    # Sign the binary using the tempalted manifest file. Signing generates both
    # a .sig file and a .manifest.sgx file
    cmd_sign = [
        "gramine-sgx-sign",
        "--manifest {}.manifest".format(binary_full_path),
        "--key {}".format(GRAMINE_KEY_PATH),
        "--output {}.manifest.sgx".format(binary_full_path),
    ]
    cmd_sign = " ".join(cmd_sign)
    run(cmd_sign, shell=True, check=True, cwd=binary_path)

    cmd_get_token = [
        "gramine-sgx-get-token",
        "--output {}.token".format(binary_full_path),
        "--sig {}.sig".format(binary_full_path),
    ]
    cmd_get_token = " ".join(cmd_get_token)
    run(cmd_get_token, shell=True, check=True, cwd=binary_path)
