"""Anthropic-inspired PDF design system for ReportLab.

Shared theme module replicating the visual language from Anthropic's
"2026 Agentic Coding Trends Report": landscape orientation, serif display
titles, generous whitespace, warm cream backgrounds, muted earth-tone
section dividers, minimal borderless tables, and callout boxes.

Usage:
    from shared.anthropic_pdf_theme import (
        AnthropicTheme, build_anthropic_styles, PAGE_SIZE, MARGINS,
        BG_CREAM, TEXT_DARK, DIVIDER_COLORS
    )
"""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, PageBreak,
    Flowable, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String

# ── Page Setup ──────────────────────────────────────────────────────────

PAGE_SIZE = landscape(letter)  # 11" x 8.5" (792 x 612 pts)
PAGE_W, PAGE_H = PAGE_SIZE
MARGINS = 1 * inch

# ── Color Palette ───────────────────────────────────────────────────────

BG_CREAM = HexColor('#FAF6F1')
TEXT_DARK = HexColor('#1a1a1a')
TEXT_BODY = HexColor('#2d2d2d')
TEXT_MUTED = HexColor('#6b6b6b')
CALLOUT_BG = HexColor('#F5F0EB')
CALLOUT_BORDER = HexColor('#E0D8D0')
LINK_BLUE = HexColor('#3366AA')

DIVIDER_COLORS = {
    "title":       HexColor('#D4845C'),  # Terracotta
    "discovery":   HexColor('#8B9A6B'),  # Sage green
    "feasibility": HexColor('#7BA3C9'),  # Muted blue
    "spec_cards":  HexColor('#A692C4'),  # Lavender
    "sources":     HexColor('#D4B0B0'),  # Dusty pink
}

# Category colors (muted versions for pill badges)
CATEGORY_COLORS = {
    "QUICK WIN":    HexColor('#8B9A6B'),
    "HIGH VALUE":   HexColor('#7BA3C9'),
    "STRATEGIC":    HexColor('#D4845C'),
    "EXPERIMENTAL": HexColor('#9E9E9E'),
}

# ── Brand Detection ─────────────────────────────────────────────────────

def _path_exists(p):
    """Check if a file path exists (handles str and Path)."""
    from pathlib import Path as _Path
    return _Path(str(p)).exists() if p else False


BRAND_MAP = {
    "export": "Export Arena",
    "arena": "Export Arena",
    "afarsemon": "Afarsemon",
    "israeli": "Afarsemon",
    "hebrew": "Afarsemon",
    "dvorkin": "Guy Dvorkin",
    "personal": "Guy Dvorkin",
    "cranianity": "Cranianity",
    "architecture": "Cranianity",
}


def detect_brand(domain_text):
    """Detect brand from domain/problem text."""
    lower = domain_text.lower()
    for keyword, brand in BRAND_MAP.items():
        if keyword in lower:
            return brand
    return "Guy Dvorkin"  # default


# ── Typography (built-in ReportLab fonts) ───────────────────────────────
# Display/Title: Times-Roman (serif) -- closest to Anthropic Serif Variable
# Body/UI: Helvetica (sans) -- closest to Anthropic Sans Variable

FONT_SERIF = 'Times-Roman'
FONT_SERIF_BOLD = 'Times-Bold'
FONT_SERIF_ITALIC = 'Times-Italic'
FONT_SANS = 'Helvetica'
FONT_SANS_BOLD = 'Helvetica-Bold'


