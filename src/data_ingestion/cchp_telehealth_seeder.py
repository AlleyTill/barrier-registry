"""Seed US federal and state-level telehealth policies from CCHP and official sources."""

from datetime import datetime, timezone
from src.database.models import HealthPolicy, get_session, init_db

# Federal telehealth policies (verified via web search, current as of April 2026)
FEDERAL_POLICIES = [
    {
        "title": "Medicare Telehealth Flexibilities Extension (Consolidated Appropriations Act 2026)",
        "summary": "Congress extended Medicare telehealth flexibilities through Dec 31, 2027 via H.R. 7148 (signed Feb 3, 2026). Includes waiving in-person requirements for behavioral telehealth, allowing home as originating site, geographic waivers, and expanded clinician eligibility.",
        "source": "Congress / CMS",
        "source_url": "https://telehealth.hhs.gov/providers/telehealth-policy/telehealth-policy-updates",
        "category": "telehealth",
        "policy_id_external": "FED-MEDICARE-TELEHEALTH-2026",
        "effective_date": "02/03/2026",
        "last_updated": "02/03/2026",
    },
    {
        "title": "DEA/HHS Telemedicine Controlled Substances Prescribing Extension (4th Temporary Rule)",
        "summary": "DEA and HHS extended telehealth flexibilities for prescribing Schedule II-V controlled substances through Dec 31, 2026. All DEA-registered providers may prescribe via telehealth regardless of when provider-patient relationship was formed. Gives time to finalize permanent Special Registration for Telemedicine.",
        "source": "DEA / HHS",
        "source_url": "https://www.hhs.gov/press-room/dea-telemedicine-extension-2026.html",
        "category": "telehealth",
        "policy_id_external": "FED-DEA-TELEHEALTH-2026",
        "effective_date": "12/31/2025",
        "last_updated": "12/30/2025",
    },
    {
        "title": "CONNECT for Health Act (Proposed)",
        "summary": "Proposed federal legislation to make Medicare telehealth flexibilities permanent, removing geographic and originating site restrictions. Would eliminate the need for recurring temporary extensions attached to must-pass funding bills. Status: proposed, not yet enacted.",
        "source": "Congress (Proposed)",
        "source_url": "https://telehealth.org/news/federal-telehealth-policy-in-2026-what-the-medicare-extensions-mean/",
        "category": "telehealth",
        "policy_id_external": "FED-CONNECT-HEALTH-ACT",
        "effective_date": "",
        "last_updated": "01/08/2026",
    },
    {
        "title": "Ryan Haight Online Pharmacy Consumer Protection Act",
        "summary": "Federal law requiring at least one in-person evaluation before prescribing controlled substances online. COVID-era telehealth flexibilities have temporarily waived this requirement. The DEA Special Registration for Telemedicine (pending) would create a permanent pathway around this requirement for qualified providers.",
        "source": "DEA",
        "source_url": "https://www.federalregister.gov/documents/2025/12/31/2025-24123/fourth-temporary-extension-of-covid-19-telemedicine-flexibilities-for-prescription-of-controlled",
        "category": "telehealth",
        "policy_id_external": "FED-RYAN-HAIGHT-ACT",
        "effective_date": "10/15/2008",
        "last_updated": "12/31/2025",
    },
    {
        "title": "Interstate Medical Licensure Compact (IMLC)",
        "summary": "42 states plus DC and Guam participate in the IMLC, which provides an expedited pathway for physicians to obtain licenses in multiple states. Hawaii and Vermont are members but not States of Principal Licensure. Arkansas, New Mexico, and Rhode Island have passed legislation but implementation is pending. Critical enabler for cross-state telehealth.",
        "source": "IMLC",
        "source_url": "https://imlcc.com/participating-states/",
        "category": "medical_licensing",
        "policy_id_external": "FED-IMLC-COMPACT-2026",
        "effective_date": "01/01/2026",
        "last_updated": "01/01/2026",
    },
    {
        "title": "HIPAA Privacy Rule and Telehealth",
        "summary": "HIPAA requires covered entities to protect patient health information during telehealth encounters. Providers must use HIPAA-compliant communication platforms. The OCR enforcement discretion for non-compliant platforms (issued during COVID) has expired; providers must now use fully compliant technology.",
        "source": "HHS OCR",
        "source_url": "https://telehealth.hhs.gov/providers/telehealth-policy",
        "category": "data_privacy",
        "policy_id_external": "FED-HIPAA-TELEHEALTH",
        "effective_date": "04/14/2003",
        "last_updated": "2025",
    },
]

