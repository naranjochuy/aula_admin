from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension

class Migration(migrations.Migration):
    dependencies = [
        ('employees', '0002_initial'),
    ]

    operations = [
        UnaccentExtension(),
    ]
