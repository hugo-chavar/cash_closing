"""
File:           restaurant.py
Author:         Dibyaranjan Sathua
Created on:     25/01/21, 12:58 am
"""
from django.db import models
from django.conf import settings

from api.models.base_model import BaseModel


class RestaurantType(BaseModel):
    """ Restaurant Type """
    name = models.CharField(max_length=200, unique=True)


class RestaurantTypeTranslation(BaseModel):
    """ Restaurant Type Translation """
    name = models.CharField(max_length=200)
    restaurant_type = models.ForeignKey('RestaurantType', on_delete=models.CASCADE)


class RestaurantTypeMiddle(BaseModel):
    """ All the types for a restaurant  """
    restaurant = models.ForeignKey(settings.RESTAURANT_MODEL, models.CASCADE)
    restaurant_type = models.ForeignKey(settings.RESTAURANT_TYPE_MODEL, models.CASCADE)


class RestaurantPeriod(BaseModel):
    """ Restaurant Period """
    start_time = models.TimeField()
    end_time = models.TimeField()
    restaurant = models.ForeignKey(settings.RESTAURANT_MODEL, on_delete=models.CASCADE)


class RestaurantRepeat(BaseModel):
    """ Store different repeats value """
    name = models.CharField(max_length=50, unique=True)


class RestaurantPeriodRepeat(BaseModel):
    """ Store the repeats value for each period """
    restaurant_period = models.ForeignKey(
        settings.RESTAURANT_PERIOD_MODEL, on_delete=models.CASCADE
    )
    restaurant_repeat = models.ForeignKey(
        settings.RESTAURANT_REPEAT_MODEL, on_delete=models.CASCADE
    )


class RestaurantHoliday(BaseModel):
    """ Store restaurant holidays """
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    restaurant = models.ForeignKey(settings.RESTAURANT_MODEL, models.CASCADE)


class RestaurantTranslationLanguage(BaseModel):
    """ Store restaurant translation languages """
    restaurant = models.ForeignKey(settings.RESTAURANT_MODEL, on_delete=models.CASCADE)
    language = models.ForeignKey(settings.LANGUAGE_MODEL, on_delete=models.CASCADE)


class RestaurantPayment(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    restaurant = models.ForeignKey(settings.RESTAURANT_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3)


class Restaurant(BaseModel):
    """ Restaurant """

    class VATCalculationMethod(models.TextChoices):
        """ VAT calculation methods """
        VAT_INCLUDED = "VatIncluded"
        VAT_EXCLUDED = "VatExcluded"

    class PaymentTerminal(models.TextChoices):
        """ Payment terminal """
        SUMUP = "SumUp"
        STRIPE = "Stripe"

    image_link = models.URLField(max_length=300, blank=True, default="")
    qr_image_link = models.URLField(max_length=300, blank=True, default="")
    name = models.CharField(max_length=300)
    address = models.TextField(null=True, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    facebook = models.URLField(max_length=300, blank=True, default="")
    instagram = models.URLField(max_length=300, blank=True, default="")
    trip_advisor = models.URLField(max_length=300, blank=True, default="")
    vat = models.CharField(max_length=45, blank=True, default="")
    vat_calculation = models.CharField(
        max_length=20,
        choices=VATCalculationMethod.choices,
        default=VATCalculationMethod.VAT_INCLUDED.value
    )
    currency = models.ForeignKey(
        settings.CURRENCY_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    primary_language = models.ForeignKey(
        settings.LANGUAGE_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    covid_mode = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    free_subscription = models.BooleanField(default=False)
    payment_terminal = models.CharField(
        max_length=20,
        choices=PaymentTerminal.choices,
        default=PaymentTerminal.SUMUP.value,
        null=True,
        blank=True
    )
    country = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"{self.name} [{self.id}]"