def build_anthropic_styles():
    """Build all paragraph styles for the Anthropic theme."""
    styles = getSampleStyleSheet()

    defs = {
        # Display titles (serif, large)
        'DisplayTitle': dict(
            parent='Title', fontName=FONT_SERIF, fontSize=44, leading=50,
            textColor=TEXT_DARK, alignment=TA_LEFT, spaceAfter=12,
        ),
        'DisplaySubtitle': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=18, leading=24,
            textColor=TEXT_DARK, alignment=TA_LEFT, spaceAfter=6,
        ),
        # Section divider title (serif, white on colored bg)
        'DividerTitle': dict(
            parent='Title', fontName=FONT_SERIF, fontSize=40, leading=46,
            textColor=TEXT_DARK, alignment=TA_LEFT, spaceAfter=0,
        ),
        # TOC
        'TOCTitle': dict(
            parent='Title', fontName=FONT_SERIF, fontSize=36, leading=42,
            textColor=TEXT_DARK, alignment=TA_LEFT, spaceAfter=16,
        ),
        'TOCSection': dict(
            parent='Normal', fontName=FONT_SANS_BOLD, fontSize=11, leading=20,
            textColor=TEXT_DARK, spaceAfter=4,
        ),
        'TOCEntry': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=10, leading=18,
            textColor=TEXT_BODY, leftIndent=20, spaceAfter=2,
        ),
        # Content page headings
        'H1Serif': dict(
            parent='Heading1', fontName=FONT_SERIF, fontSize=32, leading=38,
            textColor=TEXT_DARK, spaceBefore=0, spaceAfter=16,
        ),
        'H2Sans': dict(
            parent='Heading2', fontName=FONT_SANS_BOLD, fontSize=16, leading=20,
            textColor=TEXT_DARK, spaceBefore=14, spaceAfter=6,
        ),
        'H3Sans': dict(
            parent='Heading3', fontName=FONT_SANS_BOLD, fontSize=13, leading=17,
            textColor=TEXT_BODY, spaceBefore=10, spaceAfter=4,
        ),
        # Body text
        'Body': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=11, leading=16,
            textColor=TEXT_BODY, spaceAfter=6,
        ),
        'BodyBold': dict(
            parent='Normal', fontName=FONT_SANS_BOLD, fontSize=11, leading=16,
            textColor=TEXT_BODY, spaceAfter=6,
        ),
        'BodySmall': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=10, leading=14,
            textColor=TEXT_BODY, spaceAfter=4,
        ),
        # Bullet list
        'BulletItem': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=11, leading=16,
            textColor=TEXT_BODY, spaceAfter=4, leftIndent=18, bulletIndent=6,
        ),
        # Callout box text
        'Callout': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=10.5, leading=15,
            textColor=TEXT_BODY, spaceAfter=4,
        ),
        # Muted small text
        'Muted': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=8, leading=10,
            textColor=TEXT_MUTED,
        ),
        # Table header
        'TableHeader': dict(
            parent='Normal', fontName=FONT_SANS_BOLD, fontSize=10, leading=14,
            textColor=TEXT_DARK,
        ),
        # Table cell
        'TableCell': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=10, leading=14,
            textColor=TEXT_BODY,
        ),
        # Brand mark
        'BrandMark': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=14, leading=18,
            textColor=white, spaceAfter=0,
        ),
        # Page number
        'PageNum': dict(
            parent='Normal', fontName=FONT_SANS, fontSize=8, leading=10,
            textColor=TEXT_MUTED, alignment=TA_RIGHT,
        ),
        # Score display
        'ScoreInline': dict(
            parent='Normal', fontName=FONT_SANS_BOLD, fontSize=10, leading=14,
            textColor=TEXT_DARK,
        ),
        # Card title (serif)
        'CardTitle': dict(
            parent='Heading2', fontName=FONT_SERIF, fontSize=22, leading=26,
            textColor=TEXT_DARK, spaceBefore=0, spaceAfter=10,
        ),
    }

    for name, props in defs.items():
        parent = styles[props.pop('parent')]
        styles.add(ParagraphStyle(name, parent=parent, **props))

    return styles


# ── Custom Flowables ────────────────────────────────────────────────────

class CreamBackground(Flowable):
    """Draw cream background on content pages via onPage callback."""

    # Class-level brand config; set before building the doc
    _brand_config = {}

    @classmethod
    def set_brand_config(cls, config):
        cls._brand_config = config or {}

    @staticmethod
    def draw_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(white)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

        footer_y = 0.5 * inch
        config = CreamBackground._brand_config
        website = config.get("website", "")
        logo_path = config.get("logo")  # black logo for content pages

        # Brand footer bottom-left: small logo + website link
        x = MARGINS
        if logo_path and _path_exists(logo_path):
            from reportlab.lib.utils import ImageReader
            canvas.drawImage(ImageReader(str(logo_path)),
                             x, footer_y - 4, width=16, height=16,
                             mask='auto', preserveAspectRatio=True)
            x += 22
        if website:
            canvas.setFont(FONT_SANS, 8)
            canvas.setFillColor(TEXT_MUTED)
            url = f"https://{website}"
            canvas.drawString(x, footer_y, website)
            # Make it a clickable link
            text_w = canvas.stringWidth(website, FONT_SANS, 8)
            canvas.linkURL(url, (x, footer_y - 2, x + text_w, footer_y + 10))

        # Page number bottom-right
        canvas.setFont(FONT_SANS, 8)
        canvas.setFillColor(TEXT_MUTED)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(PAGE_W - MARGINS, footer_y, str(page_num))
        canvas.restoreState()


