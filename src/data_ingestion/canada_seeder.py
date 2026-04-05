"""Seed the database with curated Canadian (CAN) healthcare policies and regulations.

Each record represents a real, verifiable healthcare policy or regulation
with actual source URLs. Research conducted April 2026.

Covers:
  - Canada Health Act (federal framework)
  - Provincial telehealth regulations (ON, BC, AB, QC)
  - Health Canada drug & medical device regulations
  - Federal and provincial health privacy laws (PIPEDA, PHIPA, HIA, etc.)
  - Medical licensing (provincial colleges, pan-Canadian initiatives)
  - Cross-border healthcare with the US
  - CMA virtual care guidelines & national virtual care standard
  - Controlled substances prescribing via telehealth
  - Digital health / AI in healthcare
  - USMCA implications for healthcare
  - Provincial formulary differences
  - Connected Care for Canadians Act (Bill S-5)
"""

from datetime import datetime, timezone
from src.database.models import HealthPolicy, get_session, init_db


# ---------------------------------------------------------------------------
# Canadian Healthcare Policies Dataset
# ---------------------------------------------------------------------------

CANADA_POLICIES: list[dict] = [

    # -----------------------------------------------------------------------
    # 1. CANADA HEALTH ACT — Federal Framework
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Justice Laws Website",
        "source_url": "https://laws-lois.justice.gc.ca/eng/acts/c-6/",
        "category": "healthcare_access",
        "title": "Canada Health Act (R.S.C., 1985, c. C-6)",
        "summary": (
            "Canada's federal legislation for publicly funded health care insurance. "
            "It sets out the criteria and conditions provinces and territories must meet "
            "to receive federal health transfer payments, requiring that insured health "
            "services be administered publicly, comprehensive, universal, portable across "
            "provinces, and accessible without financial barriers."
        ),
        "original_language": "en",
        "effective_date": "1984-04-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-RSC-1985-C6",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/health-care-system/canada-health-care-system-medicare/canada-health-act.html",
        "category": "healthcare_access",
        "title": "About the Canada Health Act — Health Canada Overview",
        "summary": (
            "Health Canada's reference page explaining the five principles of the "
            "Canada Health Act: public administration, comprehensiveness, universality, "
            "portability, and accessibility. It describes how the federal government "
            "monitors provincial compliance and the conditions for Canada Health Transfer "
            "payments."
        ),
        "original_language": "en",
        "effective_date": "1984-04-01",
        "last_updated": "2025-06-01",
        "policy_id_external": "CAN-HC-CHA-ABOUT",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/publications/health-system-services/canada-health-act-annual-report-2024-2025.html",
        "category": "healthcare_access",
        "title": "Canada Health Act Annual Report 2024-2025",
        "summary": (
            "Annual report to Parliament on the administration of the Canada Health Act. "
            "It details provincial and territorial compliance with the Act's criteria and "
            "conditions, documents any deductions from federal transfers due to extra-billing "
            "or user charges, and reports on the state of publicly funded health insurance "
            "across Canada."
        ),
        "original_language": "en",
        "effective_date": "2024-04-01",
        "last_updated": "2025-03-01",
        "policy_id_external": "CAN-CHA-ANNUAL-2024-25",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/health-care-system/canada-health-care-system-medicare/canada-health-act.html",
        "category": "healthcare_access",
        "title": "Canada Health Act Services Policy — CHA Interpretation (2025)",
        "summary": (
            "In January 2025, the Federal Minister of Health released a new interpretation "
            "of the Canada Health Act stating that charging patients for medically necessary "
            "services provided by any health professional (e.g., nurse practitioners, "
            "pharmacists, midwives) that are typically covered when delivered by a physician "
            "is a violation of the CHA's prohibitions on extra-billing and user charges. "
            "Takes effect April 1, 2026, with compliance reporting beginning December 2028."
        ),
        "original_language": "en",
        "effective_date": "2026-04-01",
        "last_updated": "2026-03-01",
        "policy_id_external": "CAN-CHA-SERVICES-POLICY-2025",
    },

    # -----------------------------------------------------------------------
    # 2. PROVINCIAL TELEHEALTH REGULATIONS
    # -----------------------------------------------------------------------

    # Ontario
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "CPSO",
        "source_url": "https://www.cpso.on.ca/physicians/policies-guidance/policies/virtual-care",
        "category": "telehealth",
        "title": "CPSO Policy — Virtual Care (Ontario)",
        "summary": (
            "The College of Physicians and Surgeons of Ontario's policy on virtual care "
            "sets expectations for physicians providing telemedicine. Physicians must meet "
            "the same standard of care as in-person visits, establish appropriate "
            "physician-patient relationships, and ensure they can provide or arrange "
            "follow-up care. The policy addresses prescribing via virtual care, including "
            "controlled substances."
        ),
        "original_language": "en",
        "effective_date": "2021-06-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-CPSO-VIRTUAL-CARE",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Ontario Legislature",
        "source_url": "https://www.ola.org/en/legislative-business/bills/parliament-43/session-1/bill-60",
        "category": "telehealth",
        "title": "Bill 60: Your Health Act, 2023 (Ontario)",
        "summary": (
            "Ontario legislation that introduces as-of-right licensing, allowing healthcare "
            "professionals licensed in other Canadian provinces to practice in Ontario "
            "without additional approval. It aims to reduce surgical wait times, expand "
            "community health services, and increase use of private surgical and diagnostic "
            "facilities while maintaining public insurance coverage. Received Royal Assent "
            "May 18, 2023."
        ),
        "original_language": "en",
        "effective_date": "2023-05-18",
        "last_updated": "2023-09-25",
        "policy_id_external": "CAN-ON-BILL60-YOUR-HEALTH-ACT",
    },

    # British Columbia
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of BC",
        "source_url": "https://www.cpsbc.ca/registrants/current-registrants/regulatory-documents-resources/practice-standards/telemedicine",
        "category": "telehealth",
        "title": "CPSBC Telemedicine Practice Standard (British Columbia)",
        "summary": (
            "The College of Physicians and Surgeons of British Columbia's practice "
            "standard for telemedicine requires that out-of-province physicians providing "
            "virtual care to BC patients must have a formal affiliation with a local "
            "in-person clinic for timely in-person assessment when required. Physicians "
            "must ensure appropriate technology, informed consent, record-keeping, and "
            "continuity of care."
        ),
        "original_language": "en",
        "effective_date": "2020-03-01",
        "last_updated": "2024-06-01",
        "policy_id_external": "CAN-BC-CPSBC-TELEMEDICINE",
    },

    # Alberta
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College of Physicians and Surgeons of Alberta",
        "source_url": "https://cpsa.ca/physicians/standards-of-practice/telemedicine/",
        "category": "telehealth",
        "title": "CPSA Telemedicine Standard of Practice (Alberta)",
        "summary": (
            "The College of Physicians and Surgeons of Alberta requires out-of-province "
            "physicians providing virtual care to Alberta patients to be registered in the "
            "Telemedicine Register. Exceptions exist for care not readily available in "
            "Alberta, follow-up with an established physician-patient relationship, or "
            "emergency assessment. Same standard of care applies as in-person visits."
        ),
        "original_language": "en",
        "effective_date": "2020-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "CAN-AB-CPSA-TELEMEDICINE",
    },

    # Quebec
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "College des medecins du Quebec",
        "source_url": "https://www.cmq.org/en/resources-tools/practice/telemedicine",
        "category": "telehealth",
        "title": "CMQ Telemedicine Practice Guidelines (Quebec)",
        "summary": (
            "The College des medecins du Quebec regulates telehealth practice under the "
            "same ethical and professional standards as in-person care. Quebec requires "
            "out-of-province physicians to have a formal affiliation with a local clinic. "
            "Telehealth is considered an alternative modality for delivering care, not a "
            "separate discipline, and must comply with all existing professional obligations."
        ),
        "original_language": "fr",
        "effective_date": "2015-01-01",
        "last_updated": "2024-06-01",
        "policy_id_external": "CAN-QC-CMQ-TELEMEDICINE",
    },

    # -----------------------------------------------------------------------
    # 3. HEALTH CANADA — DRUG AND MEDICAL DEVICE REGULATIONS
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Justice Laws Website",
        "source_url": "https://laws-lois.justice.gc.ca/eng/acts/f-27/index.html",
        "category": "drug_regulation",
        "title": "Food and Drugs Act (R.S.C., 1985, c. F-27)",
        "summary": (
            "Canada's primary federal statute governing the safety, efficacy, and quality "
            "of food, drugs, cosmetics, and medical devices. It prohibits the sale of "
            "adulterated or misbranded products and gives Health Canada authority to "
            "regulate the manufacture, import, and sale of health products through "
            "subordinate regulations."
        ),
        "original_language": "en",
        "effective_date": "1985-01-01",
        "last_updated": "2025-06-01",
        "policy_id_external": "CAN-RSC-1985-F27",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Justice Laws Website",
        "source_url": "https://laws.justice.gc.ca/eng/regulations/SOR-98-282/FullText.html",
        "category": "medical_devices",
        "title": "Medical Devices Regulations (SOR/98-282)",
        "summary": (
            "Federal regulations under the Food and Drugs Act governing the licensing, "
            "classification, and post-market surveillance of medical devices in Canada. "
            "Devices are classified into four risk-based classes (I-IV). Manufacturers "
            "must obtain device licenses from Health Canada before selling Class II, III, "
            "or IV devices. Amended in 2025 under Agile Licensing to allow terms and "
            "conditions on authorizations."
        ),
        "original_language": "en",
        "effective_date": "1998-07-01",
        "last_updated": "2025-03-01",
        "policy_id_external": "CAN-SOR-98-282",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices.html",
        "category": "medical_devices",
        "title": "Health Canada — Medical Devices Overview",
        "summary": (
            "Health Canada's portal for medical device regulation including licensing "
            "requirements, guidance documents, recalls, and safety alerts. Health Canada "
            "reviews pre-market applications for Class II-IV devices and issues "
            "establishment licenses to manufacturers, importers, and distributors. "
            "Includes the Medical Devices Active Licence Listing database."
        ),
        "original_language": "en",
        "effective_date": "1998-07-01",
        "last_updated": "2025-12-01",
        "policy_id_external": "CAN-HC-MED-DEVICES-PORTAL",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/corporate/about-health-canada/legislation-guidelines/acts-regulations/forward-regulatory-plan/plan.html",
        "category": "drug_regulation",
        "title": "Health Canada 2025-2027 Forward Regulatory Plan",
        "summary": (
            "Health Canada's forward-looking plan for regulatory amendments from 2025 to "
            "2027, covering drugs, medical devices, natural health products, and food safety. "
            "Includes the Agile Licensing framework that gives Health Canada greater "
            "flexibility to impose terms and conditions on drug and device authorizations, "
            "with medical device provisions effective January 1, 2026."
        ),
        "original_language": "en",
        "effective_date": "2025-01-01",
        "last_updated": "2025-12-01",
        "policy_id_external": "CAN-HC-FORWARD-REG-2025-27",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "PMPRB",
        "source_url": "https://www.canada.ca/en/patented-medicine-prices-review/services/legislation/about-guidelines/guidelines.html",
        "category": "drug_regulation",
        "title": "PMPRB Guidelines for Patented Medicine Price Review",
        "summary": (
            "The Patented Medicine Prices Review Board released updated Guidelines in "
            "June 2025 (effective January 1, 2026) introducing a two-step price review "
            "process. Step one screens Canadian list prices against the highest price "
            "among 11 comparator countries. If exceeded, step two involves a detailed "
            "review. The PMPRB is an independent quasi-judicial body protecting Canadians "
            "from excessive patented drug prices."
        ),
        "original_language": "en",
        "effective_date": "2026-01-01",
        "last_updated": "2025-06-30",
        "policy_id_external": "CAN-PMPRB-GUIDELINES-2025",
    },

    # -----------------------------------------------------------------------
    # 4. PRIVACY LAWS — Federal and Provincial
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Office of the Privacy Commissioner of Canada",
        "source_url": "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/pipeda_brief/",
        "category": "data_privacy",
        "title": "PIPEDA — Personal Information Protection and Electronic Documents Act",
        "summary": (
            "Canada's federal private-sector privacy law governing how organizations "
            "collect, use, and disclose personal information in the course of commercial "
            "activities. PIPEDA applies to health data held by private-sector "
            "organizations unless a province has enacted substantially similar legislation. "
            "It is built on 10 fair information principles including consent, limiting "
            "collection, and safeguards."
        ),
        "original_language": "en",
        "effective_date": "2000-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-PIPEDA",
    },

    # Ontario PHIPA
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Ontario Legislature",
        "source_url": "https://www.ontario.ca/laws/statute/04p03",
        "category": "data_privacy",
        "title": "PHIPA — Personal Health Information Protection Act, 2004 (Ontario)",
        "summary": (
            "Ontario's health-sector privacy law governing the collection, use, and "
            "disclosure of personal health information by health information custodians "
            "(physicians, hospitals, pharmacies, etc.). Declared substantially similar to "
            "PIPEDA, exempting Ontario health custodians from federal privacy law for "
            "intra-provincial activities. The Information and Privacy Commissioner of "
            "Ontario can issue administrative monetary penalties for violations."
        ),
        "original_language": "en",
        "effective_date": "2004-11-01",
        "last_updated": "2025-08-01",
        "policy_id_external": "CAN-ON-PHIPA-2004",
    },

    # Alberta HIA
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Government of Alberta",
        "source_url": "https://www.alberta.ca/health-information-act",
        "category": "data_privacy",
        "title": "Health Information Act (Alberta)",
        "summary": (
            "Alberta's Health Information Act (HIA), in force since April 25, 2001, "
            "governs the collection, use, and disclosure of health information by "
            "custodians. It requires custodians to collect and disclose health information "
            "in the most limited manner on a need-to-know basis. Individuals have rights "
            "to access and request corrections to their health information. Breach "
            "notification is mandatory when there is a risk of harm."
        ),
        "original_language": "en",
        "effective_date": "2001-04-25",
        "last_updated": "2024-01-01",
        "policy_id_external": "CAN-AB-HIA",
    },

    # BC E-Health Act
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "BC Laws",
        "source_url": "https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/08038_01",
        "category": "data_privacy",
        "title": "E-Health (Personal Health Information Access and Protection of Privacy) Act (BC)",
        "summary": (
            "British Columbia's E-Health Act (2008) governs electronic health information "
            "in designated Health Information Banks such as PharmaNet and CareConnect. "
            "It provides individuals with limited rights to impose disclosure directives "
            "on their health information. The Act enables the creation of a province-wide "
            "electronic system for storing and accessing patient records while setting "
            "privacy protections for e-health data."
        ),
        "original_language": "en",
        "effective_date": "2008-07-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "CAN-BC-EHEALTH-ACT",
    },

    # Quebec Health Information Privacy
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "LegisQuebec",
        "source_url": "https://www.legisquebec.gouv.qc.ca/en/document/cs/p-9.0001",
        "category": "data_privacy",
        "title": "Act Respecting the Sharing of Certain Health Information (Quebec)",
        "summary": (
            "Quebec's Act respecting health and social services information came into "
            "force on July 1, 2024. It modernizes privacy obligations for health and "
            "social services providers, gives individuals the right to restrict access to "
            "their health information by specific providers, and aligns with Quebec's "
            "broader privacy reforms under Law 25 (Bill 64). Enforcement includes "
            "administrative monetary penalties."
        ),
        "original_language": "fr",
        "effective_date": "2024-07-01",
        "last_updated": "2024-07-01",
        "policy_id_external": "CAN-QC-AHSSI",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "LegisQuebec",
        "source_url": "https://www.legisquebec.gouv.qc.ca/en/document/cs/p-39.1",
        "category": "data_privacy",
        "title": "Act Respecting the Protection of Personal Information in the Private Sector — Law 25 (Quebec)",
        "summary": (
            "Quebec's modernized private-sector privacy law (Law 25 / Bill 64), adopted "
            "September 2021 and phased in through 2024, introduces GDPR-inspired "
            "obligations including mandatory privacy impact assessments, breach "
            "notification, consent requirements, and the right to data portability. "
            "It applies to all private-sector organizations in Quebec including those "
            "handling health data."
        ),
        "original_language": "fr",
        "effective_date": "2022-09-22",
        "last_updated": "2024-09-22",
        "policy_id_external": "CAN-QC-LAW25",
    },

    # -----------------------------------------------------------------------
    # 5. MEDICAL LICENSING
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Medical Council of Canada",
        "source_url": "https://mcc.ca/credentials-and-services/pathways-to-licensure/",
        "category": "medical_licensing",
        "title": "Medical Council of Canada — Pathways to Licensure",
        "summary": (
            "The Medical Council of Canada (MCC) administers qualifying examinations and "
            "grants the Licentiate of the Medical Council of Canada (LMCC), a prerequisite "
            "for provincial licensure. However, the MCC does not itself license physicians — "
            "licensing authority rests with each province's College of Physicians and "
            "Surgeons. Canada has no national medical license."
        ),
        "original_language": "en",
        "effective_date": "1912-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-MCC-PATHWAYS",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Medical Council of Canada",
        "source_url": "https://mcc.ca/credentials-and-services/pathways-to-licensure/pathways-for-u-s-graduates-and-physicians/",
        "category": "medical_licensing",
        "title": "MCC Pathways for U.S. Medical Graduates and Physicians",
        "summary": (
            "The MCC outlines pathways for U.S.-trained physicians to practice in Canada. "
            "U.S. graduates must pass MCC examinations (MCCQE Part I and Part II or NAC) "
            "and obtain the LMCC, then apply to a provincial College of Physicians and "
            "Surgeons. Requirements differ by province and training background, creating "
            "complexity for cross-border physician mobility."
        ),
        "original_language": "en",
        "effective_date": "2020-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-MCC-US-PATHWAYS",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "CPSO",
        "source_url": "https://www.cpso.on.ca/Physicians/Registration/Requirements",
        "category": "medical_licensing",
        "title": "CPSO — Registration Requirements (Ontario)",
        "summary": (
            "The College of Physicians and Surgeons of Ontario (CPSO) sets registration "
            "requirements for physicians practicing in Ontario. Applicants must hold the "
            "LMCC, complete accredited postgraduate training, and meet specific "
            "certification requirements. Ontario's Your Health Act (2023) introduced "
            "as-of-right licensing for physicians licensed in other Canadian jurisdictions."
        ),
        "original_language": "en",
        "effective_date": "2000-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-CPSO-REGISTRATION",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "CMA",
        "source_url": "https://www.cma.ca/our-focus/pan-canadian-licensure",
        "category": "medical_licensing",
        "title": "CMA — Pan-Canadian Licensure Initiative",
        "summary": (
            "The Canadian Medical Association advocates for pan-Canadian licensure to "
            "allow physicians in good standing to practice across provinces. A 2023 CMA "
            "poll found 95% of physicians support this. In October 2023, federal, "
            "provincial, and territorial health ministers committed to a new process for "
            "cross-jurisdictional practice. The Atlantic Physician Registry launched in "
            "May 2023 covering NS, NB, PEI, and NL."
        ),
        "original_language": "en",
        "effective_date": "2023-05-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-CMA-PAN-CANADIAN-LICENCE",
    },

    # -----------------------------------------------------------------------
    # 6. CROSS-BORDER HEALTHCARE WITH THE US
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/drugs-health-products/compliance-enforcement/importation-exportation/personal-use-health-products-guidance/document.html",
        "category": "cross_border",
        "title": "Bringing Health Products into Canada for Personal Use (GUI-0116)",
        "summary": (
            "Health Canada guidance on importing health products (drugs, devices, natural "
            "health products) for personal use. Generally, Canadian residents are not "
            "allowed to bring prescription drugs into Canada unless specific conditions "
            "are met, such as a 90-day supply for personal use with a valid prescription. "
            "Controlled substances have additional restrictions under the CDSA."
        ),
        "original_language": "en",
        "effective_date": "2014-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-HC-GUI-0116",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "CBSA",
        "source_url": "https://www.cbsa-asfc.gc.ca/publications/dm-md/d19/d19-9-2-eng.html",
        "category": "cross_border",
        "title": "CBSA Memorandum D19-9-2 — Importation and Exportation of Controlled Substances",
        "summary": (
            "Canada Border Services Agency memorandum outlining the rules for importing "
            "and exporting controlled substances and precursors across Canadian borders. "
            "Covers requirements for personal use quantities, permits for commercial "
            "importation, and prohibited substances. Directly relevant to cross-border "
            "prescription drug movement between Canada and the US."
        ),
        "original_language": "en",
        "effective_date": "2018-10-17",
        "last_updated": "2024-01-01",
        "policy_id_external": "CAN-CBSA-D19-9-2",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Government of Canada",
        "source_url": "https://travel.gc.ca/travelling/health-safety/medication",
        "category": "cross_border",
        "title": "Travelling with Medication — Government of Canada Travel Advisory",
        "summary": (
            "Government of Canada travel advisory on carrying prescription and "
            "over-the-counter medications when travelling internationally. Advises "
            "travellers to carry original packaging, a letter from their prescribing "
            "physician, and notes that some medications legal in Canada may be controlled "
            "or prohibited in other countries. Relevant to Canada-US border crossings."
        ),
        "original_language": "en",
        "effective_date": "2020-01-01",
        "last_updated": "2025-01-27",
        "policy_id_external": "CAN-TRAVEL-MEDICATION",
    },

    # -----------------------------------------------------------------------
    # 7. VIRTUAL CARE FRAMEWORK
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/corporate/transparency/health-agreements/bilateral-agreement-pan-canadian-virtual-care-priorities-covid-19/policy-framework.html",
        "category": "telehealth",
        "title": "Virtual Care Policy Framework — Health Canada",
        "summary": (
            "Health Canada's policy framework for pan-Canadian virtual care, developed "
            "through bilateral agreements with provinces and territories. It establishes "
            "principles for expanding virtual care access including equity, quality, "
            "privacy, interoperability, and integration with in-person services. Originally "
            "developed during COVID-19, it continues to guide national virtual care policy."
        ),
        "original_language": "en",
        "effective_date": "2020-06-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "CAN-HC-VIRTUAL-CARE-FRAMEWORK",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Standards Organization",
        "source_url": "https://healthstandards.org/standard/virtual-care-can-hso-83001-2025-e/",
        "category": "telehealth",
        "title": "CAN/HSO 83001:2025 — National Standard of Canada for Virtual Care",
        "summary": (
            "The 2025 revision of Canada's National Standard for Virtual Care, published "
            "by the Health Standards Organization. It consolidates previous virtual health "
            "and telehealth standards, reducing criteria from 119 to 41. It outlines "
            "organizational accountability for governing high-quality virtual care and "
            "sets expectations for personalized, safe virtual care encounters. Developed "
            "in compliance with Standards Council of Canada requirements."
        ),
        "original_language": "en",
        "effective_date": "2025-10-01",
        "last_updated": "2025-10-01",
        "policy_id_external": "CAN-HSO-83001-2025",
    },

    # -----------------------------------------------------------------------
    # 8. CMA VIRTUAL CARE GUIDELINES
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "CMA",
        "source_url": "https://www.cma.ca/virtual-care-playbook-canadian-physicians",
        "category": "telehealth",
        "title": "CMA Virtual Care Playbook for Canadian Physicians",
        "summary": (
            "The Canadian Medical Association's practical guide for physicians introducing "
            "virtual care services. Developed jointly with the College of Family Physicians "
            "of Canada and the Royal College of Physicians and Surgeons of Canada, it "
            "covers practice workflow integration, technology requirements, scope of "
            "practice, informed consent, and clinical documentation for virtual encounters."
        ),
        "original_language": "en",
        "effective_date": "2020-02-11",
        "last_updated": "2024-01-01",
        "policy_id_external": "CAN-CMA-VIRTUAL-PLAYBOOK",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "CMA",
        "source_url": "https://www.cma.ca/virtual-care-canada-progress-and-potential-report-virtual-care-task-force-0",
        "category": "telehealth",
        "title": "Virtual Care in Canada: Progress and Potential — CMA Task Force Report",
        "summary": (
            "The CMA Virtual Care Task Force report (2022) assessing the state of virtual "
            "care adoption in Canada post-pandemic. It documents progress in telehealth "
            "utilization, identifies barriers including inconsistent provincial regulations "
            "and digital equity gaps, and provides recommendations for scaling virtual "
            "medical services across the country."
        ),
        "original_language": "en",
        "effective_date": "2022-02-01",
        "last_updated": "2022-02-01",
        "policy_id_external": "CAN-CMA-VCTF-PROGRESS-2022",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "CMPA",
        "source_url": "https://www.cmpa-acpm.ca/en/covid19/virtual-care",
        "category": "telehealth",
        "title": "CMPA — Virtual Care Medico-Legal Guidance",
        "summary": (
            "The Canadian Medical Protective Association's medico-legal guidance for "
            "physicians providing virtual care. It addresses liability considerations, "
            "documentation requirements, patient identification and consent, jurisdictional "
            "issues when patient and physician are in different provinces, and when virtual "
            "care may not be appropriate. Essential risk management resource for telehealth."
        ),
        "original_language": "en",
        "effective_date": "2020-03-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-CMPA-VIRTUAL-CARE",
    },

    # -----------------------------------------------------------------------
    # 9. CONTROLLED SUBSTANCES PRESCRIBING VIA TELEHEALTH
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Justice Laws Website",
        "source_url": "https://laws-lois.justice.gc.ca/eng/acts/c-38.8/",
        "category": "drug_regulation",
        "title": "Controlled Drugs and Substances Act (S.C. 1996, c. 19)",
        "summary": (
            "Canada's federal legislation controlling substances that can alter mental "
            "processes and pose public health risks. Enacted in 1996, the CDSA classifies "
            "controlled substances in Schedules I-V and prohibits unauthorized production, "
            "sale, import, and export. It fulfills Canada's obligations under three UN "
            "drug conventions and provides the framework for prescribing controlled "
            "substances, including via telehealth."
        ),
        "original_language": "en",
        "effective_date": "1996-06-20",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-SC-1996-C19-CDSA",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/substance-use/toolkit-substance-use-covid-19/frequently-asked-questions.html",
        "category": "drug_regulation",
        "title": "Health Canada — Access to Controlled Substances: Telehealth Prescribing FAQ",
        "summary": (
            "Health Canada guidance on prescribing controlled substances during and after "
            "COVID-19. During the pandemic, practitioners were permitted to issue verbal "
            "prescriptions for controlled substances to pharmacists by telephone. "
            "Provincial and territorial regulators maintain standards for virtual "
            "prescribing of controlled substances, including requirements for established "
            "physician-patient relationships and risk assessment for misuse."
        ),
        "original_language": "en",
        "effective_date": "2020-03-19",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-HC-CONTROLLED-TELEHEALTH-FAQ",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Canada Gazette",
        "source_url": "https://gazette.gc.ca/rp-pr/p1/2024/2024-06-01/html/reg2-eng.html",
        "category": "drug_regulation",
        "title": "Proposed Amendments to Controlled Substances Regulations (Canada Gazette, Part I)",
        "summary": (
            "Pre-published proposed amendments to the Controlled Substances Regulations, "
            "published in the Canada Gazette on June 1, 2024. These amendments aim to "
            "modernize the prescribing framework for controlled substances, addressing "
            "telehealth prescribing practices that emerged during the pandemic and "
            "establishing permanent rules for verbal and electronic prescriptions. "
            "Final regulations expected in late 2025."
        ),
        "original_language": "en",
        "effective_date": "2024-06-01",
        "last_updated": "2025-06-01",
        "policy_id_external": "CAN-GAZETTE-CSR-2024",
    },

    # -----------------------------------------------------------------------
    # 10. DIGITAL HEALTH / AI IN HEALTHCARE
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/pre-market-guidance-machine-learning-enabled-medical-devices.html",
        "category": "medical_devices",
        "title": "Pre-market Guidance for Machine Learning-Enabled Medical Devices (PMGMLMD)",
        "summary": (
            "Health Canada's February 2025 guidance for manufacturers submitting "
            "applications for Class II, III, and IV machine-learning-enabled medical "
            "devices. Requires documentation on design, risk management, data and model "
            "development, testing, clinical validation, transparency, and post-market "
            "monitoring. Introduces predetermined change control plans (PCCPs) and "
            "emphasizes Good Machine Learning Practice (GMLP)."
        ),
        "original_language": "en",
        "effective_date": "2025-02-01",
        "last_updated": "2025-02-01",
        "policy_id_external": "CAN-HC-PMGMLMD-2025",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/corporate/transparency/health-agreements/pan-canadian-ai-guiding-principles.html",
        "category": "medical_devices",
        "title": "Pan-Canadian AI for Health (AI4H) Guiding Principles",
        "summary": (
            "Health Canada's pan-Canadian guiding principles for the responsible "
            "development and use of AI in healthcare. Covers safety and oversight, "
            "transparency, equity, accountability, and privacy. Aims to ensure AI "
            "technologies are developed and used responsibly in Canada's health system "
            "with appropriate regulatory, ethical, and procurement frameworks. Developed "
            "through federal-provincial-territorial collaboration."
        ),
        "original_language": "en",
        "effective_date": "2024-01-01",
        "last_updated": "2025-09-24",
        "policy_id_external": "CAN-HC-AI4H-PRINCIPLES",
    },

    # -----------------------------------------------------------------------
    # 11. USMCA IMPLICATIONS FOR HEALTHCARE
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "USTR / Government of Canada",
        "source_url": "https://ustr.gov/trade-agreements/free-trade-agreements/united-states-mexico-canada-agreement/agreement-between",
        "category": "cross_border",
        "title": "USMCA — Healthcare and Pharmaceutical Provisions (Canada Perspective)",
        "summary": (
            "The United States-Mexico-Canada Agreement (USMCA, in force July 1, 2020) "
            "includes provisions affecting healthcare trade. Canada agreed to extend "
            "market exclusivity for pharmaceutical patents and protect biologics with a "
            "minimum five-year data protection period. The agreement reduces duplicative "
            "regulatory requirements for medical devices across North America and includes "
            "annexes on investment and services for healthcare."
        ),
        "original_language": "en",
        "effective_date": "2020-07-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "CAN-USMCA-HEALTHCARE",
    },

    # -----------------------------------------------------------------------
    # 12. PROVINCIAL FORMULARY DIFFERENCES
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/services/health-care-system/pharmaceuticals/access-insurance-coverage-prescription-medicines/provincial-territorial-public-drug-benefit-programs.html",
        "category": "insurance",
        "title": "Provincial and Territorial Public Drug Benefit Programs",
        "summary": (
            "Health Canada's reference page listing all provincial and territorial public "
            "drug insurance programs. Coverage varies significantly: Ontario covers ~27% "
            "of new active substances vs. BC at ~11%. Each province has different "
            "premiums, deductibles, copayments, and restricted coverage categories. "
            "Drug coverage is not part of the Canada Health Act's required insured services, "
            "leading to a patchwork of provincial formularies."
        ),
        "original_language": "en",
        "effective_date": "2000-01-01",
        "last_updated": "2025-06-01",
        "policy_id_external": "CAN-HC-PROVINCIAL-DRUG-PROGRAMS",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Ontario Ministry of Health",
        "source_url": "https://www.formulary.health.gov.on.ca/",
        "category": "insurance",
        "title": "Ontario Drug Benefit Formulary / Comparative Drug Index",
        "summary": (
            "Ontario's official drug formulary listing drugs covered under the Ontario "
            "Drug Benefit (ODB) program. The ODB provides prescription drug coverage to "
            "Ontario residents aged 65+, social assistance recipients, residents of "
            "long-term care homes, and those eligible under the Trillium Drug Program. "
            "The formulary is searchable and regularly updated as new drugs are reviewed "
            "and listed."
        ),
        "original_language": "en",
        "effective_date": "1997-01-01",
        "last_updated": "2025-12-01",
        "policy_id_external": "CAN-ON-ODB-FORMULARY",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "CDA-AMC",
        "source_url": "https://www.cda-amc.ca/coverage-categories-public-drugs-plans-canada",
        "category": "insurance",
        "title": "Coverage Categories at Public Drug Plans in Canada (CDA-AMC)",
        "summary": (
            "Canada's Drug Agency (CDA-AMC, formerly CADTH) analysis of coverage "
            "categories across all 15 public drug plans in Canada. Documents how drugs "
            "are classified — from general benefit to various restricted categories — and "
            "highlights inconsistencies between provinces. All plans have one or more "
            "restricted coverage categories, and listing timelines range from 566 days "
            "(Alberta) to 816 days (PEI) from marketing authorization."
        ),
        "original_language": "en",
        "effective_date": "2023-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-CDA-AMC-COVERAGE-CATEGORIES",
    },

    # -----------------------------------------------------------------------
    # ADDITIONAL: Connected Care for Canadians Act & Digital Health Law
    # -----------------------------------------------------------------------
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Parliament of Canada",
        "source_url": "https://www.parl.ca/legisinfo/en/bill/45-1/s-5",
        "category": "healthcare_access",
        "title": "Bill S-5 — Connected Care for Canadians Act (2026)",
        "summary": (
            "Federal legislation introduced February 4, 2026, requiring health IT vendors "
            "to adopt interoperability standards for electronic health information exchange. "
            "Prohibits data blocking practices and empowers Canadians to securely access "
            "their own health data. Addresses the fact that over 70% of electronic health "
            "information is not shared between providers. Received second reading March 26, "
            "2026, and referred to Senate committee."
        ),
        "original_language": "en",
        "effective_date": "2026-02-04",
        "last_updated": "2026-03-26",
        "policy_id_external": "CAN-BILL-S5-CONNECTED-CARE",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Health Canada",
        "source_url": "https://www.canada.ca/en/health-canada/corporate/mandate/regulatory-role/what-health-canada-regulates-1/controlled-substances-precursors.html",
        "category": "drug_regulation",
        "title": "Regulating Controlled Substances and Precursors — Health Canada",
        "summary": (
            "Health Canada's overview of its regulatory role in controlling substances "
            "under the CDSA. Outlines the nine sets of regulations under the Act, "
            "including the Narcotic Control Regulations and Food and Drug Regulations "
            "Part G. Describes the licensing framework for authorized activities with "
            "controlled substances including production, distribution, and prescribing."
        ),
        "original_language": "en",
        "effective_date": "1996-06-20",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-HC-CDSA-REGULATORY",
    },
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Office of the Privacy Commissioner",
        "source_url": "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/02_05_d_15/",
        "category": "data_privacy",
        "title": "Summary of Privacy Laws in Canada — OPC",
        "summary": (
            "The Office of the Privacy Commissioner of Canada's comprehensive summary of "
            "federal, provincial, and territorial privacy legislation. Maps the landscape "
            "of health privacy laws across Canada including PIPEDA, PHIPA (Ontario), HIA "
            "(Alberta), E-Health Act (BC), and Quebec's privacy laws. Essential reference "
            "for understanding which privacy law applies in each jurisdiction."
        ),
        "original_language": "en",
        "effective_date": "2000-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CAN-OPC-PRIVACY-SUMMARY",
    },

    # Telehealth general overview (Fasken)
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "Fasken",
        "source_url": "https://www.fasken.com/en/knowledge/2024/01/considering-a-telemedicine-or-virtual-care-business-in-canada-heres-what-you-need-to-know",
        "category": "telehealth",
        "title": "Telemedicine and Virtual Care Business in Canada — Regulatory Overview (Fasken)",
        "summary": (
            "Comprehensive legal overview of the regulatory landscape for telemedicine "
            "and virtual care businesses in Canada. Covers provincial licensing "
            "requirements, standard of care obligations, prescribing rules, privacy "
            "compliance, billing considerations, and cross-provincial practice. Notes that "
            "most provinces require physicians to meet the same standard of care for "
            "virtual and in-person encounters."
        ),
        "original_language": "en",
        "effective_date": "2024-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "CAN-FASKEN-TELEHEALTH-2024",
    },

    # Digital Health Laws comprehensive reference
    {
        "country": "CAN",
        "country_name": "Canada",
        "source": "ICLG",
        "source_url": "https://iclg.com/practice-areas/digital-health-laws-and-regulations/canada",
        "category": "telehealth",
        "title": "Digital Health Laws and Regulations — Canada (ICLG 2025-2026)",
        "summary": (
            "International Comparative Legal Guide's comprehensive reference on digital "
            "health laws and regulations in Canada for 2025-2026. Covers the legal "
            "framework for telehealth, health data, AI/ML medical devices, digital "
            "therapeutics, and cross-border data transfers. Notes that Canada has no "
            "single AI statute — the proposed AIDA died when Parliament prorogued in "
            "January 2025."
        ),
        "original_language": "en",
        "effective_date": "2025-01-01",
        "last_updated": "2025-12-01",
        "policy_id_external": "CAN-ICLG-DIGITAL-HEALTH-2025",
    },
]


