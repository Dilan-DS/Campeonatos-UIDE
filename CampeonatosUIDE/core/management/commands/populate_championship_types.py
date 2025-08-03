from django.core.management.base import BaseCommand
from core.models import Deporte, TipoCampeonato

class Command(BaseCommand):
    help = 'Poblar deportes y tipos de campeonato predefinidos'

    def handle(self, *args, **options):
        deportes_con_tipos = {
            'FUTBOL': ['Round-Robin', 'Fase de grupos + Eliminatoria'],
            'BASQUET': ['Round-Robin', 'Eliminación directa'],
            'AJEDREZ': ['Eliminación directa'],
            'PING PONG': ['Eliminación directa'],
            'VIDEOJUEGOS': ['Fase de grupos + Eliminatoria'],
            'ECUABOLY': ['Round-Robin'],
            'TENIS': ['Eliminación directa'],
            'FUTBOLIN': ['Round-Robin', 'Eliminación directa'],
        }

        for deporte_nombre, tipos in deportes_con_tipos.items():
            deporte, _ = Deporte.objects.get_or_create(nombre=deporte_nombre)
            for tipo_nombre in tipos:
                tipo, _ = TipoCampeonato.objects.get_or_create(nombre=tipo_nombre)
                tipo.deportes_permitidos.add(deporte)
                tipo.save()

        self.stdout.write(self.style.SUCCESS("Tipos de campeonato y deportes creados correctamente."))
