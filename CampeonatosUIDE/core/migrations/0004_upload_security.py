from django.db import migrations, models
import core.validators


class Migration(migrations.Migration):
    dependencies = [("core", "0003_alter_pago_options_and_more")]

    operations = [
        migrations.AlterField(model_name="codigoqr", name="imagen_qr", field=models.ImageField(upload_to="codigos_qr/", validators=[core.validators.validate_upload_size], verbose_name="Imagen del QR")),
        migrations.AlterField(model_name="campeonato", name="reglamento", field=models.FileField(blank=True, null=True, upload_to="reglamentos/", validators=[core.validators.validate_pdf_upload])),
        migrations.AlterField(model_name="equipo", name="logo", field=models.ImageField(blank=True, null=True, upload_to="logos_equipos/", validators=[core.validators.validate_upload_size])),
        migrations.AlterField(model_name="pago", name="comprobante_pago", field=models.ImageField(blank=True, null=True, upload_to="comprobantes/", validators=[core.validators.validate_upload_size])),
        migrations.AlterField(model_name="imagengaleria", name="imagen", field=models.ImageField(upload_to="galeria/", validators=[core.validators.validate_upload_size])),
        migrations.AlterField(model_name="noticia", name="imagen", field=models.ImageField(blank=True, null=True, upload_to="noticias/", validators=[core.validators.validate_upload_size])),
        migrations.AlterField(model_name="testimonio", name="foto", field=models.ImageField(blank=True, null=True, upload_to="testimonios/", validators=[core.validators.validate_upload_size])),
    ]
