Kind = "service-intentions"
Name = "${CONSUL_SERVICE_NAME}"
Sources = [
  {
    Name   = "*"
    Action = "deny"
  },
  {
    Name   = "user"
    Action = "allow"
  }
]
