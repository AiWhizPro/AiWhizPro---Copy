import sys
import os
from io import BytesIO

# Ensure project package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Configure Django settings so forms and other parts work outside manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloglinkedin.settings')
try:
    import django
    django.setup()
except Exception:
    # If Django isn't configured (very minimal environment), tests that require settings will fail earlier.
    pass

from blog_to_linkedin import utils
from blog_to_linkedin.forms import BlogToLinkedInForm


def test_generate_basic():
    title = '10 lessons from building a creator business'
    content = (
        "I spent 6 months learning this lesson.\n"
        "Lesson one: focus on audience.\n"
        "Lesson two: ship often.\n"
        "Lesson three: learn from feedback.\n"
        "Conclusion: keep iterating."
    )
    post = utils.generate_linkedin_post(title, content)
    assert post, 'No output generated'
    assert len(post.split()) <= 280, 'Output exceeds MAX_WORDS limit'
    assert any(line.strip().startswith('•') for line in post.splitlines()), 'No bullet points found'
    assert '?' in post or 'What' in post or 'How' in post, 'CTA seems missing'
    print('test_generate_basic: PASS')


def test_dedupe():
    title = ''
    repeated = 'Key lesson repeated. ' * 3
    content = f"Introduction. {repeated} More details. {repeated} End."
    post = utils.generate_linkedin_post(title, content)
    # Count normalized occurrences of the repeated phrase
    normalized = 'key lesson repeated'
    count = post.lower().count(normalized)
    assert count == 1, f'Duplicate content detected ({count} occurrences)'
    print('test_dedupe: PASS')


def test_parse_txt():
    sample = b"Hello world\nThis is a sample blog text."
    fake = BytesIO(sample)
    fake.name = 'sample.txt'
    result = utils.parse_uploaded_file(fake)
    assert 'Hello world' in result, 'parse_uploaded_file failed to read .txt content'
    print('test_parse_txt: PASS')


def test_form_word_limit():
    long_text = 'word ' * 1201
    form = BlogToLinkedInForm({'text': long_text})
    valid = form.is_valid()
    assert not valid, 'Form should be invalid for >1200 words'
    errors = form.non_field_errors() or form.errors.get('__all__')
    # Expect the limit message somewhere in the errors
    joined = ' '.join([str(e) for e in errors])
    assert 'Maximum allowed is 1200 words' in joined or 'too long' in joined, 'Form error message missing or unexpected'
    print('test_form_word_limit: PASS')


def run_all():
    tests = [
        test_generate_basic,
        test_dedupe,
        test_parse_txt,
        test_form_word_limit,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed += 1
            print(f"{t.__name__}: FAIL — {e}")
        except Exception as e:
            failed += 1
            print(f"{t.__name__}: ERROR — {e}")
    if failed:
        print(f"\n{failed} tests failed")
        sys.exit(2)
    print('\nAll tests passed')


if __name__ == '__main__':
    run_all()
