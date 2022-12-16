service {
  name = "profile"
  address = "${CONSUL_SERVICE_IP_ADDR}"
  port = 8081

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
            destination_name = "profile-memcached"
            local_bind_port  = 11211
          },
          {
            destination_name = "profile-mongodb"
            local_bind_port  = 27017
          }
        ]
      }
    }
  }

  check {
    id       = "profile-check"
    tcp     = "${CONSUL_SERVICE_IP_ADDR}:8081"
    interval = "1s"
  }
}
