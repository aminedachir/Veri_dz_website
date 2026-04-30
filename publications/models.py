from django.db import models
from django.conf import settings


class Publication(models.Model):
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pub_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    image = models.ImageField(upload_to='publications/images/', blank=True, null=True)
    video = models.FileField(upload_to='publications/videos/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='publications/thumbnails/', blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title