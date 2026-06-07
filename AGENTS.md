# AiWhizPro Agent Guidelines

> Guide for AI coding agents to be immediately productive in this codebase.

## Quick Start Commands

| Task | Command | Location |
|------|---------|----------|
| **Run dev server** | `cd bloglinkedin && python manage.py runserver` | http://localhost:8000 |
| **Run tests** | `..\venv\Scripts\python.exe manage.py test` | From `bloglinkedin/` |
| **Run integration tests** | `..\venv\Scripts\python.exe scripts/test_application.py` | Manual assertions, good for debugging |
| **Admin interface** | http://localhost:8000/admin/ | Create superuser with `manage.py createsuperuser` |
| **DB migrations** | `python manage.py migrate` | Auto-created, rarely manual edits needed |

## Project Structure

```
bloglinkedin/                    # Django project root
├── blog_to_linkedin/            # Main converter app
│   ├── models.py                # 5 models: LinkedInConversion, RelatedLink, FeatureItem, HowItWorksStep, FaqItem
│   ├── views.py                 # Single home() view: GET→form, POST→convert→save
│   ├── forms.py                 # BlogToLinkedInForm: text/file/URL input
│   ├── utils.py                 # generate_linkedin_post() + parse_uploaded_file()
│   ├── admin.py                 # All 5 models registered with custom displays
│   ├── urls.py                  # Single route: "" → home (no prefix)
│   ├── migrations/              # Auto-generated, commit these
│   ├── templates/blog_to_linkedin/
│   │   ├── base.html            # Page shell + header/footer
│   │   └── home.html            # Upload form + output display (sidebar layout)
│   └── tests.py                 # 20 tests: forms, views, models, file uploads
├── bloglinkedin/                # Django config
│   ├── settings.py              # DEBUG=True, SQLite, media folder
│   ├── urls.py                  # Root routing + media serving (DEBUG only)
│   └── wsgi.py/asgi.py
├── media/uploads/               # User-uploaded files (.txt, .md, .docx)
├── scripts/                     # Standalone test utilities
│   ├── test_converter.py        # Manual conversion tests
│   └── test_application.py      # Integration tests with full output
├── frontend/                    # Separate asset layer
│   └── assets/css/tokens.css    # Design system variables (REQUIRED)
└── db.sqlite3                   # Development database

docs/                            # Project documentation (architectural decisions, rules)
└── PROJECT_RULES.md             # Key constraints and patterns
```

## Architecture: Single-View MTV Pattern

### Views (`views.py`)
- **`home()` view**: Only endpoint handling all conversion logic
  - GET: Render form + context (FAQ, HowItWorks, RelatedLinks)
  - POST: Parse input → call `generate_linkedin_post()` → save `LinkedInConversion` → re-render with output
  - Auto-populates FAQ/HowItWorks on first request (self-seeding models)

### Models (`models.py` - 5 flat models, no relationships)

1. **LinkedInConversion** (primary)
   - Fields: `title`, `original_text`, `generated_post`, `source_file`, `source_url`, `created_at`
   - Admin search: by title/text; readonly `created_at`

2. **RelatedLink** (content management)
   - Fields: `link_type` (TOOL|BLOG), `title`, `description`, `url`, `order`
   - Auto-sorted by order + title

3. **FeatureItem**, **HowItWorksStep**, **FaqItem**
   - Self-seeding: auto-created with default content on first request
   - Can be edited in admin

### Forms (`forms.py`)
- **BlogToLinkedInForm**
  - Fields: `title` (optional), `text` (≤1200 words), `url` (optional), `upload` (optional)
  - Validation: At least ONE of text/url/upload required; file extension checks; word count
  - Error on `__all__` if no content provided

### Conversion Logic (`utils.py`)

```python
def generate_linkedin_post(title: str, content: str) -> str:
    """
    Steps:
    1. Clean text: Remove code blocks, markdown, links
    2. Extract hook (context-aware, e.g., "Most creators miss...")
    3. Extract insight (first sentence of cleaned text)
    4. Extract bullets (3-4 key points; min 6 words each)
    5. Add perspective + CTA + hashtags
    6. Deduplicate sentences (normalized comparison)
    7. Enforce 280-word limit (MAX_WORDS constant)
    
    Returns: LinkedIn-ready post (string)
    """
```

