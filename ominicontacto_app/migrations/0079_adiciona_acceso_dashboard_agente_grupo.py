# Generated by Django 2.2.7 on 2021-06-21 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ominicontacto_app', '0078_adiciona_acceso_grabaciones_agente_grupo'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupo',
            name='acceso_dashboard_agente',
            field=models.BooleanField(default=True, verbose_name='Acceso dashboard agentes'),
        ),
    ]
