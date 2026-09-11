import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0004_upload_security")]
    operations = [migrations.AlterField(
        model_name="usuario", name="cedula",
        field=models.CharField(blank=True, max_length=10, null=True, unique=True,
                               validators=[core.validators.validate_ecuadorian_cedula]),
    )]
