service {
  name = "search"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 8082

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
            destination_name = "geo"
            local_bind_port  = 8083
          },
          {
            destination_name = "rate"
            local_bind_port  = 8084
          }
        ]
      }
    }
  }

  check {
    id       = "search-check"
    tcp      = "${CONSUL_SERVICE_IP_ADDR}:8082"
    interval = "1s"
  }
}
