service {
  name = "frontend"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 5000

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
            destination_name = "profile"
            local_bind_port  = 8081
          },
          {
            destination_name = "search"
            local_bind_port  = 8082
          },
          {
            destination_name = "recommendation"
            local_bind_port  = 8085
          },
          {
            destination_name = "user"
            local_bind_port  = 8086
          },
          {
            destination_name = "reservation"
            local_bind_port  = 8087
          }
        ]
      }
    }
  }

  check {
    id       = "frontend-check"
    tcp      = "${CONSUL_SERVICE_IP_ADDR}:5000"
    interval = "1s"
  }
}
