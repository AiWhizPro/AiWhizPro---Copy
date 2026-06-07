from django.contrib import admin

from .models import FeatureItem, FaqItem, HowItWorksStep, LinkedInConversion, RelatedLink


@admin.register(LinkedInConversion)
class LinkedInConversionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'source_file', 'source_url')
    readonly_fields = ('created_at',)
    search_fields = ('title', 'original_text', 'generated_post')


@admin.register(RelatedLink)
class RelatedLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'link_type', 'url', 'order')
    list_filter = ('link_type',)
    ordering = ('link_type', 'order')


@admin.register(FeatureItem)
class FeatureItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'order')
    ordering = ('order',)


@admin.register(HowItWorksStep)
class HowItWorksStepAdmin(admin.ModelAdmin):
    list_display = ('step_number', 'title')
    ordering = ('step_number',)


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'order')
    ordering = ('order',)
