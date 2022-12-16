service {
  name = "profile-memcached"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 11211

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
    id       = "profile-memcached-check"
    tcp     = "${CONSUL_SERVICE_IP_ADDR}:11211"
    interval = "1s"
  }
}
