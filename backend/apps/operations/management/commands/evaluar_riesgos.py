"""Comando programable de la automatización de riesgos.

En producción se ejecuta cada minuto mediante un planificador (cron,
task scheduler de la plataforma de nube):

    * * * * *  cd /app && python manage.py evaluar_riesgos
"""
from collections import Counter

from django.core.management.base import BaseCommand

from apps.operations.services.risk import evaluar_activas


class Command(BaseCommand):
    help = (
        "Evalúa las entregas activas contra la hora límite y genera "
        "alertas de riesgo o retraso (regla de automatización)."
    )

    def handle(self, *args, **opciones):
        evaluaciones = evaluar_activas()
        conteo = Counter(evaluacion.nivel for evaluacion in evaluaciones)
        self.stdout.write(
            self.style.SUCCESS(
                f"Entregas evaluadas: {len(evaluaciones)} → "
                f"normal={conteo.get('NORMAL', 0)}, "
                f"en_riesgo={conteo.get('EN_RIESGO', 0)}, "
                f"retrasada={conteo.get('RETRASADA', 0)}"
            )
        )
