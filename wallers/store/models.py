from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Benutzer')
    name = models.CharField(max_length=200, null=True, verbose_name='Name')
    email = models.CharField(max_length=200, null=True, verbose_name='Email')

    class Meta:
        verbose_name = 'Kunde'
        verbose_name_plural = 'Kunden'

    def __str__(self):
        return self.name
        

category_choices = (
    ('wasser', 'Wasser'), 
    ('wein', 'Wein'),
    ('bier', 'Bier'),
    ('likor', 'Likor'),
    ('softdrinks', 'Softdrinks'),
    ('energydrink', 'Energydrink'),
)

class Item(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Preis')
    category = models.CharField(max_length=200, choices=category_choices, default="wasser", verbose_name='Kategorie')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=False, verbose_name='Bild')
    uploaded_on  = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height != img.width:
            left = 5
            top = img.height / 4
            right = 164
            bottom = 3 * img.height / 4
            img.crop((left, top, right, bottom))        
            img.save(self.image.path)

    class Meta:
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkte'

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Kunde')
    delivery_date = models.DateTimeField(default=None, null=True, verbose_name='Lieferdatum')
    date_ordered = models.DateTimeField(auto_now=True, verbose_name='Bestelldatum')
    complete = models.BooleanField(max_length=200, null=True, verbose_name='Aufgegeben')
    transaction_id = models.CharField(max_length=200, null=True, verbose_name='Transaktionsnummer')
    finished = models.BooleanField(default=False, verbose_name='Abgeschlossen')
    comment = models.TextField(default=None, null=True, verbose_name='Kommentar')

    class Meta:
        verbose_name = 'Bestellung'
        verbose_name_plural = 'Bestellungen'

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def get_cart_items_list(self):
        orderitems = self.orderitem_set.all()
        return orderitems

    @property
    def get_shipping_address(self):
        address = list(self.shippingaddress_set.filter(order=self).values())[0]
        return address


class OrderItem(models.Model):
    product = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Produkt')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Bestellung')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Anzahl')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bestellprodukt'
        verbose_name_plural = 'Bestellprodukte'

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Kunde')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Bestellung')
    address = models.CharField(max_length=200, null=True, verbose_name='Adresse')
    city = models.CharField(max_length=200, null=True, verbose_name='Ortschaft')
    zipcode = models.CharField(max_length=200, null=True, verbose_name='Postleitzahl')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lieferadresse'
        verbose_name_plural = 'Lieferadressen'

    def __str__(self):
        return self.address