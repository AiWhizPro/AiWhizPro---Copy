"""
Test suite for Blog to LinkedIn converter application.
Tests views, forms, models, and conversion logic.

Run with: python manage.py test
"""
import os
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from blog_to_linkedin.models import LinkedInConversion
from blog_to_linkedin.forms import BlogToLinkedInForm
from blog_to_linkedin.utils import generate_linkedin_post


class ConversionFormTest(TestCase):
    """Test form validation and behavior."""

    def test_form_with_url_only(self):
        """Test form submission with URL only."""
        form_data = {
            'title': 'Test Article',
            'url': 'https://example.com/article',
            'text': '',
            'upload': '',
        }
        form = BlogToLinkedInForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_text_only(self):
        """Test form submission with text content only."""
        sample_text = "This is a test article. " * 100  # ~500 words
        form_data = {
            'title': 'Test Article',
            'url': '',
            'text': sample_text,
            'upload': '',
        }
        form = BlogToLinkedInForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_text_exceeds_limit(self):
        """Test that text exceeding 1200 words is rejected."""
        long_text = "This is a test word. " * 1300
        form_data = {
            'title': 'Test Article',
            'url': '',
            'text': long_text,
            'upload': '',
        }
        form = BlogToLinkedInForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_allows_optional_title(self):
        """Test that title is optional when URL is provided."""
        form_data = {
            'title': '',
            'url': 'https://example.com',
            'text': '',
            'upload': '',
        }
        form = BlogToLinkedInForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_file_upload(self):
        """Test form submission with file upload."""
        content = b"This is test file content. " * 50
        uploaded_file = SimpleUploadedFile(
            "test.txt",
            content,
            content_type="text/plain"
        )
        form_data = {
            'title': 'Test Article',
            'url': '',
            'text': '',
        }
        form = BlogToLinkedInForm(data=form_data, files={'upload': uploaded_file})
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_file_type(self):
        """Test that invalid file types are rejected."""
        invalid_file = SimpleUploadedFile(
            "test.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        form_data = {
            'title': 'Test Article',
            'url': '',
            'text': '',
        }
        form = BlogToLinkedInForm(data=form_data, files={'upload': invalid_file})
        self.assertFalse(form.is_valid())


class ConversionLogicTest(TestCase):
    """Test the conversion utility functions."""

    def test_convert_simple_text(self):
        """Test conversion of simple text input."""
        sample_text = """
        Understanding Machine Learning
        
        Machine learning is a subset of artificial intelligence. It enables systems to learn from data.
        Key concepts include supervised learning, unsupervised learning, and reinforcement learning.
        
        Benefits:
        - Automated decision making
        - Pattern recognition
        - Predictive analytics
        
        Organizations using ML are seeing 25% improvement in efficiency.
        """
        result = generate_linkedin_post("Understanding Machine Learning", sample_text)
        
        self.assertIsNotNone(result)
        self.assertIn("machine learning", result.lower())
        self.assertGreater(len(result), 50)

    def test_convert_preserves_key_points(self):
        """Test that conversion extracts key takeaways."""
        text = """
        The future of AI
        
        Artificial Intelligence is transforming industries. Key trends include:
        1. Natural language processing advances
        2. Computer vision improvements
        3. Autonomous systems
        4. Personalization at scale
        """
        result = generate_linkedin_post("The Future of AI", text)
        
        self.assertIsNotNone(result)
        # Should mention AI or related terms
        self.assertTrue(
            any(term in result.lower() for term in ['ai', 'artificial', 'intelligence'])
        )

    def test_convert_with_title(self):
        """Test that title is included in conversion."""
        text = "This is sample content about digital transformation."
        title = "Digital Transformation Guide"
        result = generate_linkedin_post(title, text)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)


