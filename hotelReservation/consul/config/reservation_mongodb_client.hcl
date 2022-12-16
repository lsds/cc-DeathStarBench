node_name = "client-reservation-mongodb"
data_dir = "/consul/data"
log_level = "INFO"

retry_join = ["${CONSUL_IP_ADDR}"]

connect {
  enabled = true
}

ports {
  http = -1
  https = 8501
  grpc = 8502
}

enable_central_service_config = true

encrypt = "FZrxFpIJh898/HEfXB67l3q0LLzCDwX/1Q8Uz1+xEFo="

tls {
  defaults {
    verify_incoming = true
    verify_outgoing = true
    ca_file = "${CONSUL_CACERT}"
    cert_file = "${CONSUL_CLIENT_CERT}"
    key_file = "${CONSUL_CLIENT_KEY}"
  }

  grpc {
    verify_incoming = false
  }

  internal_rpc {
    verify_server_hostname = true
  }
}
