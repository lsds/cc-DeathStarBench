Kind = "service-intentions"
Name = "${CONSUL_SERVICE_NAME}"
Sources = [
  {
    Name   = "*"
    Action = "deny"
  },
  {
    Name   = "frontend"
    Action = "allow"
  },
  {
    Name   = "reservation"
    Action = "allow"
  }
]
