from django.db import migrations, models
from django.db.models import deletion  # Updated import

class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CarMake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'carmake',
            },
        ),
        migrations.CreateModel(
            name='CarModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('Sedan', 'Sedan'), ('SUV', 'SUV'), ('WAGON', 'WAGON')], max_length=20)),
                ('year', models.IntegerField(choices=[(year, str(year)) for year in range(2015, 2024)], default=2015)),  # Updated choices
                ('make', models.ForeignKey(on_delete=deletion.CASCADE, to='your_app_name_here.CarMake')),  # Updated ForeignKey
            ],
            options={
                'db_table': 'carmodel',
            },
        ),
    ]
