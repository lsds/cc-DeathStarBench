service {
  name = "geo"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 8083

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
            destination_name = "geo-mongodb"
            local_bind_port  = 27017
          }
        ]
      }
    }
  }

  check {
    id       = "geo-check"
    tcp     = "${CONSUL_SERVICE_IP_ADDR}:8083"
    interval = "1s"
  }
}
