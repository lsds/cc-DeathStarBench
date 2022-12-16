Kind = "service-intentions"
Name = "${CONSUL_SERVICE_NAME}"
Sources = [
  {
    Name   = "*"
    Action = "deny"
  },
  {
    Name   = "geo"
    Action = "allow"
  }
]
