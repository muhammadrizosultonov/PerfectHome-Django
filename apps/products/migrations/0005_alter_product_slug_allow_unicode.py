from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_alter_product_slug_alter_producttag_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="slug",
            field=models.SlugField(allow_unicode=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="producttag",
            name="slug",
            field=models.SlugField(allow_unicode=True, max_length=120, unique=True),
        ),
    ]
