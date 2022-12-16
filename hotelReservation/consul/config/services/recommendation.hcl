service {
  name = "recommendation"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 8085

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
            destination_name = "recommendation-mongodb"
            local_bind_port  = 27017
          }
        ]
      }
    }
  }

  check {
    id       = "recommendation-check"
    tcp     = "${CONSUL_SERVICE_IP_ADDR}:8085"
    interval = "1s"
  }
}
