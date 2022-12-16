## Configure `uk8s`

We install `microk8s` (or `uk8s` for short) in a development environment.
In addition, as part of the installation scripts, we also install the SGX
plugin for k8s.

You can bootstrap the single-node k8s cluster by running:

```bash
inv deploy.uk8s.install
```

That's it.

As part of the installation you will have seen the node name and the properties
detected by the SGX plugin.

### Debugging

To uninstall you may run:

```bash
inv deploy.uk8s.uninstall
```

To reset the cluster if something is not working:

```bash
inv deploy.uk8s.reset
```

The installation commands require `sudo`. In order to interact with `uk8s`
without `sudo` you will need to add your user to the `microk8s` group:

```bash
sudo usermod -aG microk8s ${USER}
newgrp microk8s
```

### Troubleshoot

Microk8s does not clean up `iptables` rules after uninstall, which means that
if the process is repeated several times, it can end up running out of IP
addresses to assign. In that case, you will see that even the basic system
pods (in namespace `kube-system`) fail to start.

To verify, after uninstall, run:

```bash
sudo iptables -L -v | grep -i kube | wc -l
```

If the result is different than 0, this problem may be happening.

To fix it, a system reboot is needed.

