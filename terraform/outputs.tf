output "instance_id" { value = aws_instance.app.id }
output "public_ip" { value = aws_eip.app.public_ip }
output "elastic_ip" { value = aws_eip.app.public_ip }
output "ssh_command" { value = "ssh -i <ruta-a-tu-clave-privada> ec2-user@${aws_eip.app.public_ip}" }
output "application_url" { value = "https://${var.domain_name}" }

# Pega este valor en el registro A "@" de Hostinger (y en "www" si lo usas).
output "dns_a_record_value" { value = aws_eip.app.public_ip }
