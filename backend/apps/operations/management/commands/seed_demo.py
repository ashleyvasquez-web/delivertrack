"""Datos sintéticos de demostración (sin datos personales reales).

Uso:
    python manage.py seed_demo             # crea datos si la base está vacía
    python manage.py seed_demo --forzar    # borra todo y regenera

Genera: 1 administrador, 3 repartidores, entregas históricas de los
últimos días y entregas "en vivo" que muestran la automatización
(una EN_RIESGO y una RETRASADA) para la demostración.
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Repartidor
from apps.operations.models import (
    Alerta,
    Entrega,
    HistorialEstado,
    Incidencia,
    Pedido,
)
from apps.operations.services.risk import evaluar_activas

random.seed(7)

CLAVE_DEMO = "Demo1234!"

CLIENTES = [
    "Ferretería El Buen Precio",
    "Pulpería Doña Lola",
    "Farmacia Central",
    "Tienda María Elena",
    "Librería Escolar",
    "Panadería La Espiga",
    "Distribuidora El Sol",
    "Vivero La Colina",
]
BARRIOS = [
    "Colonia Centro",
    "Villa Nueva",
    "Barrio San Juan",
    "Residencial Los Álamos",
    "Zona 1",
    "Colina Sur",
    "Barrio El Carmen",
    "Sector Norte",
]


class Command(BaseCommand):
    help = "Crea usuarios y pedidos sintéticos para la demostración."

    def add_arguments(self, parser):
        parser.add_argument(
            "--forzar",
            action="store_true",
            help="Elimina los datos existentes antes de crear los de demostración.",
        )

    def handle(self, *args, **opciones):
        Usuario = get_user_model()

        if opciones["forzar"]:
            Pedido.objects.all().delete()
            Alerta.objects.all().delete()
            HistorialEstado.objects.all().delete()
            Entrega.objects.all().delete()
            Repartidor.objects.all().delete()
            Usuario.objects.all().delete()
        elif Pedido.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Ya existen datos. Use --forzar para regenerarlos."
                )
            )
            return

        ahora = timezone.now()

        admin = Usuario.objects.create_user(
            "admin",
            "admin@delivertrack.local",
            CLAVE_DEMO,
            first_name="Ana",
            last_name="Supervisora",
            rol=Usuario.Rol.ADMIN,
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        repartidores = []
        for username, nombre, apellido, vehiculo in [
            ("carlos", "Carlos", "Ramírez", "Motocicleta"),
            ("maria", "María", "López", "Motocicleta"),
            ("pedro", "Pedro", "Sánchez", "Panel liviano"),
        ]:
            usuario = Usuario.objects.create_user(
                username,
                f"{username}@delivertrack.local",
                CLAVE_DEMO,
                first_name=nombre,
                last_name=apellido,
                rol=Usuario.Rol.REPARTIDOR,
            )
            repartidores.append(
                Repartidor.objects.create(usuario=usuario, vehiculo=vehiculo)
            )

        def crear_pedido(hora_limite, estado):
            pedido = Pedido.objects.create(
                cliente=random.choice(CLIENTES),
                telefono=f"8888-{random.randint(1000, 9999)}",
                direccion=(
                    f"{random.choice(BARRIOS)}, "
                    f"casa {random.randint(1, 90)}"
                ),
                hora_limite=hora_limite,
                estado=estado,
            )
            # Fecha de registro retroactiva para que la serie diaria sea realista.
            Pedido.objects.filter(pk=pedido.pk).update(
                fecha_registro=hora_limite - timedelta(hours=2, minutes=30)
            )
            return pedido

        def crear_entrega(pedido, repartidor, estado, salida=None, entrega_hora=None):
            entrega = Entrega.objects.create(
                pedido=pedido,
                repartidor=repartidor,
                estado=estado,
                hora_salida=salida,
                hora_entrega=entrega_hora,
            )
            if salida:
                Entrega.objects.filter(pk=entrega.pk).update(
                    hora_asignacion=salida - timedelta(minutes=15)
                )
            return entrega

        # --- Entregas históricas (6 días anteriores) --------------------
        cerradas = 0
        for dias_atras in range(6, 0, -1):
            dia = ahora - timedelta(days=dias_atras)
            for _ in range(random.randint(4, 6)):
                hora_limite = dia.replace(
                    hour=random.randint(9, 17),
                    minute=random.choice([0, 15, 30, 45]),
                    second=0,
                    microsecond=0,
                )
                pedido = crear_pedido(hora_limite, Pedido.Estado.ENTREGADO)
                repartidor = random.choice(repartidores)
                salida = hora_limite - timedelta(
                    minutes=random.randint(30, 120)
                )
                llega_tarde = random.random() < 0.25  # ~25 % con retraso
                if llega_tarde:
                    hora_entrega = hora_limite + timedelta(
                        minutes=random.randint(5, 45)
                    )
                else:
                    hora_entrega = hora_limite - timedelta(
                        minutes=random.randint(0, 35)
                    )
                crear_entrega(
                    pedido,
                    repartidor,
                    Entrega.Estado.ENTREGADO,
                    salida=salida,
                    entrega_hora=hora_entrega,
                )
                cerradas += 1
                if random.random() < 0.15:
                    Incidencia.objects.create(
                        entrega=Entrega.objects.get(pedido=pedido),
                        tipo=random.choice(Incidencia.Tipo.values),
                        descripcion="Problema registrado durante la ruta (dato sintético).",
                        resuelta=True,
                        fecha_resolucion=hora_entrega - timedelta(minutes=5),
                    )

        # --- Entregas "en vivo" para la demostración ---------------------
        crear_pedido(ahora + timedelta(hours=3), Pedido.Estado.RECIBIDO)
        crear_pedido(ahora + timedelta(hours=4), Pedido.Estado.RECIBIDO)
        crear_pedido(
            ahora + timedelta(hours=2, minutes=30), Pedido.Estado.PREPARANDO
        )

        # Asignada a Carlos, límite en 50 minutos (NORMAL).
        pedido_asignado = crear_pedido(
            ahora + timedelta(minutes=50), Pedido.Estado.ASIGNADO
        )
        crear_entrega(pedido_asignado, repartidores[0], Entrega.Estado.ASIGNADO)

        # En camino con María, límite en 20 minutos → EN_RIESGO.
        pedido_riesgo = crear_pedido(
            ahora + timedelta(minutes=20), Pedido.Estado.ASIGNADO
        )
        crear_entrega(
            pedido_riesgo,
            repartidores[1],
            Entrega.Estado.EN_CAMINO,
            salida=ahora - timedelta(minutes=40),
        )

        # En camino con Pedro, límite hace 35 minutos → RETRASADA.
        pedido_tarde = crear_pedido(
            ahora - timedelta(minutes=35), Pedido.Estado.ASIGNADO
        )
        crear_entrega(
            pedido_tarde,
            repartidores[2],
            Entrega.Estado.EN_CAMINO,
            salida=ahora - timedelta(hours=1, minutes=30),
        )

        # Con incidencia (cliente ausente).
        pedido_incidencia = crear_pedido(
            ahora + timedelta(hours=1), Pedido.Estado.ASIGNADO
        )
        entrega_inc = crear_entrega(
            pedido_incidencia,
            repartidores[1],
            Entrega.Estado.INCIDENCIA,
            salida=ahora - timedelta(minutes=25),
        )
        Incidencia.objects.create(
            entrega=entrega_inc,
            tipo=Incidencia.Tipo.CLIENTE_AUSENTE,
            descripcion="El cliente no se encontraba en el domicilio; se dejó aviso (dato sintético).",
        )

        # Dispara la automatización para que las alertas existan ya.
        evaluar_activas()

        self.stdout.write(self.style.SUCCESS("Datos de demostración creados:"))
        self.stdout.write(f"  · Entregas históricas cerradas: {cerradas}")
        self.stdout.write(
            "  · Usuarios: admin, carlos, maria, pedro — "
            f"contraseña de demo: {CLAVE_DEMO} (cámbiela en un entorno real)"
        )
        self.stdout.write(
            "  · Incluye 1 entrega EN RIESGO y 1 RETRASADA para mostrar la automatización."
        )
