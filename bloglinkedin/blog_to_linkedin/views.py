from django.shortcuts import render

from .forms import BlogToLinkedInForm
from .models import FaqItem, FeatureItem, HowItWorksStep, LinkedInConversion, RelatedLink
from .utils import generate_linkedin_post, parse_uploaded_file


def home(request):
    form = BlogToLinkedInForm(request.POST or None, request.FILES or None)
    conversion = None

    if request.method == 'POST' and form.is_valid():
        title = form.cleaned_data.get('title', '').strip()
        text = form.cleaned_data.get('text', '').strip()
        upload = form.cleaned_data.get('upload')
        url = form.cleaned_data.get('url')

        if upload:
            text = parse_uploaded_file(upload)
            if not title:
                title = upload.name.rsplit('.', 1)[0]
        elif not text and url:
            # Try to fetch the URL content (best-effort). Requires requests + bs4 for best results.
            try:
                import requests
                from bs4 import BeautifulSoup

                resp = requests.get(url, timeout=6)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # Extract main text as visible text
                    text = ' '.join(p.get_text(separator=' ', strip=True) for p in soup.find_all('p'))
                    if not title:
                        title = soup.title.string if soup.title and soup.title.string else url
            except Exception:
                # best-effort only; leave text empty if fetch fails
                text = text or ''

        generated_post = generate_linkedin_post(title=title, content=text)
        conversion = LinkedInConversion(
            title=title or 'Blog conversion',
            original_text=text,
            generated_post=generated_post,
            source_file=upload if upload else None,
            source_url=url or None,
        )
        conversion.save()

    # Seed default HowItWorks steps and FAQs when empty (first-run convenience)
    if HowItWorksStep.objects.count() == 0:
        HowItWorksStep.objects.bulk_create([
            HowItWorksStep(step_number=1, title='Read the article', description='Scan the article to identify its main insight and key lessons.'),
            HowItWorksStep(step_number=2, title='Extract 3–5 lessons', description='Pick the clearest, most actionable takeaways that professionals can apply.'),
            HowItWorksStep(step_number=3, title='Craft a hook', description='Write a 1–2 line hook that creates curiosity for the main insight.'),
            HowItWorksStep(step_number=4, title='Add CTA & hashtags', description='End with a simple CTA and 2–3 relevant hashtags to boost engagement.'),
        ])

    if FaqItem.objects.count() == 0:
        FaqItem.objects.bulk_create([
            FaqItem(question='What formats can I upload?', answer='Supported formats: .txt, .md, .docx.', order=1),
            FaqItem(question='How long should the LinkedIn post be?', answer='Aim for 150–300 words for best engagement; we keep posts concise.', order=2),
            FaqItem(question='Can I edit the generated post?', answer='Yes — copy the generated text and edit it before posting to add personal details.', order=3),
            FaqItem(question='Will this post publish to LinkedIn for me?', answer='No — this tool generates LinkedIn-ready text. Publishing must be done manually or via a connected API in the future.', order=4),
        ])

    # Prepare features with optional link if a RelatedLink matches the feature title
    features_qs = FeatureItem.objects.all()
    related = {rl.title.lower(): rl.url for rl in RelatedLink.objects.all()}
    features_for_how = []
    for f in features_qs:
        key = f.title.lower()
        features_for_how.append({
            'title': f.title,
            'description': f.description,
            'url': related.get(key)
        })

    context = {
        'form': form,
        'conversion': conversion,
        'tools': RelatedLink.objects.filter(link_type=RelatedLink.TOOL),
        'blogs': RelatedLink.objects.filter(link_type=RelatedLink.BLOG),
        'faqs': FaqItem.objects.all(),
        'features': FeatureItem.objects.all(),
        'steps': HowItWorksStep.objects.all(),
        'features_for_how': features_for_how,
    }
    return render(request, 'blog_to_linkedin/home.html', context)
