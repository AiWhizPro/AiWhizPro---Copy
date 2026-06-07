from django import forms

class BlogToLinkedInForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label='Blog title',
        widget=forms.TextInput(attrs={'placeholder': 'Optional blog title or headline'})
    )
    text = forms.CharField(
        required=False,
        label='Paste blog content',
        widget=forms.Textarea(attrs={
            'placeholder': 'Paste blog content here',
            'rows': 10,
            'class': 'border rounded-lg p-3 w-full'
        })
    )
    url = forms.URLField(
        required=False,
        label='Blog URL',
        widget=forms.URLInput(attrs={'placeholder': 'Optional: paste a link to the blog'})
    )
    upload = forms.FileField(
        required=False,
        label='Upload file',
        help_text='Supported: .txt, .md, .docx',
    )

    def clean(self):
        cleaned = super().clean()
        text = cleaned.get('text')
        upload = cleaned.get('upload')
        url = cleaned.get('url')

        if not text and not upload and not url:
            raise forms.ValidationError('Please paste content, upload a supported file, or provide a blog URL.')

        if upload:
            allowed = ('.txt', '.md', '.markdown', '.docx')
            filename = upload.name.lower()
            if not filename.endswith(allowed):
                raise forms.ValidationError('Unsupported file type. Use .txt, .md, .markdown, or .docx.')

        # Enforce maximum pasted content length (words) when user pastes text
        if text:
            words = len(text.split())
            if words > 1200:
                raise forms.ValidationError('Pasted content is too long. Maximum allowed is 1200 words.')

        return cleaned