# State telehealth policies (from CCHP Fall 2025 report and web research)
# Organized by key policy dimensions across all states
STATE_POLICIES = [
    # --- PARITY LAWS (24 states + territories have payment parity) ---
    {
        "title": "Telehealth Payment Parity Laws — National Summary",
        "summary": "As of Fall 2025, 44 states plus DC, Puerto Rico, and Virgin Islands have laws addressing private payer telehealth reimbursement. 24 states and Puerto Rico require payment parity (same rate as in-person). All 50 states and DC provide some form of Medicaid reimbursement for telehealth.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/topic/parity/",
        "category": "telehealth",
        "policy_id_external": "STATE-PARITY-NATIONAL-SUMMARY",
        "effective_date": "10/01/2025",
        "last_updated": "10/01/2025",
    },
    # Individual state highlights
    {
        "title": "California — Telehealth Advancement Act (AB 32)",
        "summary": "California requires health plans and insurers to cover telehealth services on the same basis as in-person services. Medi-Cal (Medicaid) covers telehealth including audio-only. No geographic or originating site restrictions for Medi-Cal telehealth.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/california/",
        "category": "telehealth",
        "policy_id_external": "STATE-CA-TELEHEALTH",
        "effective_date": "01/01/2022",
        "last_updated": "2025",
    },
    {
        "title": "Texas — Telehealth Medicaid and Private Payer Coverage",
        "summary": "Texas Medicaid covers telehealth services including live video and store-and-forward. Private payers must provide coverage for telehealth but are not required to reimburse at the same rate as in-person (no payment parity). Texas requires an existing provider-patient relationship or initial video visit.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/texas/",
        "category": "telehealth",
        "policy_id_external": "STATE-TX-TELEHEALTH",
        "effective_date": "2019",
        "last_updated": "2025",
    },
    {
        "title": "New York — Telehealth Coverage and Payment Parity",
        "summary": "New York requires commercial insurers to cover telehealth services and reimburse at the same rate as in-person care (payment parity). Medicaid covers telehealth broadly including behavioral health, primary care, and specialty services. Audio-only telephone services are covered under Medicaid.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/new-york/",
        "category": "telehealth",
        "policy_id_external": "STATE-NY-TELEHEALTH",
        "effective_date": "2020",
        "last_updated": "2025",
    },
    {
        "title": "Florida — Telehealth Provider Registration and Coverage",
        "summary": "Florida requires out-of-state telehealth providers to register with the state before providing services. Medicaid covers telehealth services. Private payer coverage is required but no payment parity mandate. Florida was among the first states to create a telehealth provider registration pathway.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/florida/",
        "category": "telehealth",
        "policy_id_external": "STATE-FL-TELEHEALTH",
        "effective_date": "2019",
        "last_updated": "2025",
    },
    {
        "title": "New Jersey — Telehealth Payment Parity Extension Through 2026",
        "summary": "New Jersey extended its telehealth payment parity requirements through July 1, 2026. Commercial insurers must reimburse telehealth at the same rate as in-person services. Medicaid covers telehealth including audio-only services.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/new-jersey/",
        "category": "telehealth",
        "policy_id_external": "STATE-NJ-TELEHEALTH",
        "effective_date": "2020",
        "last_updated": "2026",
    },
    {
        "title": "New Mexico — Expanded Telehealth Act",
        "summary": "New Mexico broadened its Telehealth Act, expanding the definition of eligible providers and encouraging both commercial insurers and Medicaid to incorporate telehealth coverage. Includes provisions for behavioral health and rural access.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/new-mexico/",
        "category": "telehealth",
        "policy_id_external": "STATE-NM-TELEHEALTH",
        "effective_date": "2025",
        "last_updated": "2025",
    },
    {
        "title": "Mississippi — Permanent Private Payer Telehealth Coverage",
        "summary": "Mississippi made its private payer telehealth coverage law permanent by removing the scheduled repeal date. Insurers must provide coverage for services delivered via telehealth. Medicaid covers telehealth including live video.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/mississippi/",
        "category": "telehealth",
        "policy_id_external": "STATE-MS-TELEHEALTH",
        "effective_date": "2025",
        "last_updated": "2025",
    },
    {
        "title": "Maryland — Permanent Private Payer Telehealth Coverage",
        "summary": "Maryland made its private payer telehealth coverage law permanent by removing the scheduled repeal date. Requires coverage parity for telehealth services. Maryland Medicaid covers a broad range of telehealth services including behavioral health and chronic disease management.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/maryland/",
        "category": "telehealth",
        "policy_id_external": "STATE-MD-TELEHEALTH",
        "effective_date": "2025",
        "last_updated": "2025",
    },
    {
        "title": "Colorado — Telehealth Coverage and Behavioral Health",
        "summary": "Colorado requires private payers to cover telehealth services. Strong behavioral health telehealth provisions. Medicaid covers telehealth broadly. Colorado participates in the Psychology Interjurisdictional Compact (PSYPACT) for cross-state behavioral health.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/colorado/",
        "category": "telehealth",
        "policy_id_external": "STATE-CO-TELEHEALTH",
        "effective_date": "2020",
        "last_updated": "2025",
    },
    {
        "title": "Illinois — Telehealth Coverage and Payment Parity",
        "summary": "Illinois requires commercial insurers to cover and reimburse telehealth services at the same rate as in-person care. Medicaid covers telehealth including audio-only. Illinois has expansive provider eligibility for telehealth services.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/illinois/",
        "category": "telehealth",
        "policy_id_external": "STATE-IL-TELEHEALTH",
        "effective_date": "2020",
        "last_updated": "2025",
    },
    # --- AUDIO-ONLY POLICIES ---
    {
        "title": "Audio-Only Telehealth Coverage — National Summary",
        "summary": "Most state Medicaid programs now cover audio-only (telephone) telehealth services, a major expansion from pre-pandemic policy. Coverage varies by state: some limit audio-only to behavioral health, others allow it broadly. Private payer audio-only requirements vary widely.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/all-telehealth-policies/",
        "category": "telehealth",
        "policy_id_external": "STATE-AUDIO-ONLY-SUMMARY",
        "effective_date": "2025",
        "last_updated": "10/01/2025",
    },
    # --- CROSS-STATE LICENSING ---
    {
        "title": "IMLC Non-Member States — Licensing Barriers for Telehealth",
        "summary": "8 states have not joined the IMLC as of 2026: California, Massachusetts, New York, New Jersey, Connecticut, Alaska, Florida, and Oregon (plus some with pending implementation). Providers must obtain individual state licenses to practice telehealth in these states, creating significant barriers to cross-state telehealth.",
        "source": "IMLC / CCHP",
        "source_url": "https://imlcc.com/participating-states/",
        "category": "medical_licensing",
        "policy_id_external": "STATE-IMLC-NONMEMBER",
        "effective_date": "01/01/2026",
        "last_updated": "01/01/2026",
    },
    # --- PRESCRIBING ---
    {
        "title": "State Telehealth Prescribing Requirements — National Summary",
        "summary": "States vary significantly on telehealth prescribing rules. Some require an initial in-person visit before prescribing, others allow prescribing after a video-only encounter, and some permit audio-only prescribing for non-controlled substances. Controlled substance prescribing is further governed by the federal Ryan Haight Act and DEA temporary flexibilities.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/all-telehealth-policies/",
        "category": "telehealth",
        "policy_id_external": "STATE-PRESCRIBING-SUMMARY",
        "effective_date": "2025",
        "last_updated": "10/01/2025",
    },
    # --- STORE AND FORWARD ---
    {
        "title": "Store-and-Forward Telehealth Coverage — National Summary",
        "summary": "Store-and-forward (asynchronous) telehealth involves transmitting recorded health data (images, video, text) for review by a provider at a later time. Common in dermatology, radiology, and ophthalmology. Coverage varies widely: some states cover under Medicaid, many have no specific store-and-forward mandate for private payers.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/all-telehealth-policies/",
        "category": "telehealth",
        "policy_id_external": "STATE-STORE-FORWARD-SUMMARY",
        "effective_date": "2025",
        "last_updated": "10/01/2025",
    },
    # --- REMOTE PATIENT MONITORING ---
    {
        "title": "Remote Patient Monitoring (RPM) Coverage — National Summary",
        "summary": "Remote Patient Monitoring uses digital devices to collect and transmit patient health data to providers. Medicare covers RPM under specific CPT codes. State Medicaid coverage of RPM is growing but uneven. RPM is increasingly important for chronic disease management and post-surgical follow-up in telehealth programs.",
        "source": "CCHP",
        "source_url": "https://www.cchpca.org/all-telehealth-policies/",
        "category": "telehealth",
        "policy_id_external": "STATE-RPM-SUMMARY",
        "effective_date": "2025",
        "last_updated": "10/01/2025",
    },
]


