service {
  name = "reservation"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 8087

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
            destination_name = "reservation-memcached"
            local_bind_port  = 11211
          },
          {
            destination_name = "reservation-mongodb"
            local_bind_port  = 27017
          },
          {
            destination_name = "user"
            local_bind_port  = 8086
          }
        ]
      }
    }
  }

  check {
    id       = "reservation-check"
    tcp     = "${CONSUL_SERVICE_IP_ADDR}:8087"
    interval = "1s"
  }
}
