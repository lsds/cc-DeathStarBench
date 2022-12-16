from invoke import task
from os import makedirs
from subprocess import run, check_output
from sys import stdout
from os.path import exists, join


@task
def install_driver(ctx):
    """
    Install SGX driver
    """
    # Clone repo
    install_dir = "/opt/intel"
    if not exists(install_dir):
        makedirs(install_dir)
    run(
        "sudo git clone https://github.com/intel/linux-sgx-driver.git",
        shell=True,
        check=True,
        cwd=install_dir,
    )

    # Run make
    repo_path = join(install_dir, "linux-sgx-driver")
    run("make", shell=True, check=True, cwd=repo_path)

    # Create directory
    version_info = (
        check_output("uname -r", shell=True).decode(stdout.encoding).strip()
    )
    cmd = "sudo mkdir -p /lib/modules/{}/kernel/drivers/intel/sgx".format(
        version_info
    )
    print(cmd)
    run(cmd, shell=True, check=True)

    cmd = "sudo cp isgx.ko /lib/modules/{}/kernel/drivers/intel/sgx".format(
        version_info
    )
    print(cmd)
    run(cmd, shell=True, check=True)

    cmd = (
        "sudo sh -c "
        '"cat /etc/modules | grep -Fxq isgx || echo isgx >> /etc/modules"'
    )
    print(cmd)
    run(cmd, shell=True, check=True)

    # Load the module
    run("sudo /sbin/depmod", shell=True, check=True)
    run("sudo /sbin/modprobe isgx", shell=True, check=True)
    print("SGX driver succesfully installed")
