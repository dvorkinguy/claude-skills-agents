#!/usr/bin/env python3
"""Generate styled PDF report for AI Automation Brainstorm.

Uses the Anthropic-inspired PDF design system (landscape, serif titles,
warm cream backgrounds, muted earth-tone section dividers).

Usage:
    1. Write brainstorm data to tmp/automation-brainstorm-data.json
    2. Run: python /home/gi/.claude/skills/ai-automation-brainstorm/generate_pdf.py

Expected JSON structure:
{
    "date": "2026-03-07",
    "domain": "logistics",
    "problem_area": "shipment tracking",
    "cost": "$0.00",
    "discoveries": [
        {"num": 1, "name": "...", "source": "...", "problem": "...", "proven": true}
    ],
    "feasibility": [
        {"num": 1, "name": "...", "existing_skill": "...", "n8n_nodes": "Yes",
         "stack_fit": "High", "build_hours": "4h", "feasibility": "Ready"}
    ],
    "spec_cards": [
        {
            "num": 1, "category": "QUICK WIN", "name": "...", "score": "45/50",
            "outcome": "...", "architecture": "...",
            "tech_stack": {"n8n_nodes": [...], "ai_model": "...", "integrations": [...], "skills": [...]},
            "template_id": null, "build_time": "4h",
            "revenue": {"setup": "$500", "monthly": "$297/mo", "usage": null, "tier": "Starter"},
            "steps": ["Step 1", "Step 2", "Step 3"],
            "scores": {"revenue": 8, "impact": 9, "feasibility": 10, "demand": 9, "differentiation": 9}
        }
    ],
    "sources": ["Source 1", "Source 2"]
}
"""

import json
import re
import sys
import os
from pathlib import Path

# Add skills directory to path for shared module imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.anthropic_pdf_theme import (
    PAGE_SIZE, PAGE_W, PAGE_H, MARGINS,
    BG_CREAM, TEXT_DARK, TEXT_BODY, TEXT_MUTED, LINK_BLUE,
    CALLOUT_BG, CALLOUT_BORDER,
    DIVIDER_COLORS, CATEGORY_COLORS,
    FONT_SERIF, FONT_SANS, FONT_SANS_BOLD,
    build_anthropic_styles, detect_brand,
    make_title_page, make_divider_page, make_minimal_table,
    make_callout_box, make_pill_badge, make_two_column,
    CreamBackground,
)

from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor, white, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, Flowable
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.widgetbase import TypedPropertyCollection
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Image as RLImage
from collections import Counter
from reportlab.platypus import SimpleDocTemplate


# ── QA Validation ─────────────────────────────────────────────────────

