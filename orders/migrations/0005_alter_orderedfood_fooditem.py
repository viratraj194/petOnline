# Generated by Django 4.1.3 on 2023-03-03 07:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_fooditem_image_2_fooditem_image_3_fooditem_image_4_and_more'),
        ('orders', '0004_alter_orderedfood_fooditem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedfood',
            name='fooditem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.fooditem'),
        ),
    ]
