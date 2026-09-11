# Infraestructura AWS — Campeonatos UIDE

Crea una VPC pública mínima con una EC2 Amazon Linux 2023 `t3.micro`, EBS gp3 20 GB cifrado,
Elastic IP y reglas 22/80/443. **No** crea RDS, NAT Gateway, balanceador ni Route53.

## Arquitectura

```
Internet
   │  DNS: campeonatos-uide.shop  ->  Elastic IP  (registro A en Hostinger, manual)
   ▼
EC2 t3.micro (Amazon Linux 2023)
   ├─ Nginx (host)         :80 / :443   reverse proxy + /media/ por alias + TLS (certbot)
   └─ Docker Compose
        ├─ web   (Gunicorn :127.0.0.1:8000)  Django 5.2 + WhiteNoise (estáticos)
        └─ db    (mysql:8.0)  solo red interna, NO publica 3306
```

- **Base de datos**: MySQL 8 en contenedor. Datos en el volumen Docker `mysql_data`
  (sobre el disco EBS de la instancia). Sobrevive a `docker compose down` y a reiniciar la EC2.
- **media/**: bind mount `CampeonatosUIDE/media` en el disco de la EC2; lo sirve Nginx.
- **estáticos**: los sirve Django vía WhiteNoise (Nginx solo hace proxy).
- **Secretos**: `SECRET_KEY` y las contraseñas de MySQL se generan con `openssl` dentro de la
  EC2 la primera vez (`user-data.sh`) y quedan solo en `/opt/campeonatos-uide/CampeonatosUIDE/.env`.
  No pasan por Terraform, ni por el state, ni por los datos de user-data.

## Antes de aplicar

1. `terraform.tfvars`:
   ```
   cp terraform.tfvars.example terraform.tfvars
   ```
   Ajusta `ssh_allowed_cidr` a tu IP `/32` (`curl -s https://checkip.amazonaws.com`) y
   `public_key_path` a una clave pública existente. Si no tienes:
   ```
   ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\campeonatos-uide
   ```
   La **privada** (`campeonatos-uide`, sin extensión) se queda en tu máquina; `*.pem` y claves
   están en `.gitignore`.

2. Credenciales AWS en el entorno (`aws configure` o variables `AWS_ACCESS_KEY_ID` /
   `AWS_SECRET_ACCESS_KEY`).

3. ```
   cd terraform
   terraform init
   terraform plan
   ```
   Revisa el plan. **No** ejecutes `apply` hasta estar conforme.

## Después del primer `terraform apply`

1. Anota la IP:
   ```
   terraform output elastic_ip
   ```

2. **DNS en Hostinger** (`hpanel.hostinger.com` → Dominios → `campeonatos-uide.shop` → DNS).
   El DNS **no** lo gestiona Terraform. Deja los registros así:

   | Tipo  | Nombre | Valor / Contenido            | TTL |
   |-------|--------|------------------------------|-----|
   | A     | `@`    | *(la Elastic IP del output)* | 300 |
   | A     | `www`  | *(la misma Elastic IP)*      | 300 |

   Borra el registro `A @ -> 2.57.91.91` que trae Hostinger por defecto y el
   `CNAME www -> campeonatos-uide.shop` (se sustituye por el `A www`). Espera a que propague
   (`nslookup campeonatos-uide.shop`).

3. **HTTPS** (solo cuando el DNS ya resuelva a la EC2): conéctate por SSH y ejecuta
   ```
   sudo certbot --nginx -d campeonatos-uide.shop -d www.campeonatos-uide.shop
   ```
   Certbot añade el `server` de 443, la redirección 80→443 y deja la renovación automática.

4. Activa la redirección en Django: en `/opt/campeonatos-uide/CampeonatosUIDE/.env` pon
   `SECURE_SSL_REDIRECT=True` y `docker compose up -d`.

## CI/CD

- `.github/workflows/ci.yml`: pruebas y `check --deploy` (ya existía).
- `.github/workflows/deploy.yml`: en cada push a `main`, SSH a la EC2 → `git pull` →
  `docker compose build` → `up -d` → `migrate`. Se ejecuta **solo** si el repo tiene los
  secretos `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`, `EC2_APP_DIR` (este último = `/opt/campeonatos-uide`).
  La clave privada vive únicamente en GitHub Secrets. Terraform no se ejecuta nunca aquí.

## Costos (aprox., us-east-1)

| Recurso                     | Coste |
|-----------------------------|-------|
| EC2 `t3.micro`              | ~7–8 USD/mes encendida (elegible free tier el primer año) |
| EBS gp3 20 GB               | ~1,6 USD/mes, **también con la EC2 apagada** |
| IPv4 pública / Elastic IP   | ~3,6 USD/mes por IP (AWS cobra toda IPv4 pública; una EIP sin asociar cuesta igual o más) |
| Transferencia de salida     | primeros 100 GB/mes gratis |

No es 0 USD. Apagar la EC2 ahorra el cómputo pero **no** el EBS ni la IPv4.

## `terraform destroy`

Elimina EC2, EIP, SG y red. El **volumen raíz** tiene `delete_on_termination = false`, así que
queda un EBS huérfano que debes borrar a mano desde la consola EC2 → Volumes (o seguirá
facturando). Los datos de MySQL viven en ese volumen: `destroy` = se pierden salvo que hagas
copia antes (`docker compose exec db mysqldump ...`).

## Límites de `t3.micro`

1 GB de RAM. `user-data.sh` crea 2 GB de swap porque el build de la imagen (pandas, pillow,
reportlab) más MySQL no caben en RAM. El primer `apply` tarda varios minutos en tener la app
arriba (build + arranque de MySQL). Con muchos usuarios concurrentes escribiendo, este tamaño
se queda corto; para eso habría que subir a `t3.small`.
