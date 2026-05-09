from django.db import models
from django.conf import settings


class FactCheckResult(models.Model):
    VERDICT_CHOICES = [
        ('trusted',     'موثوق جداً'),
        ('no_evidence', 'لا يوجد أدلة كافية'),
        ('uncertain',   'غير مؤكد'),
        ('conflicting', 'مصادر متعارضة'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='fact_checks'
    )
    input_text = models.TextField()
    input_url = models.URLField(blank=True)
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES)
    confidence_score = models.FloatField(default=0.0)  # 0.0 - 1.0
    explanation = models.TextField()
    key_claims = models.TextField(blank=True)
    red_flags = models.TextField(blank=True)
    sources_suggested = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def confidence_pct(self):
        return int(self.confidence_score * 100)

    def verdict_label(self):
        return dict(self.VERDICT_CHOICES).get(self.verdict, self.verdict)

    def __str__(self):
        return f"[{self.verdict}] {self.input_text[:60]}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'نتيجة تحقق'
        verbose_name_plural = 'نتائج التحقق'