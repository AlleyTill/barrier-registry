"""Fetch health indicators from WHO Global Health Observatory OData API."""

import httpx
from datetime import datetime, timezone
from src.database.models import WHOIndicator, get_session, init_db

WHO_API_BASE = "https://ghoapi.azureedge.net/api"

# Key health system indicators relevant to telehealth and healthcare access
INDICATORS = {
    "UHC_INDEX_REPORTED": "Universal Health Coverage Index",
    "CHE_GDPCHE": "Current Health Expenditure (% of GDP)",
    "HWF_0001": "Medical Doctors (per 10,000 population)",
    "HWF_0006": "Nursing and Midwifery Personnel (per 10,000 population)",
    "MDG_0000000001": "Infant Mortality Rate (per 1,000 live births)",
    "WHOSIS_000001": "Life Expectancy at Birth (years)",
    "NCD_BMI_30A": "Prevalence of Obesity Among Adults",
    "WHS4_100": "Hospital Beds (per 10,000 population)",
    "MDG_0000000026": "Births Attended by Skilled Health Personnel (%)",
    "WHS7_156": "Population with Household Expenditures on Health > 10% of Total",
}

# ISO 3166-1 alpha-3 codes
COUNTRIES = {
    "USA": "United States of America",
    "GBR": "United Kingdom of Great Britain and Northern Ireland",
    "MEX": "Mexico",
}


def fetch_indicator(indicator_code: str, country_code: str) -> list[dict]:
    """Fetch a single indicator for a single country from WHO API."""
    url = f"{WHO_API_BASE}/{indicator_code}?$filter=SpatialDim eq '{country_code}'"
    try:
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("value", [])
    except Exception as e:
        print(f"  Error fetching {indicator_code} for {country_code}: {e}")
        return []


def fetch_all_indicators():
    """Fetch all indicators for all countries and store in database."""
    init_db()
    session = get_session()

    total_stored = 0

    for country_code, country_name in COUNTRIES.items():
        print(f"\nFetching data for {country_name} ({country_code})...")

        for indicator_code, indicator_name in INDICATORS.items():
            print(f"  {indicator_name}...", end=" ")
            records = fetch_indicator(indicator_code, country_code)

            count = 0
            for record in records:
                value = record.get("NumericValue")
                if value is None:
                    continue

                year = record.get("TimeDim")
                if year:
                    try:
                        year = int(year)
                    except ValueError:
                        year = None

                indicator = WHOIndicator(
                    country=country_code,
                    country_name=country_name,
                    indicator_code=indicator_code,
                    indicator_name=indicator_name,
                    year=year,
                    value=float(value),
                    value_type=record.get("TimeDimensionValue", "numeric"),
                    fetched_at=datetime.now(timezone.utc),
                )
                session.add(indicator)
                count += 1

            print(f"{count} records")
            total_stored += count

    session.commit()
    session.close()
    print(f"\nDone! Stored {total_stored} WHO indicator records.")


if __name__ == "__main__":
    fetch_all_indicators()
