from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

	dependencies = [
		('main', '0005_add_fecha_termino'),
	]


	operations = [
		migrations.CreateModel(
			name='Detalles_pedidos',
			fields=[
				('id_detalle', models.AutoField(primary_key=True, serialize=False)),
				('cantidad', models.PositiveIntegerField(default=1)),
				('subtotal', models.DecimalField(max_digits=10, decimal_places=2)),
				('email_usuario', models.EmailField(blank=True, null=True, max_length=254)),
				('pedido', models.ForeignKey(to='main.Pedidos', on_delete=django.db.models.deletion.CASCADE, related_name='detalles')),
				('producto', models.ForeignKey(to='main.Producto', on_delete=django.db.models.deletion.CASCADE)),
			],
		),
	]