def seed_telehealth_policies():
    """Seed federal and state telehealth policies into the database."""
    init_db()
    session = get_session()

    all_policies = FEDERAL_POLICIES + STATE_POLICIES
    stored = 0
    skipped = 0

    for p in all_policies:
        existing = session.query(HealthPolicy).filter_by(
            country="USA",
            policy_id_external=p["policy_id_external"],
        ).first()

        if existing:
            skipped += 1
            continue

        policy = HealthPolicy(
            country="USA",
            country_name="United States",
            source=p["source"],
            source_url=p["source_url"],
            category=p["category"],
            title=p["title"],
            summary=p["summary"],
            effective_date=p.get("effective_date", ""),
            last_updated=p.get("last_updated", ""),
            fetched_at=datetime.now(timezone.utc),
            policy_id_external=p["policy_id_external"],
            original_language="en",
        )
        session.add(policy)
        stored += 1

    session.commit()
    session.close()
    print(f"Telehealth Policy Seeder complete.")
    print(f"  Stored: {stored} new policies")
    print(f"  Skipped: {skipped} duplicates")
    print(f"  Federal: {len(FEDERAL_POLICIES)} policies")
    print(f"  State: {len(STATE_POLICIES)} policies")


if __name__ == "__main__":
    seed_telehealth_policies()