class PillBadge(Flowable):
    """Rounded pill badge like 'Trend 1' or 'Quick Win'."""

    def __init__(self, text, bg_color=None, text_color=TEXT_DARK, width=None, height=22):
        super().__init__()
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self._height = height
        self._width = width

    def wrap(self, availWidth, availHeight):
        if self._width:
            w = self._width
        else:
            from reportlab.pdfbase.pdfmetrics import stringWidth
            w = stringWidth(self.text, FONT_SANS, 9) + 24
        return w, self._height

    def draw(self):
        w, h = self.wrap(0, 0)
        canvas = self.canv
        canvas.saveState()
        if self.bg_color:
            canvas.setFillColor(self.bg_color)
            canvas.roundRect(0, 0, w, h, radius=h / 2, fill=1, stroke=0)
            canvas.setFillColor(white)
        else:
            canvas.setStrokeColor(TEXT_MUTED)
            canvas.setLineWidth(0.75)
            canvas.roundRect(0, 0, w, h, radius=h / 2, fill=0, stroke=1)
            canvas.setFillColor(self.text_color)
        canvas.setFont(FONT_SANS, 9)
        canvas.drawCentredString(w / 2, (h - 9) / 2 + 1, self.text)
        canvas.restoreState()


class CalloutBox(Flowable):
    """Warm-gray callout box with thin rounded border."""

    def __init__(self, content_flowables, width=None):
        super().__init__()
        self.content = content_flowables
        self._width = width

    def wrap(self, availWidth, availHeight):
        w = self._width or availWidth
        inner_w = w - 24  # padding
        total_h = 0
        for f in self.content:
            fw, fh = f.wrap(inner_w, availHeight)
            total_h += fh
        total_h += 24  # top + bottom padding
        self._actual_width = w
        self._actual_height = total_h
        return w, total_h

    def draw(self):
        canvas = self.canv
        w = self._actual_width
        h = self._actual_height
        # Background
        canvas.saveState()
        canvas.setFillColor(CALLOUT_BG)
        canvas.setStrokeColor(CALLOUT_BORDER)
        canvas.setLineWidth(0.75)
        canvas.roundRect(0, 0, w, h, radius=6, fill=1, stroke=1)
        canvas.restoreState()
        # Draw content
        y = h - 12  # top padding
        for f in self.content:
            fw, fh = f.wrap(w - 24, h)
            f.drawOn(canvas, 12, y - fh)
            y -= fh


# ── Builder Functions ───────────────────────────────────────────────────

def make_divider_page(title, color, page_num_text=None):
    """Create elements for a full-bleed colored section divider page.

    Returns a list of flowables to append to the story.
    The actual colored background is drawn via a custom onPage callback
    using DividerPageTemplate, but since we use SimpleDocTemplate,
    we insert a special DividerPage flowable that draws the background.
    """
    return [DividerPageFlowable(title, color), PageBreak()]


class DividerPageFlowable(Flowable):
    """Full-bleed colored page with large serif title at bottom-left."""

    def __init__(self, title, color):
        super().__init__()
        self.title = title
        self.color = color

    def wrap(self, availWidth, availHeight):
        return availWidth, availHeight

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        # Full-bleed color background (extend beyond margins)
        canvas.setFillColor(self.color)
        canvas.rect(-2*MARGINS, -2*MARGINS, PAGE_W + 2*MARGINS, PAGE_H + 2*MARGINS, fill=1, stroke=0)
        # Title at bottom-left
        canvas.setFont(FONT_SERIF, 40)
        canvas.setFillColor(TEXT_DARK)
        # Handle multi-line titles
        lines = self.title.split('\n')
        y_start = MARGINS * 0.5 + (len(lines) - 1) * 46
        for i, line in enumerate(lines):
            canvas.drawString(0, y_start - i * 46, line)
        # Page number bottom-right
        canvas.setFont(FONT_SANS, 8)
        canvas.setFillColor(TEXT_MUTED)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(
            PAGE_W - MARGINS * 2, -MARGINS + 0.5 * inch, str(page_num)
        )
        canvas.restoreState()


def make_title_page(title, subtitle, brand_text, date, color=None, brand_config=None):
    """Create elements for the title page (full-bleed terracotta)."""
    color = color or DIVIDER_COLORS["title"]
    return [TitlePageFlowable(title, subtitle, brand_text, date, color, brand_config), PageBreak()]


