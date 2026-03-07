#!/usr/bin/env python3
"""Generate styled PDF report for AI Automation Brainstorm.

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

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

# Colors (matching youtube-content-ideator style)
DARK_BG = HexColor('#1a1a2e')
ACCENT = HexColor('#4361ee')
ACCENT_LIGHT = HexColor('#e8ecff')
HEADER_BG = HexColor('#16213e')
ROW_ALT = HexColor('#f8f9fa')
SCORE_GREEN = HexColor('#10b981')
SCORE_YELLOW = HexColor('#f59e0b')
SCORE_BLUE = HexColor('#3b82f6')
SCORE_GRAY = HexColor('#6b7280')
BORDER_COLOR = HexColor('#dee2e6')
TEXT_DARK = HexColor('#212529')
TEXT_MUTED = HexColor('#6c757d')

CATEGORY_COLORS = {
    "QUICK WIN": SCORE_GREEN,
    "HIGH VALUE": SCORE_BLUE,
    "STRATEGIC": SCORE_YELLOW,
    "EXPERIMENTAL": SCORE_GRAY,
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
        # Try current directory
        json_path = Path("tmp/automation-brainstorm-data.json")
    if not json_path.exists():
        print(f"ERROR: Data file not found at {json_path}")
        print("Write brainstorm data to tmp/automation-brainstorm-data.json first.")
        sys.exit(1)
    with open(json_path) as f:
        return json.load(f)


def build_styles():
    """Create all custom paragraph styles."""
    styles = getSampleStyleSheet()

    style_defs = {
        'TitlePage': dict(parent='Title', fontSize=28, leading=34, textColor=DARK_BG,
                          alignment=TA_CENTER, spaceAfter=12, fontName='Helvetica-Bold'),
        'TitleSub': dict(parent='Normal', fontSize=16, leading=22, textColor=ACCENT,
                         alignment=TA_CENTER, spaceAfter=6, fontName='Helvetica'),
        'TitleDate': dict(parent='Normal', fontSize=14, leading=18, textColor=TEXT_MUTED,
                          alignment=TA_CENTER, spaceAfter=30, fontName='Helvetica'),
        'SectionHead': dict(parent='Heading1', fontSize=20, leading=26, textColor=DARK_BG,
                            spaceBefore=20, spaceAfter=10, fontName='Helvetica-Bold'),
        'SubHead': dict(parent='Heading2', fontSize=15, leading=20, textColor=HEADER_BG,
                        spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold'),
        'SubHead3': dict(parent='Heading3', fontSize=13, leading=17, textColor=ACCENT,
                         spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold'),
        'Body': dict(parent='Normal', fontSize=10, leading=14, textColor=TEXT_DARK,
                     spaceAfter=6, fontName='Helvetica'),
        'BodyBold': dict(parent='Normal', fontSize=10, leading=14, textColor=TEXT_DARK,
                         spaceAfter=6, fontName='Helvetica-Bold'),
        'BulletCustom': dict(parent='Normal', fontSize=10, leading=14, textColor=TEXT_DARK,
                             spaceAfter=3, fontName='Helvetica', leftIndent=18, bulletIndent=6),
        'CardTitle': dict(parent='Heading2', fontSize=14, leading=18, textColor=white,
                          spaceBefore=0, spaceAfter=0, fontName='Helvetica-Bold'),
        'ScoreBig': dict(parent='Normal', fontSize=22, leading=26, textColor=SCORE_GREEN,
                         alignment=TA_CENTER, fontName='Helvetica-Bold'),
        'SmallMuted': dict(parent='Normal', fontSize=8, leading=10, textColor=TEXT_MUTED,
                           fontName='Helvetica'),
        'TOCEntry': dict(parent='Normal', fontSize=11, leading=18, textColor=TEXT_DARK,
                         fontName='Helvetica', leftIndent=20),
        'CategoryLabel': dict(parent='Normal', fontSize=12, leading=16, textColor=white,
                              fontName='Helvetica-Bold', alignment=TA_CENTER),
    }

    for name, props in style_defs.items():
        parent = styles[props.pop('parent')]
        styles.add(ParagraphStyle(name, parent=parent, **props))

    return styles


def make_standard_table(data, col_widths, header_bg=HEADER_BG):
    """Create a standard table with header row and alternating rows."""
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, ROW_ALT]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


def build_pdf():
    """Build the full PDF report."""
    data = load_data()
    date = data.get("date", "Unknown")
    domain = data.get("domain", "Unknown")
    problem_area = data.get("problem_area", "")
    cost = data.get("cost", "$0.00")

    # Determine output path
    out_dir = Path.home() / "Documents" / "_projects" / "DVORKIN-2" / "tmp"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"automation-brainstorm-{date}.pdf"

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
    )

    styles = build_styles()
    story = []

    # ===== TITLE PAGE =====
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("AI AUTOMATION BRAINSTORM", styles['TitlePage']))
    story.append(HRFlowable(width="40%", thickness=3, color=ACCENT, spaceAfter=16, spaceBefore=8))
    subtitle = smart_title(domain)
    if problem_area:
        subtitle += f" -- {smart_title(problem_area)}"
    story.append(Paragraph(subtitle, styles['TitleSub']))
    story.append(Paragraph(date, styles['TitleDate']))
    story.append(Spacer(1, 0.8 * inch))

    # Summary stats box
    discoveries = data.get("discoveries", [])
    feasibility = data.get("feasibility", [])
    spec_cards = data.get("spec_cards", [])
    num_discoveries = len(discoveries)
    num_feasible = len(feasibility)
    num_cards = len(spec_cards)

    summary_header = [
        Paragraph('<b>Solutions Found</b>', styles['Body']),
        Paragraph('<b>Feasibility Checked</b>', styles['Body']),
        Paragraph('<b>Spec Cards</b>', styles['Body']),
        Paragraph('<b>Run Cost</b>', styles['Body']),
    ]
    summary_vals = [
        Paragraph(f'<b>{num_discoveries}</b>', styles['Body']),
        Paragraph(f'<b>{num_feasible}</b>', styles['Body']),
        Paragraph(f'<b>{num_cards}</b>', styles['Body']),
        Paragraph(f'<b>{cost}</b>', styles['Body']),
    ]
    summary_table = Table([summary_header, summary_vals],
                          colWidths=[1.7 * inch, 1.8 * inch, 1.3 * inch, 1.3 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('BACKGROUND', (0, 1), (-1, 1), ACCENT_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # ===== TABLE OF CONTENTS =====
    story.append(Paragraph("Table of Contents", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    # Count cards by category
    cat_counts = {}
    for card in spec_cards:
        cat = card.get("category", "EXPERIMENTAL")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    toc_items = [
        (f"Phase 1: Solution Discovery ({num_discoveries} items)", 20),
        (f"Phase 2: Feasibility Matrix ({num_feasible} items)", 20),
        (f"Phase 3: Automation Spec Cards ({num_cards} cards)", 20),
    ]
    for cat_key, cat_label in [("QUICK WIN", "Quick Wins"), ("HIGH VALUE", "High Value"),
                                ("STRATEGIC", "Strategic"), ("EXPERIMENTAL", "Experimental")]:
        count = cat_counts.get(cat_key, 0)
        if count > 0:
            toc_items.append((f"{cat_label} ({count})", 40))
    toc_items.append(("Sources", 20))

    for text, indent in toc_items:
        s = ParagraphStyle('toc_tmp', parent=styles['TOCEntry'], leftIndent=indent)
        story.append(Paragraph(text, s))

    story.append(Spacer(1, 20))

    # ===== PHASE 1: DISCOVERY =====
    story.append(Paragraph("Phase 1: Solution Discovery", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))
    story.append(Paragraph(
        f"Proven AI automations for <b>{domain}</b> discovered from web, n8n templates, "
        f"tool directories, and Claude Code capabilities.",
        styles['Body']
    ))
    story.append(Spacer(1, 8))

    if discoveries:
        cell = styles['Body']
        disc_table_data = [["#", "Automation / Solution", "Source", "Target Problem", "Proven?"]]
        for d in discoveries:
            disc_table_data.append([
                str(d.get("num", "")),
                Paragraph(d.get("name", ""), cell),
                Paragraph(d.get("source", ""), cell),
                Paragraph(d.get("problem", ""), cell),
                "Yes" if d.get("proven") else "No",
            ])
        story.append(make_standard_table(
            disc_table_data,
            [0.3 * inch, 2.3 * inch, 1.3 * inch, 2.1 * inch, 0.7 * inch]
        ))
    story.append(Spacer(1, 16))

    # ===== PHASE 2: FEASIBILITY =====
    story.append(Paragraph("Phase 2: Feasibility Matrix", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))

    if feasibility:
        cell = styles['Body']
        feas_table_data = [["#", "Automation", "Existing Skill?", "n8n Nodes?", "Stack Fit", "Build", "Status"]]
        for f in feasibility:
            feas_table_data.append([
                str(f.get("num", "")),
                Paragraph(f.get("name", ""), cell),
                Paragraph(f.get("existing_skill", "-"), cell),
                Paragraph(f.get("n8n_nodes", "-"), cell),
                f.get("stack_fit", "-"),
                f.get("build_hours", "-"),
                f.get("feasibility", "-"),
            ])
        story.append(make_standard_table(
            feas_table_data,
            [0.3 * inch, 2.0 * inch, 1.2 * inch, 1.0 * inch, 0.6 * inch, 0.5 * inch, 0.8 * inch]
        ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Legend:</b> Ready = build today | Needs Work = missing 1-2 components | "
                           "Blocked = missing critical integration", styles['SmallMuted']))
    story.append(Spacer(1, 16))

    # ===== PHASE 3: SPEC CARDS =====
    story.append(Paragraph("Phase 3: Automation Spec Cards", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=14))

    current_category = None

    for card in spec_cards:
        cat = card.get("category", "EXPERIMENTAL")
        cat_color = CATEGORY_COLORS.get(cat, SCORE_GRAY)

        # Category banner (not inside KeepTogether -- it's a section divider)
        if cat != current_category:
            current_category = cat
            if cat == "QUICK WIN":
                label = "QUICK WINS -- Build This Week"
            elif cat == "HIGH VALUE":
                label = "HIGH VALUE -- Worth Investment"
            elif cat == "STRATEGIC":
                label = "STRATEGIC -- Plan For"
            else:
                label = "EXPERIMENTAL -- Backlog"

            cat_banner = Table(
                [[Paragraph(label, styles['CategoryLabel'])]],
                colWidths=[7 * inch]
            )
            cat_banner.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), cat_color),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(cat_banner)
            story.append(Spacer(1, 12))

        # Build card elements list for KeepTogether
        card_elements = []

        # Card header bar
        header_data = [[
            Paragraph(f'#{card.get("num", "")}. {card.get("name", "")}', styles['CardTitle']),
            Paragraph(card.get("score", ""), ParagraphStyle(
                'sc', parent=styles['CardTitle'], alignment=TA_RIGHT, fontSize=16)),
        ]]
        header_table = Table(header_data, colWidths=[5.2 * inch, 1.8 * inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HEADER_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (0, -1), 10),
            ('RIGHTPADDING', (-1, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        card_elements.append(header_table)
        card_elements.append(Spacer(1, 4))

        # Business outcome
        card_elements.append(Paragraph(f'<b>Business Outcome:</b> {card.get("outcome", "")}', styles['Body']))

        # Architecture
        card_elements.append(Paragraph(f'<b>Architecture:</b> {card.get("architecture", "")}', styles['Body']))

        # Tech stack
        tech = card.get("tech_stack", {})
        if tech:
            tech_parts = []
            if tech.get("n8n_nodes"):
                tech_parts.append(f'n8n: {", ".join(tech["n8n_nodes"])}')
            if tech.get("ai_model"):
                tech_parts.append(f'AI: {tech["ai_model"]}')
            if tech.get("integrations"):
                tech_parts.append(f'Integrations: {", ".join(tech["integrations"])}')
            if tech.get("skills"):
                tech_parts.append(f'Skills: {", ".join(tech["skills"])}')
            for tp in tech_parts:
                card_elements.append(Paragraph(f"&bull; {tp}", styles['BulletCustom']))

        # Build time + template
        build_time = card.get("build_time", "")
        template_id = card.get("template_id")
        template_str = f"Template #{template_id}" if template_id else "Build from scratch"
        card_elements.append(Paragraph(f'<b>Build Time:</b> {build_time} | <b>Template:</b> {template_str}',
                               styles['Body']))

        # Revenue model
        rev = card.get("revenue", {})
        if rev:
            rev_parts = []
            if rev.get("setup"):
                rev_parts.append(f'Setup: {rev["setup"]}')
            if rev.get("monthly"):
                rev_parts.append(f'Monthly: {rev["monthly"]}')
            if rev.get("usage"):
                rev_parts.append(f'Usage: {rev["usage"]}')
            if rev.get("tier"):
                rev_parts.append(f'Tier: {rev["tier"]}')
            card_elements.append(Paragraph(f'<b>Revenue:</b> {" | ".join(rev_parts)}', styles['Body']))

        # Implementation steps
        steps = card.get("steps", [])
        if steps:
            card_elements.append(Paragraph("<b>Implementation:</b>", styles['BodyBold']))
            for i, step in enumerate(steps, 1):
                card_elements.append(Paragraph(f"{i}. {step}", styles['BulletCustom']))

        # Score breakdown table
        scores = card.get("scores", {})
        if scores:
            score_headers = ["Revenue", "Impact", "Feasibility", "Demand", "Differentiation", "Total"]
            total = sum(scores.values())
            score_vals = [
                f'{scores.get("revenue", 0)}/10',
                f'{scores.get("impact", 0)}/10',
                f'{scores.get("feasibility", 0)}/10',
                f'{scores.get("demand", 0)}/10',
                f'{scores.get("differentiation", 0)}/10',
                f'{total}/50',
            ]
            score_table = Table([score_headers, score_vals],
                                colWidths=[1 * inch, 1 * inch, 1.1 * inch, 1 * inch, 1.3 * inch, 0.8 * inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), ACCENT_LIGHT),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (-1, 1), (-1, 1), ACCENT_LIGHT),
                ('FONTNAME', (-1, 1), (-1, 1), 'Helvetica-Bold'),
            ]))
            card_elements.append(score_table)

        card_elements.append(Spacer(1, 16))

        # Wrap card in KeepTogether to prevent mid-card page breaks
        story.append(KeepTogether(card_elements))

    # ===== SOURCES =====
    story.append(PageBreak())
    story.append(Paragraph("Sources", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))

    link_style = ParagraphStyle('link', parent=styles['BulletCustom'], textColor=SCORE_BLUE)
    sources = data.get("sources", [])
    for s in sources:
        # Parse "Name - https://url" format and make URLs clickable
        if ' - http' in s:
            parts = s.split(' - ', 1)
            name = parts[0]
            url = parts[1].strip()
            story.append(Paragraph(
                f'&bull; {name} - <a href="{url}" color="blue">{url}</a>', styles['BulletCustom']))
        elif s.startswith('http'):
            story.append(Paragraph(
                f'&bull; <a href="{s}" color="blue">{s}</a>', styles['BulletCustom']))
        else:
            story.append(Paragraph(f"&bull; {s}", styles['BulletCustom']))

    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=8))
    story.append(Paragraph(
        f"Generated by AI Automation Brainstorm | {smart_title(domain)} | {date}",
        ParagraphStyle('footer', parent=styles['SmallMuted'], alignment=TA_CENTER)
    ))

    doc.build(story)
    print(f"PDF generated: {out_path}")


if __name__ == "__main__":
    build_pdf()
