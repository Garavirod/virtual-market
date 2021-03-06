from django.db import models
from django.conf import settings

# Managers
from .managers import ProductManager


#
from model_utils.models import TimeStampedModel

"""
    To create a backup no matter SGBD
    python manage.py dumpdata > name_cpy.json
    this creates a python dictinary with data


    If you want to use the data previusly created or backed up
    paste the data.json in the sema level where is manage.py file,
    then type:

    python manage loaddata data_file_name.json

"""


class Colors(models.Model):
    """ Representa color de un producto """

    color = models.CharField(
        'Tag', 
        max_length=120, 
        unique=True
    )
    #

    class Meta:
        verbose_name = 'Color Producto'
        verbose_name_plural = 'Colores'

    def __str__(self):
        return str(self.id) + ' - ' + str(self.color)


class Product(TimeStampedModel):
    """Modelo que representa a un producto de tienda"""

    name = models.CharField(
        'Nombre', 
        max_length=100
    )
    description = models.TextField(
        'Descripcion producto',
        blank=True
    )
    man = models.BooleanField(
        'Para Hombre', 
        default=True
    ) # es solo para mujer 
    woman = models.BooleanField(
        'Para Mujer', 
        default=True
    ) # es para varon
    weight = models.DecimalField(
        'Peso', 
        max_digits=5, 
        decimal_places=2, 
        default=1
    )
    price_purchase = models.DecimalField(
        'Precio de Compra',
        max_digits=10,
        decimal_places=3
    )
    price_sale = models.DecimalField(
        'Precio de Venta',
        max_digits=10,
        decimal_places=2
    )
    main_image = models.ImageField(
        'imagen principal',
        upload_to='producto',
    ) # imagen principal del producto
    image1 = models.ImageField('Imagen 1', blank=True, null=True, upload_to='producto')
    image2 = models.ImageField('Imagen 2', blank=True, null=True, upload_to='producto')
    image3 = models.ImageField('Imagen 3', blank=True, null=True, upload_to='producto')
    image4 = models.ImageField('Imagen 4', blank=True, null=True, upload_to='producto')
    colors = models.ManyToManyField(Colors)
    video = models.URLField('unboxin', blank=True, null=True)
    stok = models.PositiveIntegerField('Stok', default=0)
    num_sales = models.PositiveIntegerField('Veces vendido', default=0)
    user_created = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prod_created",
    )


    # Conetcting the manager
    objects = ProductManager()

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return str(self.id) + ' ' + str(self.name)