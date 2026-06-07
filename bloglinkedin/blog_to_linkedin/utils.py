import re
from pathlib import Path
from docx import Document

MAX_WORDS = 280


def parse_uploaded_file(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith('.docx'):
        return _read_docx(uploaded_file)
    text = uploaded_file.read().decode('utf-8', errors='ignore')
    return text


def _read_docx(uploaded_file):
    document = Document(uploaded_file)
    return '\n'.join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())


def _clean_text(text):
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)
    text = re.sub(r'[>#*`]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [part.strip() for part in parts if part.strip()]


def _dedupe_items(items):
    seen = set()
    out = []
    for it in items:
        key = re.sub(r'[^a-z0-9 ]', '', it.lower()).strip()
        if key and key not in seen:
            seen.add(key)
            out.append(it)
    return out


def _collapse_duplicate_sentences(text):
    """Remove duplicate sentences across the text while preserving order."""
    sentences = _split_sentences(text)
    seen = set()
    out = []
    for s in sentences:
        key = re.sub(r'[^a-z0-9 ]', '', s.lower()).strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return ' '.join(out)


def _dedupe_sentences_preserve_bullets(lines):
    """Given a list of lines, split into sentences, remove duplicates, and preserve bullet markers."""
    seen = set()
    out = []
    for ln in lines:
        if ln.startswith('• '):
            text = ln[2:]
            sents = _split_sentences(text)
            for s in sents:
                key = re.sub(r'[^a-z0-9 ]', '', s.lower()).strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                out.append('• ' + s)
        else:
            sents = _split_sentences(ln)
            for s in sents:
                key = re.sub(r'[^a-z0-9 ]', '', s.lower()).strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                out.append(s)
    return '\n'.join(out)


def _extract_bullets(text, max_items=4):
    lines = [line.strip('-*• \t') for line in text.splitlines() if line.strip()]
    bullets = [line for line in lines if len(line.split()) > 3]
    if len(bullets) >= max_items:
        return bullets[:max_items]

    sentences = _split_sentences(text)
    for sentence in sentences:
        if len(sentence.split()) > 6 and sentence not in bullets:
            bullets.append(sentence)
            if len(bullets) >= max_items:
                break

    return bullets[:max_items]


def _make_hook(title, text):
    if title:
        return f"Most creators miss this about {title.split(':')[0].strip()}."

    sentences = _split_sentences(text)
    if sentences:
        first = sentences[0]
        if len(first.split()) < 15:
            return f"{first}"
        return f"Here is one lesson I wish more people understood."

    return "Nobody talks about this growth strategy."


def _make_insight(text):
    sentences = _split_sentences(text)
    if sentences:
        return sentences[0]
    return 'This is the core insight from the article.'


def _make_perspective(text):
    return 'I distilled the article into a fast, LinkedIn-native format that keeps the main insight, lessons, and a strong CTA.'


def _make_cta():
    return 'What is your biggest takeaway from this topic?'


def _make_hashtags(title, text):
    tags = []
    base = title or text
    if base:
        words = re.findall(r'\b[A-Za-z]{4,}\b', base)
        seen = []
        for word in words:
            tag = word.lower()
            if tag not in seen and len(seen) < 3:
                seen.append(tag)
        tags = [f'#{tag}' for tag in seen]
    if not tags:
        tags = ['#LinkedIn', '#ContentStrategy', '#CreatorEconomy']
    return ' '.join(tags)


def generate_linkedin_post(title, content):
    content = content or ''
    raw = _clean_text(content)
    hook = _make_hook(title, raw)
    insight = _make_insight(raw)
    bullets = _extract_bullets(raw, max_items=4)
    if len(bullets) < 3:
        sentences = _split_sentences(raw)
        for sentence in sentences[:5]:
            if sentence not in bullets and len(bullets) < 4:
                bullets.append(sentence)
    bullets = bullets[:4]
    # Remove duplicate bullets (normalized)
    bullets = _dedupe_items(bullets)

    perspective = _make_perspective(raw)
    cta = _make_cta()
    hashtags = _make_hashtags(title, raw)

    lines = [hook, '', insight, '']
    for bullet in bullets:
        lines.append(f'• {bullet}')
    lines += ['', perspective, '', cta, '', hashtags]
    # Deduplicate lines and avoid repeated content
    lines = [ln for ln in lines if ln is not None]
    # Normalize and remove duplicate lines while preserving order
    deduped_lines = _dedupe_items(lines)
    # Collapse duplicate sentences while preserving bullet formatting
    post = _dedupe_sentences_preserve_bullets(deduped_lines)

    words = post.split()
    if len(words) > MAX_WORDS:
        post = ' '.join(words[:MAX_WORDS])
        post += '\n\n' + cta + '\n' + hashtags

    return post.strip()
