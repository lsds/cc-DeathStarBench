ARG DSB_VERSION
FROM cc-uservice-security/cli:${DSB_VERSION} as cli
FROM cc-uservice-security/base:0.2.1

# We copy the built binaries and sources from the CLI image
COPY --from=cli /code/DeathStarBench/hotelReservation \
    /code/DeathStarBench/hotelReservation
WORKDIR /code/DeathStarBench/hotelReservation
