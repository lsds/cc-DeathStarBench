service {
  name = "recommendation-mongodb"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 27017

  connect {
    sidecar_service {
      port = 20000

      check {
        name = "Connect Envoy Sidecar"
        tcp = "${CONSUL_SERVICE_IP_ADDR}:20000"
        interval ="10s"
      }
    }
  }

  check {
    id       = "recommendation-mongodb-check"
    tcp     = "${CONSUL_SERVICE_IP_ADDR}:27017"
    interval = "1s"
  }
}
