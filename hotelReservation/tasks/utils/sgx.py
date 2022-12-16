from os.path import exists


def get_sgx_device_mount_path():
    """
    Get the mount path for the installed SGX driver
    """
    # The in-tree linux kernel SGX driver (available from 5.11 onwards) creates
    # the enclave device at /dev/sgx_enclave and /dev/sgx_provision. Thus, we
    # give preference to this path and, eventually, will be the only one that
    # we support
    if exists("/dev/sgx_enclave") and exists("/dev/sgx_provision"):
        driver_mount_path = "/dev/sgx_enclave"
        provision_mount_path = "/dev/sgx_provision"
        print(
            "Detected SGX driver at: /dev/sgx_enclave and /dev/sgx_provision"
        )
    # In contrast, the out-of-tree DCAP driver uses sgx subdirectory, i.e.,
    # /dev/sgx/enclave and /dev/sgx/provision
    elif exists("/dev/sgx/enclave") and exists("/dev/sgx/provision"):
        driver_mount_path = "/dev/sgx/enclave"
        provision_mount_path = "/dev/sgx/provision"
        print(
            "Detected SGX driver at: /dev/sgx/enclave and /dev/sgx/provision"
        )
    # Lastly, older drivers use /dev/isgx
    elif exists("/dev/isgx"):
        driver_mount_path = "/dev/isgx"
        print("Detected SGX driver at: /dev/isgx")
    else:
        print("SGX driver not found. Consider upgrading the kernel to >5.11.")
        print("Alternatively, you may install the out-of-tree driver using:")
        print("\t$ source ./bin/workon.sh")
        print("\t$ inv sgx.install-driver")
        print("For more information see the docs on SGX: ./docs/sgx.md")
        raise RuntimeError("SGX driver not found!")
    return driver_mount_path, provision_mount_path