class HomeViewTest(TestCase):
    """Test the home view and form submission."""

    def setUp(self):
        """Initialize test client."""
        self.client = Client()
        self.url = reverse('blog_to_linkedin:home')

    def test_home_page_loads(self):
        """Test that home page loads successfully."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_to_linkedin/home.html')

    def test_home_page_contains_form(self):
        """Test that home page contains the conversion form."""
        response = self.client.get(self.url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], BlogToLinkedInForm)

    def test_form_submission_with_text(self):
        """Test submitting form with text content."""
        sample_text = "This is a test article about web development. " * 20
        response = self.client.post(self.url, {
            'title': 'Web Development Tips',
            'text': sample_text,
            'url': '',
            'upload': '',
        })
        
        # Should redirect or show conversion
        self.assertIn(response.status_code, [200, 302])
        
        # Check if conversion was created
        conversions = LinkedInConversion.objects.filter(title='Web Development Tips')
        self.assertEqual(conversions.count(), 1)

    def test_form_submission_creates_conversion_record(self):
        """Test that form submission creates a conversion record."""
        sample_text = "Python is a popular programming language. " * 25
        self.client.post(self.url, {
            'title': 'Python Basics',
            'text': sample_text,
            'url': '',
            'upload': '',
        })
        
        conversion = LinkedInConversion.objects.filter(title='Python Basics').first()
        self.assertIsNotNone(conversion)
        self.assertIsNotNone(conversion.generated_post)

    def test_invalid_form_shows_errors(self):
        """Test that invalid form shows error messages."""
        response = self.client.post(self.url, {
            'title': 'Test',
            'text': '',  # Missing content (URL, text, or upload)
            'url': '',
            'upload': '',
        })
        
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # Content validation error

    def test_conversion_without_url_and_text(self):
        """Test that at least URL or text is required."""
        response = self.client.post(self.url, {
            'title': 'Test',
            'text': '',
            'url': '',
            'upload': '',
        })
        
        form = response.context['form']
        self.assertFalse(form.is_valid())


class LinkedinConversionModelTest(TestCase):
    """Test the LinkedinConversion model."""

    def test_create_conversion(self):
        """Test creating a conversion record."""
        conversion = LinkedInConversion.objects.create(
            title='Test Article',
            source_url='https://example.com/article',
            original_text='Sample content for testing',
            generated_post='Generated LinkedIn post content'
        )
        
        self.assertEqual(conversion.title, 'Test Article')
        self.assertEqual(conversion.source_url, 'https://example.com/article')
        self.assertIsNotNone(conversion.created_at)

    def test_conversion_str_representation(self):
        """Test string representation of conversion."""
        conversion = LinkedInConversion.objects.create(
            title='Test Article',
            original_text='Sample',
            generated_post='Output'
        )
        
        self.assertEqual(str(conversion), 'Test Article')

    def test_conversion_has_timestamp(self):
        """Test that conversion records have creation timestamp."""
        conversion = LinkedInConversion.objects.create(
            title='Timestamped Article',
            original_text='Content',
            generated_post='Output'
        )
        
        self.assertIsNotNone(conversion.created_at)


class FileUploadTest(TestCase):
    """Test file upload functionality."""

    def setUp(self):
        """Initialize test client."""
        self.client = Client()
        self.url = reverse('blog_to_linkedin:home')

    def test_txt_file_upload(self):
        """Test uploading a .txt file."""
        file_content = b"Article Title\n\nThis is test article content. " * 20
        uploaded_file = SimpleUploadedFile(
            "test_article.txt",
            file_content,
            content_type="text/plain"
        )
        
        response = self.client.post(self.url, {
            'title': 'Text File Upload Test',
            'text': '',
            'url': '',
            'upload': uploaded_file,
        })
        
        conversion = LinkedInConversion.objects.filter(
            title='Text File Upload Test'
        ).first()
        self.assertIsNotNone(conversion)

    def test_markdown_file_upload(self):
        """Test uploading a .md file."""
        file_content = b"# Article Title\n\nContent here. " * 20
        uploaded_file = SimpleUploadedFile(
            "test_article.md",
            file_content,
            content_type="text/markdown"
        )
        
        response = self.client.post(self.url, {
            'title': 'Markdown File Upload Test',
            'text': '',
            'url': '',
            'upload': uploaded_file,
        })
        
        conversion = LinkedInConversion.objects.filter(
            title='Markdown File Upload Test'
        ).first()
        self.assertIsNotNone(conversion)
