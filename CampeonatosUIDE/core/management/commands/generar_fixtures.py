# core/management/commands/generar_fixtures.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from core.models import Campeonato, Partido
from core.utils.generar_fixture_liga import generar_fixture_liga
from core.utils.generar_fixture_fase_grupos import generar_fixture_fase_grupos
from core.utils.generar_fixture_eliminatoria import generar_fixture_eliminatoria

class Command(BaseCommand):
    help = 'Genera el fixture para campeonatos cuya fecha de inscripción ha finalizado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--campeonato_nombre',
            type=str,
            help='Nombre del campeonato específico para generar/regenerar el fixture, ignorando los filtros por defecto.',
            nargs='?'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando proceso de generación de fixtures...'))

        campeonato_nombre = options['campeonato_nombre']

        if campeonato_nombre:
            campeonatos_para_generar = Campeonato.objects.filter(nombre=campeonato_nombre)
            if not campeonatos_para_generar.exists():
                self.stderr.write(self.style.ERROR(f'Error: El campeonato "{campeonato_nombre}" no existe.'))
                return
            self.stdout.write(self.style.SUCCESS(f'Intentando regenerar fixture para el campeonato: {campeonato_nombre}'))
        else:
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
                with transaction.atomic():
                    # 1) BORRAR anteriores SOLO dentro de una transacción que podremos revertir
                    Partido.objects.filter(campeonato=campeonato).delete()
                    self.stdout.write(self.style.WARNING(f'Partidos existentes para {campeonato.nombre} eliminados.'))

                    # 2) Generar y CONTAR
                    creados = 0
                    if campeonato.tipo_campeonato == 'LIGA':
                        creados = generar_fixture_liga(campeonato.id) or 0
                    elif campeonato.tipo_campeonato == 'FASE_GRUPOS':
                        creados = generar_fixture_fase_grupos(campeonato.id) or 0
                    elif campeonato.tipo_campeonato == 'ELIMINATORIA':
                        creados = generar_fixture_eliminatoria(campeonato.id) or 0

                    self.stdout.write(self.style.SUCCESS(f'Total partidos creados: {creados}'))

                    # Los partidos se crean sin árbitro. La asignación es
                    # manual, desde /partidos/<id>/asignar-arbitro/: aquí se
                    # llamaba a asignar_arbitros_a_partidos, que no existe en
                    # el proyecto, y ese import hacía que el comando fallara
                    # con ImportError antes de ejecutar nada.

                    # 3) Validar resultado: si 0, REVERSIÓN
                    if not creados:
                        raise ValueError('No se crearon partidos. Se revierte la operación y NO se marcará como generado.')

                    # 4) Marcar solo si sí creó
                    campeonato.fixture_generado = True
                    campeonato.estado = 'EN_CURSO'
                    campeonato.save(update_fields=['fixture_generado', 'estado'])

                    self.stdout.write(self.style.SUCCESS(
                        f'Fixture para {campeonato.nombre} generado y estado actualizado a EN CURSO.'
                    ))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error al generar fixture para {campeonato.nombre}: {e}'))

        self.stdout.write(self.style.SUCCESS('Proceso de generación de fixtures finalizado.'))
