from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Campeonato
from core.utils.generar_fixture_liga import generar_fixture_liga
from core.utils.generar_fixture_fase_grupos import generar_fixture_fase_grupos
from core.utils.generar_fixture_eliminatoria import generar_fixture_eliminatoria

class Command(BaseCommand):
    help = 'Genera el fixture para campeonatos cuya fecha de inscripción ha finalizado.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando proceso de generación de fixtures...'))
        
        campeonatos_para_generar = Campeonato.objects.filter(
            fecha_fin_inscripcion__lte=timezone.now().date(),
            fixture_generado=False,
            estado='INSCRIPCION'
        )

        if not campeonatos_para_generar.exists():
            self.stdout.write(self.style.SUCCESS('No hay campeonatos que requieran generación de fixture.'))
            return

        for campeonato in campeonatos_para_generar:
            self.stdout.write(f'Generando fixture para el campeonato: {campeonato.nombre}')
            
            try:
                if campeonato.tipo_campeonato == 'LIGA':
                    generar_fixture_liga(campeonato.id)
                elif campeonato.tipo_campeonato == 'FASE_GRUPOS':
                    generar_fixture_fase_grupos(campeonato.id)
                elif campeonato.tipo_campeonato == 'ELIMINATORIA':
                    generar_fixture_eliminatoria(campeonato.id)
                
                campeonato.fixture_generado = True
                campeonato.estado = 'CERRADO'
                campeonato.save()
                
                self.stdout.write(self.style.SUCCESS(f'Fixture para {campeonato.nombre} generado y estado actualizado.'))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error al generar fixture para {campeonato.nombre}: {e}'))

        self.stdout.write(self.style.SUCCESS('Proceso de generación de fixtures finalizado.'))
