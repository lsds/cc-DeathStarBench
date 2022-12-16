service {
  name = "rate"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 8084

  connect {
    sidecar_service {
      port = 20000

      check {
        name = "Connect Envoy Sidecar"
        tcp = "${CONSUL_SERVICE_IP_ADDR}:20000"
        interval ="10s"
      }

      proxy {
        upstreams = [
          {
            destination_name = "rate-memcached"
            local_bind_port  = 11211
          },
          {
            destination_name = "rate-mongodb"
            local_bind_port  = 27017
          }
        ]
      }
    }
  }

  check {
    id       = "rate-check"
    tcp     = "${CONSUL_SERVICE_IP_ADDR}:8084"
    interval = "1s"
  }
}
