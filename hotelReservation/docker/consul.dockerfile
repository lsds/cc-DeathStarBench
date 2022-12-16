ARG CONSUL_VERSION
FROM hashicorp/consul:${CONSUL_VERSION}

WORKDIR /tls-server
# Generate the CA certificate
RUN consul tls ca create

# Generate the certificate for the server
# The following command needs to be run as many times as servers there will be
RUN consul tls cert create -server -dc dc1
# In contrast, we use the same certificate for all the clients
RUN consul tls cert create -client

# Copy just the server CA to a different directory we can share
WORKDIR /tls-client
RUN cp /tls-server/consul-agent-ca.pem /tls-client/consul-agent-ca.pem
RUN cp /tls-server/dc1-client-consul-0-key.pem /tls-client/dc1-client-consul-0-key.pem
RUN cp /tls-server/dc1-client-consul-0.pem /tls-client/dc1-client-consul-0.pem

# Change permissions
RUN chown -R consul:consul /tls-server && \
    chown -R consul:consul /tls-client
