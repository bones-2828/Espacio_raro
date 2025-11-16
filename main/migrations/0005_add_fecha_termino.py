from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('main', '0003_auto_20251116_1135'),
	]


	operations = [
		migrations.AddField(
			model_name='pedidos',
			name='fecha_termino',
			field=models.DateField(blank=True, null=True),
		),
	]
