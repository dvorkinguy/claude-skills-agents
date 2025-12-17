#!/usr/bin/env python3
"""
AI Agent ROI Calculator

Usage:
    python roi_calculator.py --hours 20 --rate 75 --errors 10 --error-cost 100 --investment 697
"""

import argparse
import json


def calculate_roi(
    hours_saved_weekly: float,
    hourly_rate: float,
    errors_per_month: int = 0,
    error_cost: float = 0,
    monthly_investment: float = 0,
    revenue_leads_monthly: int = 0,
    conversion_rate: float = 0,
    deal_value: float = 0,
) -> dict:
    """Calculate ROI for an AI agent implementation."""

    # Time savings
    monthly_hours_saved = hours_saved_weekly * 4.33  # avg weeks/month
    annual_hours_saved = hours_saved_weekly * 52
    time_value_monthly = monthly_hours_saved * hourly_rate
    time_value_annual = annual_hours_saved * hourly_rate

    # Error reduction (assume 90% reduction)
    error_reduction_rate = 0.90
    errors_eliminated = errors_per_month * error_reduction_rate
    error_savings_monthly = errors_eliminated * error_cost
    error_savings_annual = error_savings_monthly * 12

    # Revenue increase
    new_customers_monthly = revenue_leads_monthly * (conversion_rate / 100)
    revenue_increase_monthly = new_customers_monthly * deal_value
    revenue_increase_annual = revenue_increase_monthly * 12

    # Total value
    total_monthly_value = time_value_monthly + error_savings_monthly + revenue_increase_monthly
    total_annual_value = time_value_annual + error_savings_annual + revenue_increase_annual

    # ROI calculations
    annual_investment = monthly_investment * 12
    net_annual_benefit = total_annual_value - annual_investment
    roi_percentage = ((total_annual_value - annual_investment) / annual_investment * 100) if annual_investment > 0 else 0
    payback_days = (monthly_investment / (total_monthly_value / 30)) if total_monthly_value > 0 else float('inf')

    return {
        "time_savings": {
            "hours_saved_weekly": hours_saved_weekly,
            "hours_saved_annually": annual_hours_saved,
            "value_monthly": round(time_value_monthly, 2),
            "value_annual": round(time_value_annual, 2),
        },
        "error_reduction": {
            "errors_eliminated_monthly": round(errors_eliminated, 1),
            "savings_monthly": round(error_savings_monthly, 2),
            "savings_annual": round(error_savings_annual, 2),
        },
        "revenue_increase": {
            "new_customers_monthly": round(new_customers_monthly, 1),
            "revenue_monthly": round(revenue_increase_monthly, 2),
            "revenue_annual": round(revenue_increase_annual, 2),
        },
        "totals": {
            "value_monthly": round(total_monthly_value, 2),
            "value_annual": round(total_annual_value, 2),
            "investment_monthly": monthly_investment,
            "investment_annual": annual_investment,
            "net_benefit_annual": round(net_annual_benefit, 2),
            "roi_percentage": round(roi_percentage, 1),
            "payback_days": round(payback_days, 1) if payback_days != float('inf') else "N/A",
        },
    }


def format_output(results: dict) -> str:
    """Format results for terminal output."""
    output = []
    output.append("\n" + "=" * 50)
    output.append("           AI AGENT ROI ANALYSIS")
    output.append("=" * 50)

    output.append("\n📊 TIME SAVINGS")
    output.append(f"   Hours saved weekly:    {results['time_savings']['hours_saved_weekly']}")
    output.append(f"   Hours saved annually:  {results['time_savings']['hours_saved_annually']:,}")
    output.append(f"   Monthly value:         ${results['time_savings']['value_monthly']:,.2f}")
    output.append(f"   Annual value:          ${results['time_savings']['value_annual']:,.2f}")

    if results['error_reduction']['savings_monthly'] > 0:
        output.append("\n🛡️ ERROR REDUCTION")
        output.append(f"   Errors eliminated/mo:  {results['error_reduction']['errors_eliminated_monthly']}")
        output.append(f"   Monthly savings:       ${results['error_reduction']['savings_monthly']:,.2f}")
        output.append(f"   Annual savings:        ${results['error_reduction']['savings_annual']:,.2f}")

    if results['revenue_increase']['revenue_monthly'] > 0:
        output.append("\n💰 REVENUE INCREASE")
        output.append(f"   New customers/mo:      {results['revenue_increase']['new_customers_monthly']}")
        output.append(f"   Monthly revenue:       ${results['revenue_increase']['revenue_monthly']:,.2f}")
        output.append(f"   Annual revenue:        ${results['revenue_increase']['revenue_annual']:,.2f}")

    output.append("\n" + "-" * 50)
    output.append("📈 SUMMARY")
    output.append(f"   Total value created:   ${results['totals']['value_annual']:,.2f}/year")
    output.append(f"   Investment:            ${results['totals']['investment_annual']:,.2f}/year")
    output.append(f"   Net benefit:           ${results['totals']['net_benefit_annual']:,.2f}/year")
    output.append(f"   ROI:                   {results['totals']['roi_percentage']}%")
    output.append(f"   Payback period:        {results['totals']['payback_days']} days")
    output.append("=" * 50 + "\n")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Calculate ROI for AI agent implementation")
    parser.add_argument("--hours", type=float, required=True, help="Hours saved per week")
    parser.add_argument("--rate", type=float, required=True, help="Hourly rate (fully loaded)")
    parser.add_argument("--errors", type=int, default=0, help="Errors per month (before)")
    parser.add_argument("--error-cost", type=float, default=0, help="Cost per error")
    parser.add_argument("--investment", type=float, default=0, help="Monthly investment/price")
    parser.add_argument("--leads", type=int, default=0, help="Additional leads per month")
    parser.add_argument("--conversion", type=float, default=0, help="Conversion rate (%)")
    parser.add_argument("--deal-value", type=float, default=0, help="Average deal value")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    results = calculate_roi(
        hours_saved_weekly=args.hours,
        hourly_rate=args.rate,
        errors_per_month=args.errors,
        error_cost=args.error_cost,
        monthly_investment=args.investment,
        revenue_leads_monthly=args.leads,
        conversion_rate=args.conversion,
        deal_value=args.deal_value,
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_output(results))


if __name__ == "__main__":
    main()
