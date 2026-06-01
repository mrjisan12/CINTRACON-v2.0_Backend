from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='CINTRACON')
    allow_signup = models.BooleanField(default=True)
    max_file_size_mb = models.IntegerField(default=10)
    allowed_departments = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Site Settings'

    def __str__(self):
        return self.site_name
