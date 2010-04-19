from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


PASTA_PRICE_INCLUDES_TAX = True # Are prices shown with tax included or not?


class TaxClass(models.Model):
    name = models.CharField(_('name'), max_length=100)
    rate = models.DecimalField(_('rate'), max_digits=10, decimal_places=2)
    priority = models.PositiveIntegerField(_('priority'), default=0,
        help_text = _('Used to order the tax classes in the administration interface.'))

    class Meta:
        ordering = ['-priority']
        verbose_name = _('tax class')
        verbose_name_plural = _('tax classes')


class Product(models.Model):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        pass

    def __unicode__(self):
        return self.name

    def get_price(self):
        return self.prices.latest()

    @property
    def unit_price(self):
        return self.prices.latest().unit_price


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('product'),
        related_name='prices')
    created = models.DateTimeField(_('created'), default=datetime.now)
    tax_class = models.ForeignKey(TaxClass, verbose_name=_('tax class'),
        default=lambda: TaxClass.objects.all()[0])

    _unit_price = models.DecimalField(_('unit price'), max_digits=18, decimal_places=10)
    tax_included = models.BooleanField(_('tax included'),
        help_text=_('Is tax included in given unit price?'),
        default=PASTA_PRICE_INCLUDES_TAX)
    currency = models.CharField(_('currency'), max_length=10)

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']
        verbose_name = _('product price')
        verbose_name_plural = _('product prices')

    @property
    def unit_price_incl_tax(self):
        if self.tax_included:
            return self._unit_price
        return self._unit_price * (1+self.tax_class.rate/100)

    @property
    def unit_price_excl_tax(self):
        if not self.tax_included:
            return self._unit_price
        return self._unit_price / (1+self.tax_class.rate/100)

    if PASTA_PRICE_INCLUDES_TAX:
        @property
        def unit_price(self):
            return self.unit_price_incl_tax
    else:
        @property
        def unit_price(self):
            return self.unit_price_excl_tax


class ProductImage(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('product'),
        related_name='images')
    image = models.ImageField(_('image'),
        upload_to=lambda instance, filename: '%s/%s' % (instance.product.slug, filename))
    ordering = models.PositiveIntegerField(_('ordering'), default=0)

    class Meta:
        ordering = ['ordering']
        verbose_name = _('product image')
        verbose_name_plural = _('product images')

