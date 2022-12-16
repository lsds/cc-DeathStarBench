node_name = "consul-server"
data_dir = "/consul/data"
log_level = "INFO"
server = true

bootstrap_expect = 1
ui_config {
  enabled = true
}

bind_addr = "0.0.0.0"
client_addr = "0.0.0.0"

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
    # We set this value to false (even though it should be true) to allow
    # accessing the Consul UI through a browser without having to do any
    # certificate management
    verify_incoming = false
    verify_outgoing = true
    ca_file = "/tls-server/consul-agent-ca.pem"
    cert_file = "/tls-server/dc1-server-consul-0.pem"
    key_file = "/tls-server/dc1-server-consul-0-key.pem"
  }

  grpc {
    verify_incoming = false
  }

  internal_rpc {
    verify_server_hostname = true
  }
}
