from django.db import models

class MaintenanceStatus(models.Model):
    status = models.BooleanField(default=False)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Changed to auto_now_add
    
    class Meta:
        verbose_name_plural = "Maintenance Status"
        ordering = ['-created_at']  # Newest first
    
    def __str__(self):
        return f"Maintenance: {'Active' if self.status else 'Inactive'}"