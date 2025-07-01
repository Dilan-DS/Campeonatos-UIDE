from django.urls import path
from .views import vista_inicio, vista_login, vista_logout, vista_registro, vista_inicio_publico, detalle_equipo

urlpatterns = [
    path('', vista_inicio_publico, name='inicio_publico'),
    path('panel/', vista_inicio, name='inicio'),
    path('login/', vista_login, name='login'),
    path('logout/', vista_logout, name='logout'),
    path('registro/', vista_registro, name='registro'),
    path('equipo/<int:id>/', detalle_equipo, name='detalle_equipo'),
]