**Key utilities:**
- `parse_uploaded_file()`: Handles .txt, .md, .docx (python-docx)
- `_extract_bullets()`: Identifies key points from text
- `_dedupe_items()`: Removes duplicate lines (case-insensitive)
- `_make_hook()`, `_make_cta()`: Dynamic content generation

## Development Patterns

### Adding a Feature

1. **Extend the model** (if needed)
   ```python
   # models.py
   class LinkedInConversion(models.Model):
       new_field = models.CharField(max_length=255)  # Add field
   ```

2. **Create migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Register in admin** (if applicable)
   ```python
   # admin.py
   fieldsets = (
       ("Content", {"fields": ("title", "generated_post", "new_field")}),
   )
   ```

4. **Update form + view**
   ```python
   # forms.py: add form field
   # views.py: process the new field
   # templates: render the new field
   ```

5. **Test**
   ```bash
   python manage.py test blog_to_linkedin.tests.<YourTestClass>
   ```

### Modifying Conversion Logic

1. Edit `utils.py` (focus on `generate_linkedin_post()` or `_extract_bullets()`)
2. Update constants if needed (e.g., `MAX_WORDS = 280`)
3. Run tests: `python manage.py test ConversionLogicTest`
4. Manual test via `scripts/test_application.py`

### Debugging

1. **Form validation issues**: Check `clean()` method in `forms.py`
2. **Conversion quality**: Debug `_extract_bullets()` and `_dedupe_items()` logic
3. **Database issues**: Check migrations + run `python manage.py migrate`
4. **Template rendering**: Check `home.html` + context variables from view

## Design System Rules (CRITICAL)

**Never hardcode:**
- Colors (use `--primary`, `--secondary`, etc. from `tokens.css`)
- Border radius (use `--radius-sm`, `--radius-md`, `--radius-lg`)
- Shadows (use `--shadow-card`, `--shadow-lg`)
- Typography (use `--font-primary`, `--font-secondary`)

**Always use:** Design tokens from `frontend/assets/css/tokens.css`

**Templates:** Tailwind utility classes only (no inline colors).

See [.claude/CLAUDE.md](.claude/CLAUDE.md) for full design constraints.

## Testing

### Django Test Suite (20 tests)
```bash
python manage.py test
```

**Test classes:**
- `ConversionFormTest` (6 tests): Form validation, word limits, file types
- `ConversionLogicTest` (3 tests): Text processing, bullet extraction
- `HomeViewTest` (7 tests): View rendering, form submission, conversion records
- `LinkedInConversionModelTest` (3 tests): CRUD, timestamps, string repr
- `FileUploadTest` (2 tests): .txt and .md file processing

### Integration Tests
```bash
python scripts/test_application.py
```

Standalone script with visual output; tests forms, conversion, database, file uploads.

## Key Constants & Limits

```python
MAX_WORDS = 280              # LinkedIn post max length
MAX_PASTED_TEXT = 1200       # Pasted content limit
BULLET_COUNT = 3-4           # Extracted bullet points
SUPPORTED_FORMATS = ['.txt', '.md', '.markdown', '.docx']
DEFAULT_HASHTAGS = ['#LinkedIn', '#ContentStrategy', '#CreatorEconomy']
```

## Important Caveats

- **No production setup**: SQLite only, no Docker/Gunicorn; needs PostgreSQL + env vars for production
- **Single view**: All logic in `home()` view; consider splitting if feature set grows
- **Design tokens**: See `tokens.css`; hardcoded styles will be flagged
- **Auto-seeding**: Models create default content on first access (check `admin.py` for logic)
- **DEBUG mode**: Static files + media served by Django; use whitenoise + CDN in production

## Related Documentation

- [docs/PROJECT_RULES.md](docs/PROJECT_RULES.md) — Architectural constraints
- [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) — Design tokens and UI patterns
- [.claude/CLAUDE.md](.claude/CLAUDE.md) — Design system constraints (color, radius, shadows, typography)
- [bloglinkedin/plan.md](bloglinkedin/plan.md) — Conversion algorithm details

## Next Steps for Agents

When starting work:
1. Run `python manage.py test` to ensure environment is set up
2. Check `docs/PROJECT_RULES.md` for architectural constraints
3. Reference `tokens.css` when modifying templates
4. Use `scripts/test_application.py` for quick conversion tests
5. Commit migrations alongside model changes

---

**Last updated**: June 7, 2026 | Django 6.0.6 | Python 3.x | SQLite (dev)
