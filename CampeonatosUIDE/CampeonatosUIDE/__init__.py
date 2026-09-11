# Driver MySQL en producción sin compilar nada.
#
# El proyecto se desarrolló sobre SQLite. En el despliegue (contenedores) la
# base de datos es MySQL, y django-environ traduce `mysql://...` al backend
# `django.db.backends.mysql`, que hace `import MySQLdb`. En lugar de
# `mysqlclient` (extensión en C que exige toolchain de compilación en la
# imagen y RAM que un t3.micro no sobra), usamos PyMySQL, que es Python puro,
# y le pedimos que se registre con el nombre `MySQLdb`.
#
# Si no hay PyMySQL instalado (p. ej. entorno local con SQLite), no pasa nada.
try:
    import pymysql
except ModuleNotFoundError:
    pass
else:
    pymysql.install_as_MySQLdb()
