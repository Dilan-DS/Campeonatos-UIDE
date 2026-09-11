variable "aws_region" {
  type    = string
  default = "us-east-1"
}
variable "availability_zone" {
  type    = string
  default = "us-east-1a"
}
variable "instance_type" {
  type    = string
  default = "t3.micro"
}
variable "ssh_allowed_cidr" {
  type = string
}
variable "key_name" {
  type    = string
  default = "campeonatos-uide"
}
variable "public_key_path" {
  type = string
}
variable "repository_url" {
  type    = string
  default = "https://github.com/Dilan-DS/Campeonatos-UIDE.git"
}
variable "domain_name" {
  type    = string
  default = "campeonatos-uide.shop"
}

variable "db_name" {
  type    = string
  default = "campeonatos_uide"
}

variable "db_user" {
  type    = string
  default = "campeonatos"
}
