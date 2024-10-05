from django.contrib.auth.models import User
from django.db import models

from users.models import Profile


class Forecast(models.Model):
    objects = models.Manager()
    file_name = models.CharField(max_length=100)
    excel = models.FileField(null=True, blank=True, upload_to='excel', max_length=100)
    image = models.ImageField(null=True, blank=True, upload_to='graphs')
    pdf = models.FileField(null=True, blank=True, upload_to='reports', max_length=100)

    def __str__(self):
        return self.file_name


class Saved(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    forecast = models.ForeignKey(to=Forecast, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)

    class Meta:
        unique_together = ('user', 'forecast')
