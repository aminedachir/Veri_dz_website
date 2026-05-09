from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class Publication(models.Model):
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pub_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    # ─── Cloudinary Fields ────────────────────────────────────────────────────
    image = CloudinaryField(
        'image',
        folder='publications/images/',
        blank=True,
        null=True,
        resource_type='image',
    )
    video = CloudinaryField(
        'video',
        folder='publications/videos/',
        blank=True,
        null=True,
        resource_type='video',
    )
    thumbnail = CloudinaryField(
        'thumbnail',
        folder='publications/thumbnails/',
        blank=True,
        null=True,
        resource_type='image',
    )

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

    def get_image_url(self):
        """Returns the Cloudinary URL for the image."""
        if self.image:
            return self.image.url
        return None

    def get_video_url(self):
        """Returns the Cloudinary URL for the video."""
        if self.video:
            return self.video.url
        return None

    def get_thumbnail_url(self):
        """Returns the Cloudinary URL for the thumbnail."""
        if self.thumbnail:
            return self.thumbnail.url
        return None