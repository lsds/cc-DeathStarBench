service {
  name = "user"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 8086

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
            destination_name = "user-mongodb"
            local_bind_port  = 27017
          }
        ]
      }
    }
  }

  check {
    id       = "user-check"
    tcp      = "${CONSUL_SERVICE_IP_ADDR}:8086"
    interval = "1s"
  }
}