# ---------------------------------------------------------------------------
# Seeder Functions
# ---------------------------------------------------------------------------

def seed_canada_policies():
    """Insert Canadian healthcare policies into the database, skipping duplicates."""
    init_db()
    session = get_session()

    stored = 0
    skipped = 0

    for record in CANADA_POLICIES:
        ext_id = record["policy_id_external"]

        # Check for duplicate by policy_id_external
        existing = (
            session.query(HealthPolicy)
            .filter_by(
                country="CAN",
                policy_id_external=ext_id,
            )
            .first()
        )

        if existing:
            skipped += 1
            continue

        policy = HealthPolicy(
            country=record["country"],
            country_name=record["country_name"],
            source=record["source"],
            source_url=record["source_url"],
            category=record["category"],
            title=record["title"],
            summary=record["summary"],
            original_language=record["original_language"],
            effective_date=record["effective_date"],
            last_updated=record["last_updated"],
            fetched_at=datetime.now(timezone.utc),
            policy_id_external=ext_id,
        )
        session.add(policy)
        stored += 1

    session.commit()
    session.close()
    print(f"Canada seeder complete: {stored} new policies stored, {skipped} duplicates skipped.")
    print(f"Total Canadian policies in dataset: {len(CANADA_POLICIES)}")


if __name__ == "__main__":
    seed_canada_policies()
