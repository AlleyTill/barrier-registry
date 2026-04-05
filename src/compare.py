"""Compare health data across US, UK, and Mexico using real WHO and CMS data."""

from src.database.models import HealthPolicy, WHOIndicator, get_session, init_db


def get_latest_indicator(session, country: str, indicator_code: str):
    """Get the most recent value for an indicator in a country."""
    result = (
        session.query(WHOIndicator)
        .filter_by(country=country, indicator_code=indicator_code)
        .order_by(WHOIndicator.year.desc())
        .first()
    )
    return result


def compare_countries():
    """Print a comparison of health indicators across US, UK, and Mexico."""
    init_db()
    session = get_session()

    countries = {
        "USA": "United States",
        "CAN": "Canada",
        "MEX": "Mexico",
    }

    indicators = {
        "UHC_INDEX_REPORTED": "Universal Health Coverage Index",
        "HWF_0001": "Doctors per 10,000 people",
        "HWF_0006": "Nurses per 10,000 people",
        "WHOSIS_000001": "Life Expectancy (years)",
        "WHS4_100": "Hospital Beds per 10,000",
        "MDG_0000000001": "Infant Mortality per 1,000 births",
        "NCD_BMI_30A": "Adult Obesity Prevalence (%)",
    }

    print("=" * 80)
    print("GLOBAL HEALTH POLICY INTELLIGENCE PLATFORM")
    print("Three-Country Comparison: US vs Canada vs Mexico")
    print("=" * 80)

    # WHO Indicators
    print("\n--- WHO HEALTH INDICATORS (Most Recent Year) ---\n")
    print(f"{'Indicator':<35} {'US':>12} {'Canada':>12} {'Mexico':>12}")
    print("-" * 71)

    for code, name in indicators.items():
        values = {}
        for country_code in countries:
            record = get_latest_indicator(session, country_code, code)
            if record:
                values[country_code] = f"{record.value:.1f} ({record.year})"
            else:
                values[country_code] = "N/A"

        print(f"{name:<35} {values['USA']:>12} {values['CAN']:>12} {values['MEX']:>12}")

    # CMS Policies (US only for now)
    print("\n--- US NATIONAL COVERAGE DETERMINATIONS (CMS) ---\n")
    us_policies = (
        session.query(HealthPolicy)
        .filter_by(country="USA", source="CMS")
        .order_by(HealthPolicy.last_updated.desc())
        .limit(10)
        .all()
    )

    print(f"Total US NCDs in database: {session.query(HealthPolicy).filter_by(country='USA', source='CMS').count()}")
    print(f"\nMost recently updated:")
    for p in us_policies:
        lab_tag = " [LAB]" if "Lab test: Yes" in (p.summary or "") else ""
        print(f"  [{p.last_updated}] {p.title}{lab_tag}")

    # Summary stats
    print("\n--- DATABASE SUMMARY ---\n")
    for country_code, country_name in countries.items():
        who_count = session.query(WHOIndicator).filter_by(country=country_code).count()
        policy_count = session.query(HealthPolicy).filter_by(country=country_code).count()
        print(f"{country_name}: {who_count} WHO indicators, {policy_count} policy records")

    total = session.query(WHOIndicator).count() + session.query(HealthPolicy).count()
    print(f"\nTotal records in database: {total}")

    session.close()


if __name__ == "__main__":
    compare_countries()
