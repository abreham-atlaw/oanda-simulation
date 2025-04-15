# Generated by Django 5.0.3 on 2025-04-15 11:27

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('balance', models.FloatField()),
                ('alias', models.CharField(max_length=255)),
                ('currency', models.CharField(default='USD', max_length=255)),
                ('margin_rate', models.FloatField()),
                ('time_delta', models.IntegerField(default=0)),
                ('delta_multiplier', models.FloatField(default=1)),
            ],
        ),
    ]