class TitlePageFlowable(Flowable):
    """Full-bleed title page matching Anthropic style."""

    def __init__(self, title, subtitle, brand_text, date, color, brand_config=None):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.brand_text = brand_text
        self.date = date
        self.color = color
        self.brand_config = brand_config or {}

    def wrap(self, availWidth, availHeight):
        return availWidth, availHeight

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        # Full-bleed background
        canvas.setFillColor(self.color)
        canvas.rect(-2*MARGINS, -2*MARGINS, PAGE_W + 2*MARGINS, PAGE_H + 2*MARGINS, fill=1, stroke=0)
        content_w = PAGE_W - 2 * MARGINS

        # Title top-left, large serif
        canvas.setFont(FONT_SERIF, 52)
        canvas.setFillColor(TEXT_DARK)
        # Wrap title text manually for long titles
        lines = self._wrap_text(self.title, FONT_SERIF, 52, content_w)
        y = PAGE_H - MARGINS * 2 - 52
        for line in lines:
            canvas.drawString(0, y, line)
            y -= 58

        # Subtitle below title
        canvas.setFont(FONT_SANS, 18)
        canvas.setFillColor(TEXT_DARK)
        y -= 16
        sub_lines = self._wrap_text(self.subtitle, FONT_SANS, 18, content_w * 0.6)
        for line in sub_lines:
            canvas.drawString(0, y, line)
            y -= 24

        # Bottom brand strip: separator line, logo, brand name, contact, date
        bottom_y = -MARGINS + 0.5 * inch
        x_offset = 0

        # Thin separator line
        canvas.setStrokeColor(TEXT_MUTED)
        canvas.setLineWidth(0.5)
        canvas.line(0, bottom_y + 46, content_w, bottom_y + 46)

        # Black logo (visible on terracotta)
        logo = self.brand_config.get("logo")
        if logo and _path_exists(logo):
            from reportlab.lib.utils import ImageReader
            canvas.drawImage(ImageReader(str(logo)),
                             0, bottom_y - 2, width=30, height=30,
                             mask='auto', preserveAspectRatio=True)
            x_offset = 38

        # Brand name
        canvas.setFont(FONT_SANS_BOLD, 14)
        canvas.setFillColor(TEXT_DARK)
        canvas.drawString(x_offset, bottom_y + 16, self.brand_text)

        # Email + website below brand name
        email = self.brand_config.get("email", "")
        website = self.brand_config.get("website", "")
        contact_line = "  |  ".join(filter(None, [email, website]))
        if contact_line:
            canvas.setFont(FONT_SANS, 9)
            canvas.setFillColor(TEXT_DARK)
            canvas.drawString(x_offset, bottom_y, contact_line)

        # Date right-aligned, vertically centered in strip
        canvas.setFont(FONT_SANS, 10)
        canvas.setFillColor(TEXT_DARK)
        canvas.drawRightString(content_w, bottom_y + 8, self.date)

        canvas.restoreState()

    def _wrap_text(self, text, font, size, max_width):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if stringWidth(test, font, size) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [text]


def make_minimal_table(data, col_widths, has_header=True):
    """Create a minimal borderless table matching Anthropic style.

    - No grid lines except thin bottom border on header row
    - No alternating row colors
    - Clean sans-serif text
    """
    table = Table(data, colWidths=col_widths)
    style_cmds = [
        ('FONTNAME', (0, 0), (-1, -1), FONT_SANS),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), TEXT_BODY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]
    if has_header:
        style_cmds.extend([
            ('FONTNAME', (0, 0), (-1, 0), FONT_SANS_BOLD),
            ('TEXTCOLOR', (0, 0), (-1, 0), TEXT_DARK),
            ('LINEBELOW', (0, 0), (-1, 0), 1, HexColor('#CCCCCC')),
        ])
    table.setStyle(TableStyle(style_cmds))
    return table


def make_callout_box(content_flowables, width=None):
    """Create a warm-gray callout box."""
    return CalloutBox(content_flowables, width=width)


def make_pill_badge(text, bg_color=None):
    """Create a rounded pill badge."""
    return PillBadge(text, bg_color=bg_color)


def make_two_column(left_flowables, right_flowables, left_pct=0.48):
    """Create a two-column layout using a Table.

    Returns a Table flowable with left and right content cells.
    """
    avail_w = PAGE_W - 2 * MARGINS
    left_w = avail_w * left_pct
    right_w = avail_w * (1 - left_pct) - 12  # 12pt gutter

    # Wrap flowables in mini-tables so they flow vertically within cells
    left_cell = left_flowables
    right_cell = right_flowables

    table = Table(
        [[left_cell, right_cell]],
        colWidths=[left_w, right_w],
    )
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return table


# ── Convenience: Document Setup ─────────────────────────────────────────

def create_doc(output_path):
    """Create a SimpleDocTemplate with Anthropic theme settings."""
    from reportlab.platypus import SimpleDocTemplate
    return SimpleDocTemplate(
        str(output_path),
        pagesize=PAGE_SIZE,
        topMargin=MARGINS,
        bottomMargin=MARGINS,
        leftMargin=MARGINS,
        rightMargin=MARGINS,
    )
