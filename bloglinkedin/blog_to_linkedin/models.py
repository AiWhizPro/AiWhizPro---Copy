from django.db import models


class LinkedInConversion(models.Model):
    title = models.CharField(max_length=255, blank=True)
    original_text = models.TextField(blank=True)
    generated_post = models.TextField(blank=True)
    source_file = models.FileField(upload_to='uploads/', blank=True, null=True)
    source_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f'Conversion {self.pk}'


class RelatedLink(models.Model):
    TOOL = 'tool'
    BLOG = 'blog'
    LINK_TYPES = [
        (TOOL, 'Tool'),
        (BLOG, 'Blog'),
    ]

    link_type = models.CharField(max_length=10, choices=LINK_TYPES, default=TOOL)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return f'{self.get_link_type_display()}: {self.title}'


class FeatureItem(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class HowItWorksStep(models.Model):
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=150)
    description = models.TextField()

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f'Step {self.step_number}: {self.title}'


class FaqItem(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question
