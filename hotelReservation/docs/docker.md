## Build the docker images

### Building images

There are a number of images that can be built. All the dockerfiles are
available in the `docker/` directory. We list them below:
* `cc-uservice-security/consul`: wrapper around the consul image. The tag for
  this image is out of sync with the code version and should only be updated
  if the Consul version is updated. In that case it needs to be built and
  pushed manually.
* `cc-uservice-security/mongo`: wrapper around the MongoDB image to run in an
  enclave and use Consul. The tag for this image is out of sync with the code
  version and should only be updated when we update the mongo, consul, or
  envoy version. In that case it needs to be built and pushed manually.
* `cc-uservice-security/memcached`: wrapper around the memcached image to run
  in an enclave and use Consul. The tag for this image is out of sync with the
  code and should only be updated when we update the memcached, consul, or
  envoy version. In that case it needs to be built and pushed manually.
* `cc-uservice-security/sof_root`: base image where we build all the major
  dependencies (`go`, `ego`, `consul`, and `envoy`) from scratch. The tag
  for this image is out of sync with the code version, and should only be
  updated when one of the dependencies' version changes.
* `cc-uservice-security/base`: parent image from which the client and worker
  images inherit. We install the SGX-related packages here, and copy the
  dependencies built in `sof-root`. The tag is also out-of-date.
* `cc-uservice-security/cli`: CLI image for development purposes. Gets rebuilt
  every time there is a new code release.
* `cc-uservice-security/dsb`: Lightweight worker image with the minimal
  dependencies to just run the microservices.


To build the docker images needed for development you need to start the CLI
from _outside_ the container, and run the build task:

```bash
source ./bin/workon.sh
# This will take a while the first time
inv docker.build --target base [--target mongo --nocache --push]
```
