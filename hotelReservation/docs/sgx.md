## SGX

CC-DSB supports running microservices inside SGX enclaves transparently to the
microservice code. To do so, you need to select one of SGX-powered runtimes:
* [EGo](https://github.com/edgelesssys/ego): microservices are compiled using
  `ertgo` and run inside an enclave using `ego-go`.
* [Gramine](https://github.com/gramineproject/gramine): microservices are
  compiled using `ertgo` and run inside an enclave using `gramine-sgx`.

The recommended set-up to run SGX workloads is to upgrade to a kernel version
`5.11` or newer, as the SGX driver is already installed. You can check your
kernel version by running `uname -r`.

