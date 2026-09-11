resource "aws_security_group" "web" {
  name   = "campeonatos-uide-web"
  vpc_id = aws_vpc.main.id
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Salida solo por los puertos que la instancia realmente necesita para
  # actualizar paquetes del sistema, tirar de PyPI/Docker Hub y resolver
  # DNS -- no "cualquier puerto, cualquier protocolo" como antes.
  # El CIDR sigue siendo 0.0.0.0/0 porque no se conoce de antemano la IP
  # de los mirrors/registries; es la salida habitual de un servidor con
  # acceso normal a internet, no una regla sin acotar. Trivy (AVD-AWS-0104)
  # marca cualquier egress con 0.0.0.0/0 sin mirar el puerto, asi que esto
  # sigue apareciendo aunque ya no sea "todo el trafico, a donde sea":
  # riesgo aceptado y documentado, no una regla ignorada a ciegas.
  #trivy:ignore:AVD-AWS-0104
  egress {
    description = "HTTPS (paquetes, Docker Hub, APIs externas)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  #trivy:ignore:AVD-AWS-0104
  egress {
    description = "HTTP (mirrors que aun redirigen desde 80)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  #trivy:ignore:AVD-AWS-0104
  egress {
    description = "DNS"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  #trivy:ignore:AVD-AWS-0104
  egress {
    description = "DNS sobre TCP (respuestas grandes)"
    from_port   = 53
    to_port     = 53
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  #trivy:ignore:AVD-AWS-0104
  egress {
    description = "NTP (sincronizacion de reloj)"
    from_port   = 123
    to_port     = 123
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "campeonatos-uide-web" }
}
