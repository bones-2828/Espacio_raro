from django.db import migrations, models


class Migration(migrations.Migration):


	dependencies = [
		('main', '0003_auto_20251116_0845'),
	]

	operations = [
		migrations.AddField(
			model_name='pedidos',
			name='fecha_entrega',
			field=models.DateField(blank=True, null=True),
		),
	]
