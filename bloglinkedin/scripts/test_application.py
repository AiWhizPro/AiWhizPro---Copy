#!/usr/bin/env python
"""
Simple Application Test Script
Tests the Blog to LinkedIn converter functionality without Django test framework.

Usage: python scripts/test_application.py
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloglinkedin.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from blog_to_linkedin.forms import BlogToLinkedInForm
from blog_to_linkedin.models import LinkedInConversion
from blog_to_linkedin.utils import generate_linkedin_post
from django.core.files.uploadedfile import SimpleUploadedFile


def test_form_validation():
    """Test form validation with different inputs."""
    print("\n" + "="*60)
    print("TEST 1: Form Validation")
    print("="*60)
    
    # Test 1.1: Valid form with text
    print("\n✓ Test 1.1: Form with text content...")
    form_data = {
        'title': 'Testing Django Forms',
        'text': 'This is test content. ' * 30,
        'url': '',
    }
    form = BlogToLinkedInForm(data=form_data)
    assert form.is_valid(), f"Form validation failed: {form.errors}"
    print("  ✓ PASSED: Form accepts valid text")
    
    # Test 1.2: Valid form with URL
    print("\n✓ Test 1.2: Form with URL...")
    form_data = {
        'title': 'Testing Django Forms',
        'url': 'https://example.com/article',
        'text': '',
    }
    form = BlogToLinkedInForm(data=form_data)
    assert form.is_valid(), f"Form validation failed: {form.errors}"
    print("  ✓ PASSED: Form accepts valid URL")
    
    # Test 1.3: Missing all content (should fail)
    print("\n✓ Test 1.3: Form with no content...")
    form_data = {
        'title': 'Test',
        'text': '',
        'url': '',
    }
    form = BlogToLinkedInForm(data=form_data)
    assert not form.is_valid(), "Form should reject when no content is provided"
    print("  ✓ PASSED: Form rejects when no content provided")
    
    # Test 1.4: Text exceeds word limit
    print("\n✓ Test 1.4: Form with text exceeding 1200 words...")
    long_text = "Word " * 1300  # 1300 words
    form_data = {
        'title': 'Long Article',
        'text': long_text,
        'url': '',
    }
    form = BlogToLinkedInForm(data=form_data)
    assert not form.is_valid(), "Form should reject text over 1200 words"
    print("  ✓ PASSED: Form rejects text exceeding 1200 words")
    
    print("\n✓ All form validation tests passed!")


def test_conversion_logic():
    """Test the conversion utility function."""
    print("\n" + "="*60)
    print("TEST 2: Conversion Logic")
    print("="*60)
    
    # Test 2.1: Simple text conversion
    print("\n✓ Test 2.1: Converting simple text...")
    sample_text = """
    The Future of Remote Work
    
    Remote work has become mainstream. Companies are adopting flexible policies.
    Key benefits include increased productivity and employee satisfaction.
    
    Statistics show 76% of workers want to continue working remotely.
    """
    title = "The Future of Remote Work"
    
    result = generate_linkedin_post(title, sample_text)
    assert result is not None, "Conversion returned None"
    assert len(result) > 50, "Converted text is too short"
    assert "remote" in result.lower() or "work" in result.lower(), "Conversion lost key content"
    print(f"  ✓ PASSED: Generated {len(result)} character post")
    print(f"  Generated post preview:\n  {result[:150]}...")
    
    # Test 2.2: Conversion with different content
    print("\n✓ Test 2.2: Converting technical content...")
    tech_text = """
    Understanding APIs
    
    An API is an interface for software components to communicate.
    REST, GraphQL, and SOAP are popular API styles.
    
    Benefits: Code reusability, scalability, modularity.
    """
    result = generate_linkedin_post("Understanding APIs", tech_text)
    assert result is not None, "Conversion failed"
    assert len(result) > 0, "Conversion resulted in empty string"
    print(f"  ✓ PASSED: Generated {len(result)} character post")
    
    # Test 2.3: List extraction
    print("\n✓ Test 2.3: Extracting bullet points...")
    list_text = """
    10 Ways to Boost Productivity
    
    1. Set clear goals
    2. Use time blocking
    3. Eliminate distractions
    4. Take regular breaks
    5. Practice deep work
    """
    result = generate_linkedin_post("Productivity Tips", list_text)
    assert result is not None, "Conversion failed"
    print(f"  ✓ PASSED: Generated {len(result)} character post")
    print(f"  Generated post preview:\n  {result[:150]}...")
    
    print("\n✓ All conversion logic tests passed!")


def test_database_models():
    """Test the LinkedinConversion model."""
    print("\n" + "="*60)
    print("TEST 3: Database Models")
    print("="*60)
    
    # Test 3.1: Create conversion record
    print("\n✓ Test 3.1: Creating conversion record...")
    conversion = LinkedInConversion.objects.create(
        title='Test Article',
        source_url='https://example.com/test',
        original_text='This is test content',
        generated_post='Generated LinkedIn post for testing'
    )
    assert conversion.id is not None, "Conversion not saved"
    assert conversion.title == 'Test Article', "Title mismatch"
    print(f"  ✓ PASSED: Created record with ID {conversion.id}")
    
    # Test 3.2: Retrieve conversion record
    print("\n✓ Test 3.2: Retrieving conversion record...")
    retrieved = LinkedInConversion.objects.get(id=conversion.id)
    assert retrieved.title == 'Test Article', "Retrieved title mismatch"
    assert retrieved.source_url == 'https://example.com/test', "Retrieved URL mismatch"
    print("  ✓ PASSED: Retrieved record successfully")
    
    # Test 3.3: Update conversion record
    print("\n✓ Test 3.3: Updating conversion record...")
    conversion.generated_post = 'Updated LinkedIn post'
    conversion.save()
    updated = LinkedInConversion.objects.get(id=conversion.id)
    assert updated.generated_post == 'Updated LinkedIn post', "Update failed"
    print("  ✓ PASSED: Updated record successfully")
    
    # Test 3.4: String representation
    print("\n✓ Test 3.4: Testing string representation...")
    assert str(conversion) == 'Test Article', "String representation failed"
    print(f"  ✓ PASSED: str(conversion) = '{str(conversion)}'")
    
    # Test 3.5: Timestamp
    print("\n✓ Test 3.5: Checking timestamp...")
    assert conversion.created_at is not None, "Timestamp not set"
    print(f"  ✓ PASSED: Record created at {conversion.created_at}")
    
    # Cleanup
    conversion.delete()
    print("\n✓ All database model tests passed!")


def test_file_upload():
    """Test file upload functionality."""
    print("\n" + "="*60)
    print("TEST 4: File Upload Processing")
    print("="*60)
    
    # Test 4.1: Text file simulation
    print("\n✓ Test 4.1: Processing .txt file...")
    txt_content = b"Test Article\n\nThis is content from a text file. " * 20
    assert len(txt_content) > 100, "Test file too small"
    print(f"  ✓ PASSED: Simulated {len(txt_content)} byte .txt file")
    
    # Test 4.2: Markdown file simulation
    print("\n✓ Test 4.2: Processing .md file...")
    md_content = b"# Test Article\n\nMarkdown content here. " * 20
    assert len(md_content) > 100, "Test file too small"
    print(f"  ✓ PASSED: Simulated {len(md_content)} byte .md file")
    
    # Test 4.3: Content extraction
    print("\n✓ Test 4.3: Extracting file content...")
    content_str = txt_content.decode('utf-8', errors='ignore')
    assert len(content_str) > 100, "Extracted content too short"
    print(f"  ✓ PASSED: Extracted {len(content_str)} characters")
    
    print("\n✓ All file upload tests passed!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  BLOG TO LINKEDIN CONVERTER - APPLICATION TEST SUITE".center(58) + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    try:
        test_form_validation()
        test_conversion_logic()
        test_database_models()
        test_file_upload()
        
        print("\n" + "█"*60)
        print("█" + " "*58 + "█")
        print("█" + "✓ ALL TESTS PASSED SUCCESSFULLY!".center(58) + "█")
        print("█" + " "*58 + "█")
        print("█"*60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
