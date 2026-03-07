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
    CreamBackground, create_doc,
)

from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

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

    doc = create_doc(out_path)
    story = []

    avail_w = PAGE_W - 2 * MARGINS

    # ===== TITLE PAGE =====
    title_text = "AI Automation Brainstorm"
    subtitle_text = smart_title(domain)
    if problem_area:
        subtitle_text += f" -- {smart_title(problem_area)}"
    story.extend(make_title_page(title_text, subtitle_text, brand, date))

    # ===== TABLE OF CONTENTS =====
    story.append(Paragraph("Contents", styles['TOCTitle']))
    story.append(HRFlowable(width="50%", thickness=0.5, color=HexColor('#CCCCCC'),
                             spaceAfter=20, hAlign='LEFT'))

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
    story.append(Spacer(1, 30))
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

    # ===== PHASE 1 DIVIDER =====
    story.extend(make_divider_page(
        "Phase 1:\nSolution Discovery",
        DIVIDER_COLORS["discovery"]
    ))

    # ===== PHASE 1: DISCOVERY CONTENT =====
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
    story.append(PageBreak())

    # ===== PHASE 2 DIVIDER =====
    story.extend(make_divider_page(
        "Phase 2:\nFeasibility Matrix",
        DIVIDER_COLORS["feasibility"]
    ))

    # ===== PHASE 2: FEASIBILITY CONTENT =====
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
    story.append(PageBreak())

    # ===== PHASE 3 DIVIDER =====
    story.extend(make_divider_page(
        "Phase 3:\nAutomation Spec Cards",
        DIVIDER_COLORS["spec_cards"]
    ))

    # ===== PHASE 3: SPEC CARDS =====
    current_category = None

    for card in spec_cards:
        cat = card.get("category", "EXPERIMENTAL")
        cat_color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["EXPERIMENTAL"])

        # Category section header
        if cat != current_category:
            current_category = cat
            if cat == "QUICK WIN":
                label = "Quick Wins -- Build This Week"
            elif cat == "HIGH VALUE":
                label = "High Value -- Worth Investment"
            elif cat == "STRATEGIC":
                label = "Strategic -- Plan For"
            else:
                label = "Experimental -- Backlog"

            story.append(make_pill_badge(label, bg_color=cat_color))
            story.append(Spacer(1, 16))

        # Build card elements
        card_elements = []

        # Pill badge + score on same line
        score_text = card.get("score", "")

        # Card title (large serif)
        card_elements.append(Paragraph(
            f'#{card.get("num", "")}. {card.get("name", "")}',
            styles['CardTitle']
        ))

        # Score inline
        if score_text:
            scores = card.get("scores", {})
            score_parts = []
            for key in ["revenue", "impact", "feasibility", "demand", "differentiation"]:
                val = scores.get(key, 0)
                score_parts.append(f"{key.title()}: {val}/10")
            total = sum(scores.values())
            score_line = "  |  ".join(score_parts) + f"  |  <b>Total: {total}/50</b>"
            card_elements.append(Paragraph(score_line, styles['BodySmall']))
            card_elements.append(Spacer(1, 8))

        # Two-column layout: left = details, right = callout (revenue + scores)
        left_items = []
        right_items = []

        # Left: Business outcome
        left_items.append(Paragraph(
            f'<b>Business Outcome:</b> {card.get("outcome", "")}', styles['Body']
        ))

        # Left: Architecture
        left_items.append(Paragraph(
            f'<b>Architecture:</b> {card.get("architecture", "")}', styles['Body']
        ))

        # Left: Tech stack
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

        # Left: Build time + template
        build_time = card.get("build_time", "")
        template_id = card.get("template_id")
        template_str = f"Template #{template_id}" if template_id else "Build from scratch"
        left_items.append(Spacer(1, 4))
        left_items.append(Paragraph(
            f'<b>Build Time:</b> {build_time}  |  <b>Template:</b> {template_str}',
            styles['Body']
        ))

        # Left: Implementation steps
        steps = card.get("steps", [])
        if steps:
            left_items.append(Spacer(1, 4))
            left_items.append(Paragraph("<b>Implementation</b>", styles['BodyBold']))
            for i, step in enumerate(steps, 1):
                left_items.append(Paragraph(f"{i}. {step}", styles['BulletItem']))

        # Right: Revenue model callout box
        rev = card.get("revenue", {})
        if rev:
            callout_items = []
            callout_items.append(Paragraph("<b>Revenue Model</b>", styles['Callout']))
            if rev.get("setup"):
                callout_items.append(Paragraph(f'Setup: {rev["setup"]}', styles['Callout']))
            if rev.get("monthly"):
                callout_items.append(Paragraph(f'Monthly: {rev["monthly"]}', styles['Callout']))
            if rev.get("usage"):
                callout_items.append(Paragraph(f'Usage: {rev["usage"]}', styles['Callout']))
            if rev.get("tier"):
                callout_items.append(Paragraph(f'Tier: {rev["tier"]}', styles['Callout']))
            right_items.append(make_callout_box(callout_items))
            right_items.append(Spacer(1, 8))

        # Build two-column layout
        if right_items:
            card_elements.append(make_two_column(left_items, right_items, left_pct=0.55))
        else:
            card_elements.extend(left_items)

        card_elements.append(Spacer(1, 6))
        # Thin separator between cards
        card_elements.append(HRFlowable(
            width="100%", thickness=0.5, color=HexColor('#E0D8D0'),
            spaceAfter=16, spaceBefore=8
        ))

        story.append(KeepTogether(card_elements))

    # ===== SOURCES DIVIDER =====
    story.append(PageBreak())
    story.extend(make_divider_page("Sources", DIVIDER_COLORS["sources"]))

    # ===== SOURCES CONTENT =====
    story.append(make_pill_badge("References"))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Sources", styles['H1Serif']))
    story.append(Spacer(1, 8))

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

    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph(
        f"Generated by AI Automation Brainstorm  |  {smart_title(domain)}  |  {date}",
        ParagraphStyle('footer', parent=styles['Muted'], alignment=TA_CENTER)
    ))

    doc.build(story, onFirstPage=CreamBackground.draw_bg, onLaterPages=CreamBackground.draw_bg)
    print(f"PDF generated: {out_path}")


if __name__ == "__main__":
    build_pdf()
