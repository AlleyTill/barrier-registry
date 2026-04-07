"""Expanded Canadian healthcare policy dataset.

Adds ~25 additional Canadian healthcare policies covering areas NOT already
in the canada_seeder.py (which covers telehealth for ON/BC/AB/QC, drug regulation,
data privacy, healthcare access, medical licensing, medical devices, cross-border,
and insurance).

New categories: medical_liability, clinical_standards, health_workforce, digital_health.
Expanded: telehealth (6 missing provinces).

Research conducted April 2026. All source URLs are .gc.ca, provincial college,
or equivalent authoritative sources verified at time of writing.
"""

from datetime import datetime, timezone
from src.database.models import HealthPolicy, get_session, init_db


# ---------------------------------------------------------------------------
# Canada Expansion Policies
# ---------------------------------------------------------------------------

CAN_EXPANSION_POLICIES: list[dict] = [

    # -----------------------------------------------------------------------
    # 1. MEDICAL LIABILITY (0 records currently — critical gap for cross-border)
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canadian Medical Protective Association",
        "source_url": "https://www.cmpa-acpm.ca/en/advice-publications/browse-articles/2021/telemedicine-what-you-need-to-know",
        "category": "medical_liability",
        "title": "CMPA — Telemedicine Medico-Legal Considerations",
        "summary": (
            "CMPA guidance on medico-legal risks of telemedicine practice in Canada. "
            "Covers standard of care in virtual settings, documentation requirements, "
            "patient identification and consent, prescribing via telemedicine, and "
            "jurisdictional considerations when patient and physician are in different "
            "provinces. CMPA protection applies only when the physician is licensed "
            "in the province where the patient is located at the time of the encounter."
        ),
        "original_language": "en",
        "effective_date": "2021-01-01",
        "last_updated": "2025-06-01",
        "policy_id_external": "CMPA-TELEMEDICINE-2021",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canadian Medical Protective Association",
        "source_url": "https://www.cmpa-acpm.ca/en/membership/protection",
        "category": "medical_liability",
        "title": "CMPA — Medical Liability Protection Framework",
        "summary": (
            "Overview of CMPA's medico-legal protection for Canadian physicians. "
            "CMPA is not an insurance company — it provides discretionary assistance "
            "for medico-legal problems arising from professional practice. Protection "
            "is available only to physicians licensed and practising in Canada. Foreign-"
            "licensed physicians (e.g., US-licensed doctors treating Canadian patients "
            "via telehealth) are NOT eligible for CMPA protection. This creates a "
            "significant cross-border liability gap."
        ),
        "original_language": "en",
        "effective_date": "1901-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CMPA-PROTECTION-OVERVIEW",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canadian Medical Association",
        "source_url": "https://policybase.cma.ca/en/permalink/policy14458",
        "category": "medical_liability",
        "title": "CMA Policy — Medical Liability Reform",
        "summary": (
            "CMA policy on medical liability and malpractice in Canada. Medical "
            "malpractice in Canada is governed by provincial tort law (negligence). "
            "Unlike the US, Canada does not have a 'malpractice crisis' — CMPA fees "
            "are substantially lower than US malpractice premiums. However, cross-border "
            "practitioners face dual liability exposure: they may be sued in either "
            "jurisdiction depending on where the patient was located. No bilateral "
            "agreement exists between US and Canada on medical liability jurisdiction."
        ),
        "original_language": "en",
        "effective_date": "2018-08-01",
        "last_updated": "2024-12-01",
        "policy_id_external": "CMA-LIABILITY-REFORM",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canadian Medical Protective Association",
        "source_url": "https://www.cmpa-acpm.ca/en/advice-publications/browse-articles/2023/cross-jurisdictional-telemedicine-considerations",
        "category": "medical_liability",
        "title": "CMPA — Cross-Jurisdictional Telemedicine Liability",
        "summary": (
            "CMPA guidance on liability risks when providing telemedicine across "
            "provincial or international borders. Key points: (1) The standard of "
            "care is determined by the jurisdiction where the PATIENT is located, not "
            "the physician. (2) Regulatory colleges require the physician to be licensed "
            "where the patient is. (3) CMPA protection may not extend to care provided "
            "outside of Canada. (4) Physicians providing cross-border care should verify "
            "their liability coverage applies and consider obtaining separate coverage "
            "in the patient's jurisdiction."
        ),
        "original_language": "en",
        "effective_date": "2023-03-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CMPA-CROSS-JURISDICTIONAL-2023",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of Ontario",
        "source_url": "https://www.cpso.on.ca/Physicians/Policies-Guidance/Policies/Medical-Records",
        "category": "medical_liability",
        "title": "CPSO — Medical Records Documentation Standards",
        "summary": (
            "Ontario requirements for medical record-keeping. All patient encounters, "
            "including virtual/telehealth visits, must be documented with the same "
            "rigour as in-person visits. Records must include patient consent for "
            "virtual care, the location of the patient at time of consultation, "
            "technology used, and any limitations encountered. Failure to maintain "
            "adequate records is grounds for disciplinary action and weakens defence "
            "in malpractice claims."
        ),
        "original_language": "en",
        "effective_date": "2012-06-01",
        "last_updated": "2024-09-01",
        "policy_id_external": "CPSO-MEDICAL-RECORDS",
    },

    # -----------------------------------------------------------------------
    # 2. PROVINCIAL TELEHEALTH — Missing Provinces (SK, MB, NS, NB, PEI, NL)
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of Saskatchewan",
        "source_url": "https://www.cps.sk.ca/imis/CPSS/Legislation__ByLaws__Policies_and_Guidelines/Legislation_Content/Telemedicine_Guidelines.aspx",
        "category": "telehealth",
        "title": "CPSS (Saskatchewan) — Telemedicine Practice Guidelines",
        "summary": (
            "Saskatchewan College of Physicians and Surgeons guidelines for telemedicine. "
            "Physicians must hold a Saskatchewan licence to treat patients located in "
            "Saskatchewan via telemedicine. Guidelines cover patient consent, standard "
            "of care expectations, prescribing via telemedicine (including restrictions "
            "on controlled substances for new patients), documentation requirements, "
            "and technology standards. Saskatchewan participates in the Pan-Canadian "
            "licensure discussions but has not yet adopted a national licence."
        ),
        "original_language": "en",
        "effective_date": "2019-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CPSS-TELEMEDICINE-GUIDELINES",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of Manitoba",
        "source_url": "https://cpsm.mb.ca/assets/Standards%20of%20Practice/Standard%20of%20Practice%20Telemedicine.pdf",
        "category": "telehealth",
        "title": "CPSM (Manitoba) — Standard of Practice: Telemedicine",
        "summary": (
            "Manitoba College of Physicians and Surgeons standard of practice for "
            "telemedicine. Requires Manitoba licensure for all physicians providing "
            "telemedicine to patients in Manitoba, regardless of where the physician "
            "is physically located. Covers patient-physician relationship establishment "
            "via telemedicine, prescribing standards, follow-up care requirements, and "
            "technology privacy requirements. Manitoba Health covers virtual visits "
            "under the provincial fee schedule."
        ),
        "original_language": "en",
        "effective_date": "2020-04-01",
        "last_updated": "2024-12-01",
        "policy_id_external": "CPSM-TELEMEDICINE-STANDARD",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of Nova Scotia",
        "source_url": "https://cpsns.ns.ca/resource/telemedicine-guideline/",
        "category": "telehealth",
        "title": "CPSNS (Nova Scotia) — Telemedicine Guideline",
        "summary": (
            "Nova Scotia guideline for physicians providing medical services via "
            "telemedicine. Physicians must be registered with CPSNS to provide "
            "telemedicine to patients in Nova Scotia. The guideline addresses "
            "appropriate use of telemedicine, consent requirements, prescribing "
            "(including limitations on initial prescriptions of opioids via "
            "telemedicine), documentation, and quality assurance. Nova Scotia MSI "
            "covers synchronous audio/video telehealth visits."
        ),
        "original_language": "en",
        "effective_date": "2018-06-01",
        "last_updated": "2024-06-01",
        "policy_id_external": "CPSNS-TELEMEDICINE-GUIDELINE",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of New Brunswick",
        "source_url": "https://cpsnb.org/en/medical-act-regulations-and-guidelines/guidelines/30-telemedicine",
        "category": "telehealth",
        "title": "CPSNB (New Brunswick) — Telemedicine Guideline",
        "summary": (
            "New Brunswick guideline for telemedicine practice. Physicians must hold "
            "a New Brunswick licence to provide telemedicine services to patients "
            "located in the province. The guideline covers patient identification "
            "and authentication, informed consent, standard of care (must be equivalent "
            "to in-person care), prescribing restrictions for initial encounters, and "
            "documentation. New Brunswick Medicare covers eligible telemedicine services "
            "under the provincial health plan."
        ),
        "original_language": "en",
        "effective_date": "2017-01-01",
        "last_updated": "2024-06-01",
        "policy_id_external": "CPSNB-TELEMEDICINE-GUIDELINE",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of Prince Edward Island",
        "source_url": "https://cpspei.ca/practice-guidelines/",
        "category": "telehealth",
        "title": "CPSPEI (Prince Edward Island) — Virtual Care Practice Guidelines",
        "summary": (
            "Prince Edward Island College of Physicians and Surgeons guidelines for "
            "virtual care and telemedicine. Physicians must be registered with CPSPEI "
            "to provide virtual care to patients on PEI. Guidelines cover appropriate "
            "clinical scenarios for virtual care, consent, prescribing limitations, "
            "documentation standards, and technology requirements. Health PEI covers "
            "virtual visits under the provincial Medicare plan."
        ),
        "original_language": "en",
        "effective_date": "2020-06-01",
        "last_updated": "2024-09-01",
        "policy_id_external": "CPSPEI-VIRTUAL-CARE-GUIDELINES",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of Newfoundland and Labrador",
        "source_url": "https://www.cpsnl.ca/web/files/Telemedicine-Standard.pdf",
        "category": "telehealth",
        "title": "CPSNL (Newfoundland and Labrador) — Telemedicine Standard of Practice",
        "summary": (
            "Newfoundland and Labrador standard of practice for telemedicine. "
            "Physicians must hold a CPSNL licence to provide telemedicine to patients "
            "in the province. Standard covers patient consent, clinical appropriateness "
            "assessment, prescribing via telemedicine, documentation requirements, "
            "and privacy/security of telecommunications. MCP (Medical Care Plan) covers "
            "eligible telehealth visits. Rural/remote focus given province's geography."
        ),
        "original_language": "en",
        "effective_date": "2019-03-01",
        "last_updated": "2024-06-01",
        "policy_id_external": "CPSNL-TELEMEDICINE-STANDARD",
    },

    # -----------------------------------------------------------------------
    # 3. CLINICAL STANDARDS (0 records currently)
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canadian Task Force on Preventive Health Care",
        "source_url": "https://canadiantaskforce.ca/guidelines/published-guidelines/",
        "category": "clinical_standards",
        "title": "Canadian Task Force on Preventive Health Care — Published Guidelines",
        "summary": (
            "The CTFPHC develops evidence-based clinical practice guidelines for "
            "preventive healthcare in primary care settings across Canada. Guidelines "
            "cover screening for cancers (breast, cervical, colorectal, lung, prostate), "
            "diabetes, hypertension, depression, obesity, and other conditions. These "
            "guidelines establish the Canadian standard of care for preventive services "
            "and may differ from USPSTF recommendations in the United States, creating "
            "standard-of-care conflicts for cross-border practitioners."
        ),
        "original_language": "en",
        "effective_date": "2003-01-01",
        "last_updated": "2025-03-01",
        "policy_id_external": "CTFPHC-GUIDELINES-OVERVIEW",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Accreditation Canada / Health Standards Organization",
        "source_url": "https://healthstandards.org/standard/virtual-health/",
        "category": "clinical_standards",
        "title": "HSO CAN/HSO 83001:2025 — National Standard for Virtual Health",
        "summary": (
            "Canada's first national standard for virtual health services, developed "
            "by Health Standards Organization and published 2025. Establishes clinical, "
            "technical, and organizational requirements for virtual care delivery "
            "including telehealth, remote monitoring, and digital therapeutics. Covers "
            "clinical governance, practitioner competencies, technology requirements, "
            "patient safety, informed consent, cultural safety, and quality improvement. "
            "Adoption is voluntary but Accreditation Canada may incorporate into "
            "accreditation assessments."
        ),
        "original_language": "en",
        "effective_date": "2025-01-15",
        "last_updated": "2025-01-15",
        "policy_id_external": "HSO-83001-2025-VIRTUAL-HEALTH",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Royal College of Physicians and Surgeons of Canada",
        "source_url": "https://www.royalcollege.ca/en/canmeds/canmeds-framework.html",
        "category": "clinical_standards",
        "title": "CanMEDS Physician Competency Framework",
        "summary": (
            "The CanMEDS framework defines the competencies Canadian physicians need "
            "for effective patient care. Seven roles: Medical Expert, Communicator, "
            "Collaborator, Leader, Health Advocate, Scholar, Professional. Used for "
            "medical education, assessment, and practice standards across all Canadian "
            "medical specialties. Cross-border relevance: CanMEDS competencies differ "
            "from ACGME (US) milestones, which affects credential recognition for "
            "physicians seeking to practise across the US-Canada border."
        ),
        "original_language": "en",
        "effective_date": "2015-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "RCPSC-CANMEDS-FRAMEWORK",
    },

    # -----------------------------------------------------------------------
    # 4. HEALTH WORKFORCE (0 records currently)
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canadian Institute for Health Information",
        "source_url": "https://www.cihi.ca/en/topics/health-workforce",
        "category": "health_workforce",
        "title": "CIHI — Canada's Health Workforce Data and Trends",
        "summary": (
            "CIHI tracks health workforce supply across Canada. As of 2024: ~95,000 "
            "active physicians (physician-to-population ratio ~2.5 per 1,000). "
            "Approximately 6.5 million Canadians lack a regular family doctor. "
            "Significant rural/remote shortages drive telehealth adoption. Provincial "
            "variation is substantial — Ontario, BC, and Quebec have the most physicians "
            "per capita while Atlantic provinces face acute shortages. Cross-border "
            "relevance: workforce shortages increase demand for cross-border telehealth "
            "from US specialists."
        ),
        "original_language": "en",
        "effective_date": "2024-01-01",
        "last_updated": "2025-03-01",
        "policy_id_external": "CIHI-HEALTH-WORKFORCE-2024",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Federation of Medical Regulatory Authorities of Canada",
        "source_url": "https://fmrac.ca/pan-canadian-licensure/",
        "category": "health_workforce",
        "title": "FMRAC — Pan-Canadian Medical Licensure Initiative",
        "summary": (
            "FMRAC initiative to enable physicians to practise across provincial "
            "boundaries without needing separate licences. As of 2025, not yet fully "
            "implemented — provinces retain individual licensing authority. The initiative "
            "would reduce barriers to interprovincial telehealth and help address "
            "workforce shortages in underserved provinces. Currently, a physician "
            "licensed in Ontario cannot treat a patient in Alberta via telehealth "
            "without an Alberta licence. This fragmentation is a major barrier for "
            "both interprovincial and international telehealth."
        ),
        "original_language": "en",
        "effective_date": "2021-06-01",
        "last_updated": "2025-06-01",
        "policy_id_external": "FMRAC-PAN-CANADIAN-LICENSURE",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Government of Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/health-care-system/health-human-resources/strategy/international-medical-graduates.html",
        "category": "health_workforce",
        "title": "Health Canada — International Medical Graduate (IMG) Integration",
        "summary": (
            "Federal and provincial programs for integrating internationally trained "
            "physicians into the Canadian healthcare system. IMGs face multiple barriers: "
            "credential assessment via MCC (Medical Council of Canada), residency "
            "requirements, provincial licensing exams, and limited residency positions. "
            "US-trained physicians must complete MCC evaluations unless covered by "
            "specific provincial agreements. The process typically takes 2-5 years, "
            "which is a significant barrier to cross-border physician mobility."
        ),
        "original_language": "en",
        "effective_date": "2023-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "HC-IMG-INTEGRATION",
    },

    # -----------------------------------------------------------------------
    # 5. DIGITAL HEALTH (0 records currently)
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canada Health Infoway",
        "source_url": "https://www.infoway-inforoute.ca/en/what-we-do",
        "category": "digital_health",
        "title": "Canada Health Infoway — National Digital Health Strategy",
        "summary": (
            "Canada Health Infoway is a federally funded, independent not-for-profit "
            "that works with provinces/territories to accelerate digital health "
            "adoption. Key initiatives: pan-Canadian health data interoperability, "
            "virtual care platform standards, patient access to digital health records, "
            "and AI readiness. Infoway co-invests with provinces on digital health "
            "infrastructure. Cross-border relevance: Canadian digital health standards "
            "(e.g., FHIR adoption timeline, patient portal requirements) differ from "
            "US ONC standards, creating interoperability barriers."
        ),
        "original_language": "en",
        "effective_date": "2001-01-01",
        "last_updated": "2025-06-01",
        "policy_id_external": "CHI-DIGITAL-HEALTH-STRATEGY",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Government of Canada",
        "source_url": "https://www.canada.ca/en/public-health/corporate/mandate/about-agency/external-advisory-bodies/list/pan-canadian-health-data-strategy.html",
        "category": "digital_health",
        "title": "Pan-Canadian Health Data Strategy",
        "summary": (
            "Federal-provincial-territorial strategy for modernizing Canada's health "
            "data infrastructure. Goals include: common data standards across provinces, "
            "patient-controlled data sharing, population health analytics, and privacy-"
            "preserving data linkage. The strategy acknowledges that Canada's fragmented "
            "health data systems (each province maintains separate EHR systems) create "
            "barriers to coordinated care, especially for patients who move between "
            "provinces or seek cross-border care."
        ),
        "original_language": "en",
        "effective_date": "2022-05-01",
        "last_updated": "2025-03-01",
        "policy_id_external": "PCHDS-STRATEGY",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Government of Canada",
        "source_url": "https://ised-isde.canada.ca/site/innovation-better-canada/en/artificial-intelligence-and-data-act",
        "category": "digital_health",
        "title": "Artificial Intelligence and Data Act (AIDA) — Bill C-27",
        "summary": (
            "Proposed federal legislation (Part 3 of the Digital Charter Implementation "
            "Act, 2022) to regulate AI systems in Canada. Would establish requirements "
            "for 'high-impact' AI systems including those used in healthcare: impact "
            "assessments, transparency obligations, algorithmic bias monitoring, and "
            "penalties for non-compliance. As of 2025, AIDA has not yet received Royal "
            "Assent. Cross-border relevance: AIDA's requirements would differ from "
            "US state-level AI regulations (e.g., Colorado AI Act), creating compliance "
            "complexity for cross-border health AI tools."
        ),
        "original_language": "en",
        "effective_date": "2022-06-16",
        "last_updated": "2025-06-01",
        "policy_id_external": "AIDA-BILL-C27",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canadian Medical Association",
        "source_url": "https://www.cma.ca/our-focus/digital-health/virtual-care",
        "category": "digital_health",
        "title": "CMA — Guiding Principles for Virtual Care in Canada",
        "summary": (
            "CMA principles for the equitable and effective implementation of virtual "
            "care across Canada. Principles cover: patient choice, clinical "
            "appropriateness, continuity of care, equitable access (addressing digital "
            "divide in rural/Indigenous communities), provider compensation parity "
            "with in-person visits, interoperability of virtual care platforms, and "
            "data governance. CMA advocates for pan-Canadian virtual care licensure "
            "to remove interprovincial barriers."
        ),
        "original_language": "en",
        "effective_date": "2020-02-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CMA-VIRTUAL-CARE-PRINCIPLES",
    },
]


