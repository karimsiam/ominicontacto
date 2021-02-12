# Generated by Django 2.2.7 on 2021-01-20 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0072_queue_audio_previo_conexion_llamada'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracionDeAgentesDeCampana',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                 verbose_name='ID')),
                ('set_auto_attend_inbound', models.BooleanField(default=False,
                 verbose_name='Configurar auto atender entrantes')),
                ('auto_attend_inbound', models.BooleanField(default=False,
                 verbose_name='Auto atender entrantes')),
                ('set_auto_attend_dialer', models.BooleanField(default=False,
                 verbose_name='Configurar auto atender dialer')),
                ('auto_attend_dialer', models.BooleanField(default=False,
                 verbose_name='Auto atender dialer')),
                ('set_auto_unpause', models.BooleanField(default=False,
                 verbose_name='Configurar despausar automaticamente')),
                ('auto_unpause', models.PositiveIntegerField(default=0,
                 verbose_name='Despausar automaticamente')),
                ('set_obligar_calificacion', models.BooleanField(default=False,
                 verbose_name='Configurar forzar calificación')),
                ('obligar_calificacion', models.BooleanField(default=False,
                 verbose_name='Forzar calificación')),
                ('campana', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                 related_name='configuracion_de_agentes', to='ominicontacto_app.Campana')),
            ],
        ),
    ]