class AuditingDocTemplate(SimpleDocTemplate):
    """SimpleDocTemplate subclass that records per-page flowable data for QA."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audit_data = {"pages": []}
        self._current_page = None

    def beforePage(self):
        self._current_page = {
            "page_num": self.page,
            "flowable_count": 0,
            "total_content_height": 0,
            "flowables": [],
        }

    def afterFlowable(self, flowable):
        if self._current_page is None:
            return
        # Use already-computed height from layout (avoid re-calling wrap)
        h = getattr(flowable, 'height', 0) or 0
        record = {
            "type": type(flowable).__name__,
            "height": h,
        }
        # Capture text preview for Paragraphs
        if hasattr(flowable, "text"):
            record["text_preview"] = str(flowable.text)[:80]
        self._current_page["flowable_count"] += 1
        self._current_page["total_content_height"] += h
        self._current_page["flowables"].append(record)

    def afterPage(self):
        if self._current_page is not None:
            self.audit_data["pages"].append(self._current_page)
            self._current_page = None


def _count_pdf_pages(pdf_path):
    """Count actual page objects in a PDF via raw byte regex."""
    with open(pdf_path, "rb") as f:
        data = f.read()
    return len(re.findall(rb'/Type\s*/Page(?!s)', data))


def validate_pdf(pdf_path, audit_data, data):
    """Post-build QA checks. Returns list of (level, message) tuples."""
    issues = []
    pages = audit_data.get("pages", [])
    spec_cards = data.get("spec_cards", [])
    frame_height = PAGE_H - 2 * MARGINS  # usable content height per page

    # 1. Page count sanity
    actual_pages = _count_pdf_pages(pdf_path)
    # Expected: title + TOC + 4 dividers + discovery table + discovery insights
    #         + feasibility table + feasibility insights + spec cards + sources + closing
    min_pages = 8 + len(spec_cards) // 4  # conservative lower bound
    max_pages = 12 + len(spec_cards) * 2   # generous upper bound
    if actual_pages < min_pages:
        issues.append(("WARN", f"Page count ({actual_pages}) seems low (expected >= {min_pages})"))
    elif actual_pages > max_pages:
        issues.append(("WARN", f"Page count ({actual_pages}) seems high (expected <= {max_pages})"))
    else:
        issues.append(("PASS", f"Page count: {actual_pages} pages (within expected range)"))

    # 2. Content overflow check (generous threshold -- ReportLab handles pagination,
    #    so only flag extreme cases where a single flowable exceeds frame height)
    overflow_pages = []
    for p in pages:
        for f in p.get("flowables", []):
            if f["height"] > frame_height * 1.05:
                overflow_pages.append((p["page_num"], f["type"], f["height"]))
                break
    if overflow_pages:
        details = ", ".join(f"p{pn} ({ft})" for pn, ft, _ in overflow_pages)
        issues.append(("WARN", f"Oversized flowable on: {details}"))
    else:
        issues.append(("PASS", "No oversized flowables detected"))

    # 3. Critical pages check
    if pages:
        # Title page should have TitlePageFlowable
        first_types = [f["type"] for f in pages[0].get("flowables", [])]
        if "TitlePageFlowable" in first_types:
            issues.append(("PASS", "Title page has TitlePageFlowable"))
        else:
            issues.append(("WARN", "Title page missing TitlePageFlowable"))

        # Divider pages (check for DividerPageFlowable presence across all pages)
        divider_count = sum(
            1 for p in pages
            for f in p.get("flowables", [])
            if f["type"] == "DividerPageFlowable"
        )
        expected_dividers = 4  # discovery, feasibility, spec_cards, sources
        if divider_count >= expected_dividers:
            issues.append(("PASS", f"Found {divider_count} divider pages (expected {expected_dividers})"))
        else:
            issues.append(("WARN", f"Only {divider_count} divider pages (expected {expected_dividers})"))

        # Closing page should have brand content
        last_page = pages[-1]
        if last_page["flowable_count"] >= 3:
            issues.append(("PASS", "Closing page has content"))
        else:
            issues.append(("WARN", f"Closing page has only {last_page['flowable_count']} flowables"))
    else:
        issues.append(("WARN", "No page data collected -- audit may have failed"))

    return issues

# ── Brand Config ───────────────────────────────────────────────────────
# Brand info shown on title page and closing page of every report.
_PROJECT_ROOT = Path.home() / "Documents" / "_projects" / "DVORKIN-2"

BRAND_CONFIG = {
    "Export Arena": {
        "tagline": "AI Workforce as a Service\nfor Global Trade SMBs",
        "email": "hello@exportarena.com",
        "website": "exportarena.com",
        "logo": _PROJECT_ROOT / "projects" / "export-arena" / "4_1_2.png",        # black (content pages)
        "logo_white": _PROJECT_ROOT / "projects" / "export-arena" / "4_1.png",    # white (title/divider)
    },
    "Guy Dvorkin": {
        "tagline": "AI Automations & AI Workforce\nfor Businesses",
        "email": "guy@guydvorkin.com",
        "website": "guydvorkin.com",
        "logo": None,
        "logo_white": None,
    },
    "Afarsemon": {
        "tagline": "AI Workforce as a Service\nfor Israeli Businesses",
        "email": "hello@afarsemon.com",
        "website": "afarsemon.com",
        "logo": None,
        "logo_white": None,
    },
}

# Acronyms to preserve in title casing
ACRONYMS = {"CRM", "AI", "API", "ICP", "SDR", "BDR", "ERP", "KPI", "ROI", "SaaS",
            "SEO", "SMM", "SQL", "ETL", "LLM", "RAG", "PDF", "CSV", "URL", "SMS",
            "B2B", "B2C", "HR", "IT", "QA", "ML", "NLP", "OCR", "RPA"}


def smart_title(text):
    """Title-case text while preserving known acronyms."""
    words = text.title().split()
    return " ".join(w.upper() if w.upper() in ACRONYMS else w for w in words)


def load_data():
    """Load brainstorm data from JSON file."""
    json_path = Path.home() / "Documents" / "_projects" / "DVORKIN-2" / "tmp" / "automation-brainstorm-data.json"
    if not json_path.exists():
        json_path = Path("tmp/automation-brainstorm-data.json")
    if not json_path.exists():
        print(f"ERROR: Data file not found at {json_path}")
        print("Write brainstorm data to tmp/automation-brainstorm-data.json first.")
        sys.exit(1)
    with open(json_path) as f:
        return json.load(f)


class BigStatFlowable(Flowable):
    """Large stat number with label underneath, Anthropic style."""

    def __init__(self, number, label, color=None, width=150, height=80):
        super().__init__()
        self.number = str(number)
        self.label = label
        self.color = color or TEXT_DARK
        self._width = width
        self._height = height

    def wrap(self, availWidth, availHeight):
        return self._width, self._height

    def draw(self):
        c = self.canv
        c.saveState()
        # Big number
        c.setFont(FONT_SERIF, 36)
        c.setFillColor(self.color)
        c.drawCentredString(self._width / 2, 30, self.number)
        # Label below
        c.setFont(FONT_SANS, 10)
        c.setFillColor(TEXT_MUTED)
        c.drawCentredString(self._width / 2, 10, self.label)
        c.restoreState()


class HBarChartFlowable(Flowable):
    """Clean horizontal bar chart with Anthropic styling."""

    def __init__(self, labels, values, bar_color=None, width=400, height=None,
                 value_suffix="", title=""):
        super().__init__()
        self.labels = labels
        self.values = values
        self.bar_color = bar_color or DIVIDER_COLORS["discovery"]
        self._width = width
        self.bar_h = 18
        self.gap = 4
        self._height = height or (len(labels) * (self.bar_h + self.gap) + 40)
        self.value_suffix = value_suffix
        self.title = title

    def wrap(self, availWidth, availHeight):
        return self._width, self._height

    def draw(self):
        c = self.canv
        c.saveState()

        label_col_w = 160
        chart_w = self._width - label_col_w - 50
        max_val = max(self.values) if self.values else 1

        y_offset = self._height - 10

        # Title
        if self.title:
            c.setFont(FONT_SANS_BOLD, 12)
            c.setFillColor(TEXT_DARK)
            c.drawString(0, y_offset, self.title)
            y_offset -= 28

        for i, (label, val) in enumerate(zip(self.labels, self.values)):
            y = y_offset - i * (self.bar_h + self.gap)

            # Label
            c.setFont(FONT_SANS, 10)
            c.setFillColor(TEXT_BODY)
            c.drawRightString(label_col_w - 12, y + 6, label)

            # Bar
            bar_w = (val / max_val) * chart_w if max_val > 0 else 0
            c.setFillColor(self.bar_color)
            c.roundRect(label_col_w, y, max(bar_w, 4), self.bar_h,
                        radius=3, fill=1, stroke=0)

            # Value label
            c.setFont(FONT_SANS_BOLD, 10)
            c.setFillColor(TEXT_DARK)
            c.drawString(label_col_w + bar_w + 8, y + 6,
                         f"{val}{self.value_suffix}")

        c.restoreState()


class DonutChartFlowable(Flowable):
    """Clean donut/ring chart with legend, Anthropic style."""

    def __init__(self, labels, values, colors, width=280, height=200, title=""):
        super().__init__()
        self.labels = labels
        self.values = values
        self.colors = colors
        self._width = width
        self._height = height
        self.title = title

    def wrap(self, availWidth, availHeight):
        return self._width, self._height

    def draw(self):
        import math
        c = self.canv
        c.saveState()

        total = sum(self.values) if self.values else 1
        title_offset = 24 if self.title else 0
        available_h = self._height - title_offset - 10  # space for ring
        r_outer = min(65, available_h / 2)
        r_inner = r_outer * 0.58
        cx = r_outer + 25
        cy = title_offset + available_h / 2 - 10

        y_title = self._height - 10
        if self.title:
            c.setFont(FONT_SANS_BOLD, 12)
            c.setFillColor(TEXT_DARK)
            c.drawString(0, y_title, self.title)

        # Draw arcs
        start_angle = 90
        for i, (label, val) in enumerate(zip(self.labels, self.values)):
            if val == 0:
                continue
            sweep = (val / total) * 360
            c.setFillColor(self.colors[i % len(self.colors)])
            c.setStrokeColor(white)
            c.setLineWidth(2)
            # Draw as wedge
            p = c.beginPath()
            p.moveTo(cx + r_inner * math.cos(math.radians(start_angle)),
                     cy + r_inner * math.sin(math.radians(start_angle)))
            # Outer arc
            for step in range(int(sweep) + 1):
                angle = math.radians(start_angle + step)
                p.lineTo(cx + r_outer * math.cos(angle),
                         cy + r_outer * math.sin(angle))
            # Inner arc (reverse)
            for step in range(int(sweep), -1, -1):
                angle = math.radians(start_angle + step)
                p.lineTo(cx + r_inner * math.cos(angle),
                         cy + r_inner * math.sin(angle))
            p.close()
            c.drawPath(p, fill=1, stroke=1)
            start_angle += sweep

        # Center text
        c.setFont(FONT_SERIF, 22)
        c.setFillColor(TEXT_DARK)
        c.drawCentredString(cx, cy + 4, str(total))
        c.setFont(FONT_SANS, 8)
        c.setFillColor(TEXT_MUTED)
        c.drawCentredString(cx, cy - 10, "total")

        # Legend on the right
        legend_x = cx + r_outer + 25
        legend_y = cy + (len(self.labels) * 22) / 2
        for i, (label, val) in enumerate(zip(self.labels, self.values)):
            y = legend_y - i * 22
            # Color swatch
            c.setFillColor(self.colors[i % len(self.colors)])
            c.roundRect(legend_x, y - 4, 14, 14, radius=2, fill=1, stroke=0)
            # Label
            c.setFont(FONT_SANS, 10)
            c.setFillColor(TEXT_BODY)
            c.drawString(legend_x + 20, y, f"{label}  ({val})")

        c.restoreState()


def make_phase1_summary(discoveries, styles):
    """Build visual summary page for Phase 1: Solution Discovery."""
    elements = []

    elements.append(Paragraph("Discovery Insights", styles['H1Serif']))
    elements.append(Spacer(1, 8))

    # Categorize sources
    source_categories = Counter()
    for d in discoveries:
        src = d.get("source", "").lower()
        if "n8n" in src:
            source_categories["n8n Templates"] += 1
        elif "apify" in src:
            source_categories["Apify Actors"] += 1
        elif any(x in src for x in ["clay", "jeeva", "gumloop", "taaft", "futuretools", "attio", "breakcold"]):
            source_categories["SaaS / AI Tools"] += 1
        else:
            source_categories["Other Sources"] += 1

    proven_count = sum(1 for d in discoveries if d.get("proven"))
    total = len(discoveries)

    # Big stats row
    stat_colors = [DIVIDER_COLORS["discovery"], DIVIDER_COLORS["feasibility"],
                   DIVIDER_COLORS["spec_cards"]]
    stats_data = [
        (str(total), "Solutions Found", stat_colors[0]),
        (f"{proven_count}/{total}", "Proven in Production", stat_colors[1]),
        (str(len(source_categories)), "Source Categories", stat_colors[2]),
    ]

    stat_flowables = []
    for num, label, color in stats_data:
        stat_flowables.append(BigStatFlowable(num, label, color=color, width=180, height=80))

    stat_table = Table([stat_flowables], colWidths=[180] * len(stat_flowables))
    stat_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(stat_table)
    elements.append(Spacer(1, 24))

    # Source distribution bar chart + donut side by side
    sorted_sources = sorted(source_categories.items(), key=lambda x: x[1], reverse=True)
    src_labels = [s[0] for s in sorted_sources]
    src_values = [s[1] for s in sorted_sources]

    donut_colors = [
        DIVIDER_COLORS["discovery"],
        DIVIDER_COLORS["feasibility"],
        DIVIDER_COLORS["spec_cards"],
        DIVIDER_COLORS["sources"],
    ]

    bar_chart = HBarChartFlowable(
        src_labels, src_values,
        bar_color=DIVIDER_COLORS["discovery"],
        width=380, title="Solutions by Source"
    )

    donut_chart = DonutChartFlowable(
        src_labels, src_values, donut_colors,
        width=280, height=bar_chart._height,
        title="Source Distribution"
    )

    chart_table = Table([[bar_chart, donut_chart]],
                        colWidths=[400, 280])
    chart_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(chart_table)
    elements.append(Spacer(1, 20))

    # Key insight callout
    insight_text = (
        f"All {proven_count} solutions are proven in production environments. "
        f"The largest category is n8n-based templates ({source_categories.get('n8n Templates', 0)} solutions), "
        f"followed by Apify actors ({source_categories.get('Apify Actors', 0)} solutions) -- "
        f"both already in the existing tech stack."
    )
    elements.append(make_callout_box([
        Paragraph("<b>Key Insight</b>", styles['Callout']),
        Paragraph(insight_text, styles['Callout']),
    ]))

    return elements


def make_phase2_summary(feasibility, styles):
    """Build visual summary page for Phase 2: Feasibility Matrix."""
    elements = []

    elements.append(Paragraph("Feasibility Insights", styles['H1Serif']))
    elements.append(Spacer(1, 4))

    # Count statuses
    status_counts = Counter(f.get("feasibility", "Unknown") for f in feasibility)
    stack_fit_counts = Counter(f.get("stack_fit", "Unknown") for f in feasibility)

    # Parse build hours
    build_hours = []
    for f in feasibility:
        bh = f.get("build_hours", "0h").replace("h", "")
        try:
            build_hours.append(int(bh))
        except ValueError:
            build_hours.append(0)

    total_hours = sum(build_hours)
    avg_hours = total_hours / len(build_hours) if build_hours else 0
    ready_count = status_counts.get("Ready", 0)
    high_fit = stack_fit_counts.get("High", 0)

    # Big stats (compact)
    stat_colors = [DIVIDER_COLORS["feasibility"], DIVIDER_COLORS["discovery"],
                   DIVIDER_COLORS["title"]]
    stats_data = [
        (f"{ready_count}/{len(feasibility)}", "Ready to Build", stat_colors[0]),
        (f"{total_hours}h", "Total Build Time", stat_colors[1]),
        (f"{avg_hours:.0f}h", "Avg per Solution", stat_colors[2]),
    ]

    stat_flowables = []
    for num, label, color in stats_data:
        stat_flowables.append(BigStatFlowable(num, label, color=color, width=180, height=55))

    stat_table = Table([stat_flowables], colWidths=[180] * len(stat_flowables))
    stat_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(stat_table)
    elements.append(Spacer(1, 8))

    # Feasibility status donut + Stack fit donut side by side
    status_labels = list(status_counts.keys())
    status_values = list(status_counts.values())
    status_colors = [
        DIVIDER_COLORS["discovery"],   # Ready = green
        DIVIDER_COLORS["title"],       # Needs Work = terracotta
        HexColor('#9E9E9E'),           # Blocked = gray
    ]

    fit_labels = []
    fit_values = []
    fit_order = ["High", "Med", "Low"]
    for f in fit_order:
        if f in stack_fit_counts:
            fit_labels.append(f"{f} Fit")
            fit_values.append(stack_fit_counts[f])
    fit_colors = [
        DIVIDER_COLORS["feasibility"],
        DIVIDER_COLORS["spec_cards"],
        HexColor('#9E9E9E'),
    ]

    donut1 = DonutChartFlowable(
        status_labels, status_values, status_colors,
        width=280, height=110, title="Build Readiness"
    )
    donut2 = DonutChartFlowable(
        fit_labels, fit_values, fit_colors,
        width=280, height=110, title="Stack Fit"
    )

    chart_table = Table([[donut1, donut2]],
                        colWidths=[340, 340])
    chart_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(chart_table)
    elements.append(Spacer(1, 6))

    # Build hours bar chart (compact: bar_h=14, gap=2)
    # Sort by build hours descending
    sorted_items = sorted(zip(
        [f.get("name", "") for f in feasibility],
        build_hours
    ), key=lambda x: x[1], reverse=True)
    # Truncate names
    bar_labels = [n[:40] + "..." if len(n) > 40 else n for n, _ in sorted_items]
    bar_values = [v for _, v in sorted_items]

    bar = HBarChartFlowable(
        bar_labels, bar_values,
        bar_color=DIVIDER_COLORS["feasibility"],
        width=650, title="Build Effort (hours)",
        value_suffix="h"
    )
    bar.bar_h = 14
    bar.gap = 2
    bar._height = len(bar_labels) * (14 + 2) + 34
    elements.append(bar)

    return elements


def build_pdf():
    """Build the full PDF report."""
    data = load_data()
    date = data.get("date", "Unknown")
    domain = data.get("domain", "Unknown")
    problem_area = data.get("problem_area", "")
    cost = data.get("cost", "$0.00")

    discoveries = data.get("discoveries", [])
    feasibility = data.get("feasibility", [])
    spec_cards = data.get("spec_cards", [])
    sources = data.get("sources", [])

    brand = detect_brand(domain)
    styles = build_anthropic_styles()

    # Output path
    out_dir = Path.home() / "Documents" / "_projects" / "DVORKIN-2" / "tmp"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"automation-brainstorm-{date}.pdf"

    doc = AuditingDocTemplate(
        str(out_path),
        pagesize=PAGE_SIZE,
        topMargin=MARGINS,
        bottomMargin=MARGINS,
        leftMargin=MARGINS,
        rightMargin=MARGINS,
    )
    story = []

    avail_w = PAGE_W - 2 * MARGINS

    # ===== TITLE PAGE (full-bleed terracotta) =====
    title_text = "AI Automation Brainstorm"
    subtitle_text = smart_title(domain)
    if problem_area:
        subtitle_text += f" -- {smart_title(problem_area)}"

    brand_info = BRAND_CONFIG.get(brand, BRAND_CONFIG.get("Guy Dvorkin"))
    CreamBackground.set_brand_config(brand_info)
    story.extend(make_title_page(title_text, subtitle_text, brand, date, brand_config=brand_info))

    # ===== TABLE OF CONTENTS =====
    story.append(Paragraph("Contents", styles['TOCTitle']))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#E0D8D0'),
                             spaceAfter=14, hAlign='LEFT'))

    cat_counts = {}
    for card in spec_cards:
        cat = card.get("category", "EXPERIMENTAL")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    toc_sections = [
        (f"Phase 1: Solution Discovery", f"{len(discoveries)} solutions found"),
        (f"Phase 2: Feasibility Matrix", f"{len(feasibility)} evaluated"),
        (f"Phase 3: Automation Spec Cards", f"{len(spec_cards)} cards"),
    ]
    for cat_key, cat_label in [("QUICK WIN", "Quick Wins"), ("HIGH VALUE", "High Value"),
                                ("STRATEGIC", "Strategic"), ("EXPERIMENTAL", "Experimental")]:
        count = cat_counts.get(cat_key, 0)
        if count > 0:
            toc_sections.append((f"    {cat_label}", f"{count}"))
    toc_sections.append(("Sources", ""))

    for section, detail in toc_sections:
        indent = 30 if section.startswith("    ") else 0
        section = section.strip()
        s = ParagraphStyle('toc_tmp', parent=styles['TOCEntry'], leftIndent=indent)
        if detail:
            story.append(Paragraph(f"<b>{section}</b>  <font color='#6b6b6b'>{detail}</font>", s))
        else:
            story.append(Paragraph(f"<b>{section}</b>", s))

    # Summary stats as a clean row
    story.append(Spacer(1, 16))
    summary_data = [[
        f"{len(discoveries)} Solutions", f"{len(feasibility)} Evaluated",
        f"{len(spec_cards)} Spec Cards", f"Cost: {cost}"
    ]]
    summary_table = Table(summary_data, colWidths=[avail_w / 4] * 4)
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_SANS),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), TEXT_MUTED),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, HexColor('#E0D8D0')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, HexColor('#E0D8D0')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # ===== PHASE 1: DISCOVERY =====
    story.extend(make_divider_page("Phase 1:\nSolution Discovery", DIVIDER_COLORS["discovery"]))
    story.append(make_pill_badge("Phase 1"))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Solution Discovery", styles['H1Serif']))
    story.append(Paragraph(
        f"Proven AI automations for <b>{domain}</b> discovered from web research, "
        f"n8n templates, tool directories, and Claude Code capabilities.",
        styles['Body']
    ))
    story.append(Spacer(1, 12))

    if discoveries:
        cell = styles['TableCell']
        header = styles['TableHeader']
        disc_data = [[
            Paragraph("#", header),
            Paragraph("Automation / Solution", header),
            Paragraph("Source", header),
            Paragraph("Target Problem", header),
            Paragraph("Proven", header),
        ]]
        for d in discoveries:
            proven_text = "Yes" if d.get("proven") else "No"
            disc_data.append([
                Paragraph(str(d.get("num", "")), cell),
                Paragraph(d.get("name", ""), cell),
                Paragraph(d.get("source", ""), cell),
                Paragraph(d.get("problem", ""), cell),
                Paragraph(proven_text, cell),
            ])
        story.append(make_minimal_table(
            disc_data,
            [0.35 * inch, 3.0 * inch, 2.0 * inch, 2.5 * inch, 0.7 * inch]
        ))

    # Phase 1 visual summary page
    story.append(PageBreak())
    story.extend(make_phase1_summary(discoveries, styles))
    story.append(PageBreak())

    # ===== PHASE 2: FEASIBILITY =====
    story.extend(make_divider_page("Phase 2:\nFeasibility Matrix", DIVIDER_COLORS["feasibility"]))
    story.append(make_pill_badge("Phase 2"))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Feasibility Matrix", styles['H1Serif']))
    story.append(Spacer(1, 8))

    if feasibility:
        cell = styles['TableCell']
        header = styles['TableHeader']
        feas_data = [[
            Paragraph("#", header),
            Paragraph("Automation", header),
            Paragraph("Existing Skill", header),
            Paragraph("n8n Nodes", header),
            Paragraph("Stack Fit", header),
            Paragraph("Build", header),
            Paragraph("Status", header),
        ]]
        for f in feasibility:
            feas_data.append([
                Paragraph(str(f.get("num", "")), cell),
                Paragraph(f.get("name", ""), cell),
                Paragraph(f.get("existing_skill", "-"), cell),
                Paragraph(f.get("n8n_nodes", "-"), cell),
                Paragraph(f.get("stack_fit", "-"), cell),
                Paragraph(f.get("build_hours", "-"), cell),
                Paragraph(f.get("feasibility", "-"), cell),
            ])
        story.append(make_minimal_table(
            feas_data,
            [0.35 * inch, 2.2 * inch, 1.6 * inch, 1.2 * inch, 0.7 * inch, 0.6 * inch, 0.9 * inch]
        ))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Ready</b> = build today  |  <b>Needs Work</b> = missing 1-2 components  |  "
        "<b>Blocked</b> = missing critical integration",
        styles['Muted']
    ))

    # Phase 2 visual summary page
    story.append(PageBreak())
    story.extend(make_phase2_summary(feasibility, styles))
    story.append(PageBreak())

    # ===== PHASE 3: SPEC CARDS =====
    story.extend(make_divider_page("Phase 3:\nAutomation Spec Cards", DIVIDER_COLORS["spec_cards"]))

    for card in spec_cards:
        cat = card.get("category", "EXPERIMENTAL")
        cat_color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["EXPERIMENTAL"])

        # Category label for the pill badge on every card
        if cat == "QUICK WIN":
            cat_label = "Quick Win"
        elif cat == "HIGH VALUE":
            cat_label = "High Value"
        elif cat == "STRATEGIC":
            cat_label = "Strategic"
        else:
            cat_label = "Experimental"

        score_text = card.get("score", "")

        # Card title + score line (kept together as header)
        card_header = []
        card_header.append(Paragraph(
            f'#{card.get("num", "")}. {card.get("name", "")}',
            styles['CardTitle']
        ))

        # Left column: main card details
        left_items = []

        # Business outcome
        left_items.append(Paragraph(
            f'<b>Business Outcome:</b> {card.get("outcome", "")}', styles['Body']
        ))

        # Architecture
        left_items.append(Paragraph(
            f'<b>Architecture:</b> {card.get("architecture", "")}', styles['Body']
        ))

        # Tech stack
        tech = card.get("tech_stack", {})
        if tech:
            left_items.append(Paragraph("<b>Tech Stack</b>", styles['BodyBold']))
            if tech.get("n8n_nodes"):
                left_items.append(Paragraph(
                    f'<b>n8n:</b> {", ".join(tech["n8n_nodes"])}', styles['BulletItem']
                ))
            if tech.get("ai_model"):
                left_items.append(Paragraph(
                    f'<b>AI:</b> {tech["ai_model"]}', styles['BulletItem']
                ))
            if tech.get("integrations"):
                left_items.append(Paragraph(
                    f'<b>Integrations:</b> {", ".join(tech["integrations"])}', styles['BulletItem']
                ))
            if tech.get("skills"):
                left_items.append(Paragraph(
                    f'<b>Skills:</b> {", ".join(tech["skills"])}', styles['BulletItem']
                ))

        # Build time + template
        build_time = card.get("build_time", "")
        template_id = card.get("template_id")
        template_str = f"Template #{template_id}" if template_id else "Build from scratch"
        left_items.append(Spacer(1, 4))
        left_items.append(Paragraph(
            f'<b>Build Time:</b> {build_time}  |  <b>Template:</b> {template_str}',
            styles['Body']
        ))

        # Implementation steps
        steps = card.get("steps", [])
        if steps:
            left_items.append(Spacer(1, 4))
            left_items.append(Paragraph("<b>Implementation</b>", styles['BodyBold']))
            for i, step in enumerate(steps, 1):
                left_items.append(Paragraph(f"{i}. {step}", styles['BulletItem']))

        # Right column: revenue model + scores inside a callout box
        callout_content = []
        rev = card.get("revenue", {})
        if rev:
            callout_content.append(Paragraph("<b>Revenue Model</b>", styles['Callout']))
            if rev.get("setup"):
                callout_content.append(Paragraph(f'Setup: {rev["setup"]}', styles['Callout']))
            if rev.get("monthly"):
                callout_content.append(Paragraph(f'Monthly: {rev["monthly"]}', styles['Callout']))
            if rev.get("usage"):
                callout_content.append(Paragraph(f'Usage: {rev["usage"]}', styles['Callout']))
            if rev.get("tier"):
                callout_content.append(Paragraph(f'Tier: {rev["tier"]}', styles['Callout']))

        if score_text:
            scores = card.get("scores", {})
            callout_content.append(Spacer(1, 6))
            callout_content.append(Paragraph("<b>Scores</b>", styles['Callout']))
            for key in ["revenue", "impact", "feasibility", "demand", "differentiation"]:
                val = scores.get(key, 0)
                callout_content.append(Paragraph(f'{key.title()}: {val}/10', styles['Callout']))
            total = sum(scores.values())
            callout_content.append(Paragraph(f'<b>Total: {total}/50</b>', styles['Callout']))

        right_items = []
        if callout_content:
            right_items.append(make_callout_box(callout_content))
        right_items.append(Spacer(1, 8))
        right_items.append(make_pill_badge(cat_label, bg_color=cat_color))

        # Build card as: header, then two-column body, then separator
        # two-column Table is a single flowable so KeepTogether works
        card_flowables = list(card_header)
        if right_items:
            card_flowables.append(make_two_column(left_items, right_items, left_pct=0.62))
        else:
            card_flowables.extend(left_items)
        card_flowables.append(HRFlowable(
            width="100%", thickness=0.5, color=HexColor('#E0D8D0'),
            spaceAfter=12, spaceBefore=6
        ))

        # Keep entire card on one page
        story.append(KeepTogether(card_flowables))

    # ===== SOURCES =====
    story.append(PageBreak())
    story.extend(make_divider_page("Sources", DIVIDER_COLORS["sources"]))

    for s in sources:
        if ' - http' in s:
            parts = s.split(' - ', 1)
            name = parts[0]
            url = parts[1].strip()
            story.append(Paragraph(
                f'<b>{name}</b> -- <a href="{url}" color="#3366AA">{url}</a>',
                styles['BulletItem']
            ))
        elif s.startswith('http'):
            story.append(Paragraph(
                f'<a href="{s}" color="#3366AA">{s}</a>',
                styles['BulletItem']
            ))
        else:
            story.append(Paragraph(s, styles['BulletItem']))

    # ===== BRANDED CLOSING PAGE =====
    story.append(PageBreak())
    story.append(Spacer(1, 120))

    # Centered logo (larger)
    logo_path = brand_info.get("logo")
    if logo_path and Path(logo_path).exists():
        logo_img = RLImage(str(logo_path), width=72, height=72)
        logo_table = Table([[logo_img]], colWidths=[avail_w])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(logo_table)
        story.append(Spacer(1, 20))

    # Brand name centered
    story.append(Paragraph(
        brand,
        ParagraphStyle('brand_close', parent=styles['Body'],
                       fontName=FONT_SERIF, fontSize=32, leading=38,
                       textColor=TEXT_DARK, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 8))

    # Tagline centered
    tagline = brand_info.get("tagline", "")
    for line in tagline.split("\n"):
        story.append(Paragraph(
            line,
            ParagraphStyle('tagline', parent=styles['Body'],
                           fontName=FONT_SANS, fontSize=16, leading=22,
                           textColor=TEXT_BODY, spaceAfter=2, alignment=TA_CENTER)
        ))

    story.append(Spacer(1, 32))
    story.append(HRFlowable(width="30%", thickness=0.5,
                              color=HexColor('#E0D8D0'), hAlign='CENTER'))
    story.append(Spacer(1, 20))

    # Contact info centered
    email = brand_info.get("email", "")
    website = brand_info.get("website", "")
    if email:
        story.append(Paragraph(
            f'<a href="mailto:{email}" color="#3366AA">{email}</a>',
            ParagraphStyle('contact', parent=styles['Body'],
                           fontSize=12, spaceAfter=4, alignment=TA_CENTER)
        ))
    if website:
        story.append(Paragraph(
            f'<a href="https://{website}" color="#3366AA">{website}</a>',
            ParagraphStyle('contact2', parent=styles['Body'],
                           fontSize=12, spaceAfter=4, alignment=TA_CENTER)
        ))

    story.append(Spacer(1, 60))
    story.append(Paragraph(
        f"Generated by AI Automation Brainstorm  |  {smart_title(domain)}  |  {date}",
        ParagraphStyle('footer', parent=styles['Muted'], alignment=TA_CENTER)
    ))

    doc.build(story, onFirstPage=CreamBackground.draw_bg, onLaterPages=CreamBackground.draw_bg)
    print(f"PDF generated: {out_path}")

    # QA validation
    issues = validate_pdf(out_path, doc.audit_data, data)
    print("\n--- QA Validation ---")
    for level, msg in issues:
        print(f"  [{level}] {msg}")
    warn_count = sum(1 for lvl, _ in issues if lvl == "WARN")
    if warn_count:
        print(f"\n  {warn_count} warning(s) -- review PDF manually")
    else:
        print("\n  All checks passed")


if __name__ == "__main__":
    build_pdf()