# ---------------------------------------------------------------------------
# Seeder function
# ---------------------------------------------------------------------------

def seed_canada_expansion():
    """Seed expanded Canada policies into the database."""
    init_db()
    session = get_session()
    stored = 0
    skipped = 0

    for policy_data in CAN_EXPANSION_POLICIES:
        ext_id = policy_data.get("policy_id_external", "")
        if ext_id:
            existing = session.query(HealthPolicy).filter_by(
                country="CAN",
                policy_id_external=ext_id,
            ).first()
            if existing:
                skipped += 1
                continue

        policy = HealthPolicy(
            country=policy_data["country"],
            country_name=policy_data["country_name"],
            source=policy_data["source"],
            source_url=policy_data.get("source_url"),
            category=policy_data.get("category"),
            title=policy_data["title"],
            summary=policy_data.get("summary"),
            original_language=policy_data.get("original_language", "en"),
            effective_date=policy_data.get("effective_date"),
            last_updated=policy_data.get("last_updated"),
            fetched_at=datetime.now(timezone.utc),
            policy_id_external=ext_id or None,
        )
        session.add(policy)
        stored += 1

    session.commit()
    session.close()

    print(f"Canada Expansion Seeder complete.")
    print(f"  Stored: {stored} new policies")
    print(f"  Skipped: {skipped} duplicates")
    print(f"  Total in expansion dataset: {len(CAN_EXPANSION_POLICIES)}")


if __name__ == "__main__":
    seed_canada_expansion()
