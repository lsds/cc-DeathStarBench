# CC-DeathStarBench

This repository is a fork of the
[DeathStarBench](https://github.com/delimitrou/DeathStarBench) where
microservices have been migrated to run in trusted execution environments (TEEs) using
Intel SGX. Currently, we only the [Hotel
Reservation](./hotelReservation) benchmark has been CC-fied. Check the
`hotelReservation/README.md` file there for more details. This prototype
is provided as is without guarantees of security, performance or function.

## Contributors

Transformation was part of an internship project and mainly contributed to by

* Carlos Segarra <cs1620@imperial.ac.uk>
* Ines Messadi <messadi@ibr.cs.tu-bs.de>

## DeathStar Publications

The original DeathStar Benchmark is described in a publication that can be found at
["An Open-Source Benchmark Suite for Microservices and Their Hardware-Software Implications for Cloud and Edge Systems"](http://www.csl.cornell.edu/~delimitrou/papers/2019.asplos.microservices.pdf),
Y. Gan et al., ASPLOS 2019. Please cite the publication when referring to
the original benchmark.
