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
    subtitle = domain.title()
    if problem_area:
        subtitle += f" -- {problem_area.title()}"
    story.append(Paragraph(subtitle, styles['TitleSub']))
    story.append(Paragraph(date, styles['TitleDate']))
    story.append(Spacer(1, 0.8 * inch))

    # Cost box
    cost_data = [
        [Paragraph('<b>Run Cost</b>', styles['Body']), Paragraph(f'<b>{cost}</b>', styles['Body'])],
    ]
    cost_table = Table(cost_data, colWidths=[2 * inch, 1.5 * inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT_LIGHT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cost_table)
    story.append(PageBreak())

    # ===== TABLE OF CONTENTS =====
    story.append(Paragraph("Table of Contents", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))
    toc_items = [
        "Phase 1: Solution Discovery",
        "Phase 2: Feasibility Matrix",
        "Phase 3: Automation Spec Cards",
        "    Quick Wins",
        "    High Value",
        "    Strategic",
        "    Experimental",
        "Sources",
    ]
    for item in toc_items:
        indent = 40 if item.startswith("    ") else 20
        s = ParagraphStyle('toc_tmp', parent=styles['TOCEntry'], leftIndent=indent)
        story.append(Paragraph(item.strip(), s))
    story.append(PageBreak())

    # ===== PHASE 1: DISCOVERY =====
    story.append(Paragraph("Phase 1: Solution Discovery", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))
    story.append(Paragraph(
        f"Proven AI automations for <b>{domain}</b> discovered from web, n8n templates, "
        f"tool directories, and Claude Code capabilities.",
        styles['Body']
    ))
    story.append(Spacer(1, 8))

    discoveries = data.get("discoveries", [])
    if discoveries:
        disc_table_data = [["#", "Automation / Solution", "Source", "Target Problem", "Proven?"]]
        for d in discoveries:
            disc_table_data.append([
                str(d.get("num", "")),
                d.get("name", ""),
                d.get("source", ""),
                d.get("problem", ""),
                "Yes" if d.get("proven") else "No",
            ])
        story.append(make_standard_table(
            disc_table_data,
            [0.3 * inch, 2.2 * inch, 1.2 * inch, 2 * inch, 0.5 * inch]
        ))
    story.append(PageBreak())

    # ===== PHASE 2: FEASIBILITY =====
    story.append(Paragraph("Phase 2: Feasibility Matrix", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))

    feasibility = data.get("feasibility", [])
    if feasibility:
        feas_table_data = [["#", "Automation", "Existing Skill?", "n8n Nodes?", "Stack Fit", "Build", "Status"]]
        for f in feasibility:
            feas_table_data.append([
                str(f.get("num", "")),
                f.get("name", ""),
                f.get("existing_skill", "-"),
                f.get("n8n_nodes", "-"),
                f.get("stack_fit", "-"),
                f.get("build_hours", "-"),
                f.get("feasibility", "-"),
            ])
        story.append(make_standard_table(
            feas_table_data,
            [0.3 * inch, 1.8 * inch, 1.1 * inch, 0.8 * inch, 0.7 * inch, 0.5 * inch, 0.8 * inch]
        ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Legend:</b> Ready = build today | Needs Work = missing 1-2 components | "
                           "Blocked = missing critical integration", styles['SmallMuted']))
    story.append(PageBreak())

    # ===== PHASE 3: SPEC CARDS =====
    story.append(Paragraph("Phase 3: Automation Spec Cards", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=14))

    spec_cards = data.get("spec_cards", [])
    current_category = None

    for card in spec_cards:
        cat = card.get("category", "EXPERIMENTAL")
        cat_color = CATEGORY_COLORS.get(cat, SCORE_GRAY)

        # Category banner
        if cat != current_category:
            current_category = cat
            if cat == "QUICK WIN":
                label = "QUICK WINS -- Build This Week"
            elif cat == "HIGH VALUE":
                if spec_cards.index(card) > 0:
                    story.append(PageBreak())
                label = "HIGH VALUE -- Worth Investment"
            elif cat == "STRATEGIC":
                story.append(PageBreak())
                label = "STRATEGIC -- Plan For"
            else:
                story.append(PageBreak())
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
        story.append(header_table)
        story.append(Spacer(1, 4))

        # Business outcome
        story.append(Paragraph(f'<b>Business Outcome:</b> {card.get("outcome", "")}', styles['Body']))

        # Architecture
        story.append(Paragraph(f'<b>Architecture:</b> {card.get("architecture", "")}', styles['Body']))

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
                story.append(Paragraph(f"&bull; {tp}", styles['BulletCustom']))

        # Build time + template
        build_time = card.get("build_time", "")
        template_id = card.get("template_id")
        template_str = f"Template #{template_id}" if template_id else "Build from scratch"
        story.append(Paragraph(f'<b>Build Time:</b> {build_time} | <b>Template:</b> {template_str}',
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
            story.append(Paragraph(f'<b>Revenue:</b> {" | ".join(rev_parts)}', styles['Body']))

        # Implementation steps
        steps = card.get("steps", [])
        if steps:
            story.append(Paragraph("<b>Implementation:</b>", styles['BodyBold']))
            for i, step in enumerate(steps, 1):
                story.append(Paragraph(f"{i}. {step}", styles['BulletCustom']))

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
            story.append(score_table)

        story.append(Spacer(1, 16))

    # ===== SOURCES =====
    story.append(PageBreak())
    story.append(Paragraph("Sources", styles['SectionHead']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))

    sources = data.get("sources", [])
    for s in sources:
        story.append(Paragraph(f"&bull; {s}", styles['BulletCustom']))

    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=8))
    story.append(Paragraph(
        f"Generated by AI Automation Brainstorm | {domain.title()} | {date}",
        ParagraphStyle('footer', parent=styles['SmallMuted'], alignment=TA_CENTER)
    ))

    doc.build(story)
    print(f"PDF generated: {out_path}")


if __name__ == "__main__":
    build_pdf()
