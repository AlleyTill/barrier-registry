"""Seed the database with curated UK (GBR) and Mexico (MEX) healthcare policies.

Each record represents a real, verifiable healthcare policy or regulation
with actual source URLs. Research conducted April 2026.
"""

from datetime import datetime, timezone
from src.database.models import HealthPolicy, get_session, init_db


# ---------------------------------------------------------------------------
# UK (GBR) Healthcare Policies
# ---------------------------------------------------------------------------

UK_POLICIES: list[dict] = [
    # 1. NHS Constitution and Patient Rights
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "Department of Health and Social Care",
        "source_url": "https://www.gov.uk/government/publications/the-nhs-constitution-for-england",
        "category": "healthcare_access",
        "title": "NHS Constitution for England",
        "summary": (
            "The NHS Constitution establishes the principles and values of the NHS "
            "and sets out the rights and responsibilities of patients, the public, and "
            "staff. It is a declaratory document codifying existing legal rights into a "
            "single reference, and all NHS bodies and providers of NHS services are "
            "required by law to take it into account."
        ),
        "original_language": "en",
        "effective_date": "2009-01-21",
        "last_updated": "2024-01-01",
        "policy_id_external": "NHS-CONSTITUTION-2021",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "Department of Health and Social Care",
        "source_url": "https://www.gov.uk/government/publications/supplements-to-the-nhs-constitution-for-england/the-handbook-to-the-nhs-constitution-for-england",
        "category": "healthcare_access",
        "title": "Handbook to the NHS Constitution for England",
        "summary": (
            "The Handbook accompanies the NHS Constitution and provides detailed "
            "guidance on each right, pledge, and responsibility. It explains the "
            "legal sources behind each patient right, including maximum waiting times "
            "and the right to choose a provider."
        ),
        "original_language": "en",
        "effective_date": "2009-01-21",
        "last_updated": "2024-01-01",
        "policy_id_external": "NHS-CONSTITUTION-HANDBOOK",
    },

    # 2. Health and Care Act 2022
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "legislation.gov.uk",
        "source_url": "https://www.legislation.gov.uk/ukpga/2022/31/contents/enacted",
        "category": "healthcare_access",
        "title": "Health and Care Act 2022",
        "summary": (
            "Major reform legislation that established Integrated Care Systems on a "
            "statutory footing, merged NHS England and NHS Improvement, and replaced "
            "the NHS internal market with a provider selection regime. It gives the "
            "Secretary of State enhanced powers over NHS agencies and sets a net-zero "
            "carbon target for the NHS by 2040."
        ),
        "original_language": "en",
        "effective_date": "2022-04-28",
        "last_updated": "2023-10-01",
        "policy_id_external": "UKPGA-2022-31",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "GOV.UK",
        "source_url": "https://www.gov.uk/government/collections/health-and-care-act-2022",
        "category": "healthcare_access",
        "title": "Health and Care Act 2022 — Implementation Guidance Collection",
        "summary": (
            "Collection of implementation guidance documents for the Health and Care "
            "Act 2022, including regulations for the provider selection regime, "
            "integrated care boards, and consequential amendments. Tracks commencement "
            "orders bringing provisions into force."
        ),
        "original_language": "en",
        "effective_date": "2022-04-28",
        "last_updated": "2023-11-01",
        "policy_id_external": "HCA-2022-COLLECTION",
    },

    # 3. Telehealth / Telemedicine Regulations
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "Care Quality Commission",
        "source_url": "https://www.cqc.org.uk/guidance-providers/registration/scope-registration",
        "category": "telehealth",
        "title": "CQC Registration of Remote / Telehealth Service Providers",
        "summary": (
            "The CQC requires registration of telehealth and telemedicine providers "
            "who deliver triage and medical advice remotely when the advice is "
            "responsive for immediate attention or constitutes triage. Updated guidance "
            "in 2025 clarified the scope of regulated remote advice activities."
        ),
        "original_language": "en",
        "effective_date": "2014-04-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "CQC-REMOTE-REG",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "NHS England",
        "source_url": "https://www.england.nhs.uk/long-read/digital-first-primary-care/",
        "category": "telehealth",
        "title": "Digital-First Primary Care Policy",
        "summary": (
            "NHS England policy enabling GP practices and primary care providers to "
            "deliver consultations digitally by default where clinically appropriate. "
            "Integrated Care Boards were allocated funding for digital pathways and "
            "demand/capacity tools in 2024/25."
        ),
        "original_language": "en",
        "effective_date": "2019-01-01",
        "last_updated": "2024-04-01",
        "policy_id_external": "NHSE-DIGITAL-FIRST-PC",
    },

    # 4. Medical Device Regulations (MHRA)
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "legislation.gov.uk",
        "source_url": "https://www.legislation.gov.uk/uksi/2002/618/contents/made",
        "category": "medical_devices",
        "title": "The Medical Devices Regulations 2002 (SI 2002/618, as amended)",
        "summary": (
            "The primary legislation governing medical devices in Great Britain. "
            "Requires all medical devices, including IVDs, custom-made devices, and "
            "system/procedure packs to be registered with the MHRA before placement "
            "on the GB market. Higher-risk devices require assessment by an approved body."
        ),
        "original_language": "en",
        "effective_date": "2002-06-13",
        "last_updated": "2024-06-16",
        "policy_id_external": "UKSI-2002-618",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "MHRA",
        "source_url": "https://www.gov.uk/government/publications/implementation-of-the-future-regulation-of-medical-devices",
        "category": "medical_devices",
        "title": "MHRA Roadmap to Future Medical Devices Regulation",
        "summary": (
            "Revised roadmap published December 2024 outlining the transition to the "
            "new UK medical devices regulatory framework. Core aspects applied from "
            "June 2025, with new post-market surveillance requirements, UDI mandates, "
            "and an international reliance scheme planned for 2026."
        ),
        "original_language": "en",
        "effective_date": "2024-12-01",
        "last_updated": "2025-06-16",
        "policy_id_external": "MHRA-ROADMAP-2024",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "MHRA",
        "source_url": "https://www.gov.uk/government/publications/software-and-ai-as-a-medical-device",
        "category": "medical_devices",
        "title": "MHRA AI Airlock — Regulatory Sandbox for AI as a Medical Device",
        "summary": (
            "The MHRA launched the AI Airlock in May 2024 as the first regulatory "
            "sandbox for AI as a Medical Device (AIaMD). The pilot ran until April "
            "2025 to explore proportionate regulation of AI-driven diagnostic and "
            "clinical decision support tools."
        ),
        "original_language": "en",
        "effective_date": "2024-05-01",
        "last_updated": "2025-04-01",
        "policy_id_external": "MHRA-AI-AIRLOCK",
    },

    # 5. Data Protection in Healthcare
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "legislation.gov.uk",
        "source_url": "https://www.legislation.gov.uk/ukpga/2018/12/contents",
        "category": "data_privacy",
        "title": "Data Protection Act 2018",
        "summary": (
            "The UK's primary data protection legislation implementing the UK GDPR. "
            "Schedule 1 contains specific provisions for health and social care "
            "purposes, establishing the legal basis for processing health data. "
            "Works alongside the Common Law Duty of Confidentiality for patient data."
        ),
        "original_language": "en",
        "effective_date": "2018-05-25",
        "last_updated": "2024-01-01",
        "policy_id_external": "UKPGA-2018-12",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "NHS England Digital",
        "source_url": "https://digital.nhs.uk/services/national-data-opt-out",
        "category": "data_privacy",
        "title": "NHS National Data Opt-Out",
        "summary": (
            "Policy allowing patients in England to opt out of their confidential "
            "patient information being used for research and planning purposes. "
            "NHS Digital manages the service, and all health and care organisations "
            "must apply the opt-out to disclosures of confidential patient information."
        ),
        "original_language": "en",
        "effective_date": "2018-05-25",
        "last_updated": "2024-03-01",
        "policy_id_external": "NHS-DATA-OPT-OUT",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "NHS England",
        "source_url": "https://www.england.nhs.uk/long-read/information-governance-and-data-protection/",
        "category": "data_privacy",
        "title": "NHS England Information Governance and Data Protection Framework",
        "summary": (
            "Framework governing how NHS organisations handle personal data, "
            "including requirements for data sharing agreements, fair processing "
            "notices, and the shift from data sharing to data access via Secure "
            "Data Environments as set out in the Data Saves Lives strategy."
        ),
        "original_language": "en",
        "effective_date": "2022-06-01",
        "last_updated": "2024-06-01",
        "policy_id_external": "NHSE-IG-FRAMEWORK",
    },

    # 6. Medical Licensing (GMC)
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "General Medical Council",
        "source_url": "https://www.gmc-uk.org/registration-and-licensing",
        "category": "medical_licensing",
        "title": "GMC Registration and Licensing Requirements",
        "summary": (
            "All doctors practising medicine in the UK must hold GMC registration "
            "and a licence to practise. From 2024, the UK Medical Licensing Assessment "
            "(UKMLA) is required for overseas doctors and UK medical graduates from "
            "2024-25, replacing the previous PLAB examination pathway."
        ),
        "original_language": "en",
        "effective_date": "1983-01-01",
        "last_updated": "2024-09-01",
        "policy_id_external": "GMC-REG-LICENSING",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "legislation.gov.uk",
        "source_url": "https://www.legislation.gov.uk/ukpga/1983/54/contents",
        "category": "medical_licensing",
        "title": "Medical Act 1983",
        "summary": (
            "The foundational legislation establishing the General Medical Council "
            "and the legal framework for medical registration, fitness to practise, "
            "and professional standards in the UK. Requires doctors to be registered "
            "with the GMC and hold a licence to practise medicine."
        ),
        "original_language": "en",
        "effective_date": "1983-10-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "UKPGA-1983-54",
    },

    # 7. Cross-Border Healthcare (Post-Brexit)
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "GOV.UK",
        "source_url": "https://www.gov.uk/guidance/uk-healthcare-in-the-eu",
        "category": "healthcare_access",
        "title": "UK-EU Trade and Cooperation Agreement — Healthcare Provisions",
        "summary": (
            "Post-Brexit reciprocal healthcare arrangements under the UK-EU Trade "
            "and Cooperation Agreement. Adopts provisions of EU Regulations 883/2004 "
            "and 987/2009 for social security coordination. The Global Health Insurance "
            "Card (GHIC) replaced the EHIC for UK residents travelling in the EU."
        ),
        "original_language": "en",
        "effective_date": "2021-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "UK-EU-TCA-HEALTHCARE",
    },

    # 8. Digital Health Regulations
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "NHSX / NHS England",
        "source_url": "https://www.digitalregulations.innovation.nhs.uk/",
        "category": "telehealth",
        "title": "NHS AI and Digital Regulations Service",
        "summary": (
            "Online service helping developers and commissioners understand the "
            "regulatory landscape for digital health technologies, AI, and software "
            "as a medical device in the UK. Consolidates guidance from MHRA, CQC, "
            "ICO, and NHS England into a single navigation tool."
        ),
        "original_language": "en",
        "effective_date": "2023-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "NHS-DIGITAL-REG-SERVICE",
    },

    # 9. Prescription and Pharmacy Regulations
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "legislation.gov.uk",
        "source_url": "https://www.legislation.gov.uk/uksi/2012/1916/contents/made",
        "category": "drug_regulation",
        "title": "The Human Medicines Regulations 2012 (SI 2012/1916)",
        "summary": (
            "Consolidates UK law on medicinal products for human use, covering "
            "marketing authorisation, manufacture, import, distribution, sale, "
            "supply, labelling, advertising, and pharmacovigilance. Establishes "
            "prescription-only, pharmacy, and general sale medicine classifications."
        ),
        "original_language": "en",
        "effective_date": "2012-08-14",
        "last_updated": "2024-01-01",
        "policy_id_external": "UKSI-2012-1916",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "GOV.UK",
        "source_url": "https://www.gov.uk/guidance/regulating-medical-devices-in-the-uk",
        "category": "drug_regulation",
        "title": "MHRA Guidance on Regulating Medicines and Medical Devices in the UK",
        "summary": (
            "Comprehensive guidance from the MHRA on the regulatory requirements "
            "for medicines and medical devices on the UK market, including marketing "
            "authorisation routes, GMP requirements, and the UKCA marking regime "
            "that is replacing CE marking for the GB market."
        ),
        "original_language": "en",
        "effective_date": "2021-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MHRA-REG-GUIDANCE",
    },

    # 10. Mental Health Act
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "legislation.gov.uk",
        "source_url": "https://www.legislation.gov.uk/ukpga/1983/20/contents",
        "category": "healthcare_access",
        "title": "Mental Health Act 1983",
        "summary": (
            "The primary legislation governing the compulsory detention and treatment "
            "of people with mental disorders in England and Wales. Sets out criteria "
            "for sectioning, patients' rights to tribunals, and the role of Approved "
            "Mental Health Professionals and Responsible Clinicians."
        ),
        "original_language": "en",
        "effective_date": "1983-10-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "UKPGA-1983-20",
    },
    {
        "country": "GBR",
        "country_name": "United Kingdom",
        "source": "legislation.gov.uk",
        "source_url": "https://www.legislation.gov.uk/ukpga/2025/33",
        "category": "healthcare_access",
        "title": "Mental Health Act 2025",
        "summary": (
            "Reform legislation amending the Mental Health Act 1983 with a higher "
            "'serious harm' threshold for detention, reduced time before a second "
            "opinion is required for treatment without consent, and provisions to "
            "end detention of autistic people and those with learning disabilities "
            "under Section 3 once community services are in place. Phased implementation "
            "beginning 2027."
        ),
        "original_language": "en",
        "effective_date": "2025-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "UKPGA-2025-33",
    },
]


# ---------------------------------------------------------------------------
# Mexico (MEX) Healthcare Policies
# ---------------------------------------------------------------------------

MEX_POLICIES: list[dict] = [
    # 1. Ley General de Salud
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LGS.pdf",
        "category": "healthcare_access",
        "title": "Ley General de Salud (General Health Law)",
        "summary": (
            "Mexico's primary healthcare legislation establishing the bases and "
            "modalities for access to health services, the National Health System, "
            "and distribution of competencies between federal and state governments. "
            "Guarantees the right to health protection with provisions on free "
            "services, medicines, and supplies for uninsured populations."
        ),
        "original_language": "es",
        "effective_date": "1984-02-07",
        "last_updated": "2025-01-01",
        "policy_id_external": "LGS-DOF",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Justia México",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-de-salud/",
        "category": "healthcare_access",
        "title": "Ley General de Salud — Texto Vigente Consolidado",
        "summary": (
            "Consolidated current text of the General Health Law including all "
            "amendments through 2025. Defines health as complete physical, mental, "
            "and social well-being, and mandates a differentiated approach with "
            "gender perspective and interculturality in health protection."
        ),
        "original_language": "es",
        "effective_date": "1984-02-07",
        "last_updated": "2025-01-01",
        "policy_id_external": "LGS-JUSTIA",
    },

    # 2. COFEPRIS Regulations
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS",
        "source_url": "https://www.gob.mx/cofepris",
        "category": "drug_regulation",
        "title": "COFEPRIS — Comisión Federal para la Protección contra Riesgos Sanitarios",
        "summary": (
            "Mexico's federal health regulatory agency, equivalent to the US FDA. "
            "Responsible for regulating health facilities, controlling advertising, "
            "and overseeing the manufacture, import, and export of medicines, medical "
            "devices, and other health products. Operates as a decentralized body "
            "under the Ministry of Health."
        ),
        "original_language": "es",
        "effective_date": "2001-07-05",
        "last_updated": "2025-01-01",
        "policy_id_external": "COFEPRIS-GENERAL",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS",
        "source_url": "https://www.pureglobal.com/news/mexico-cofepris-2025-abbreviated-pathway-for-medical-devices",
        "category": "medical_devices",
        "title": "COFEPRIS Abbreviated Regulatory Pathway for Medical Devices (2025)",
        "summary": (
            "Launched September 1, 2025, this pathway enables medical device and "
            "drug manufacturers to fast-track approvals by leveraging prior "
            "authorizations from trusted international regulators (FDA, EMA, Health "
            "Canada, Swissmedic, ANVISA, TGA). Promises 30-day evaluation timelines "
            "through the expanded Equivalency Route."
        ),
        "original_language": "es",
        "effective_date": "2025-09-01",
        "last_updated": "2025-09-01",
        "policy_id_external": "COFEPRIS-ABBREV-2025",
    },

    # 3. IMSS / ISSSTE Healthcare System
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "IMSS",
        "source_url": "https://www.imss.gob.mx/personas-trabajadoras-independientes/extranjeros-en-mexico/english",
        "category": "insurance",
        "title": "IMSS Voluntary and Mandatory Enrollment Requirements",
        "summary": (
            "The Instituto Mexicano del Seguro Social provides healthcare coverage "
            "to formal-sector employees (mandatory enrollment from first day of "
            "employment) and voluntary enrollees including foreign residents with "
            "legal residency status. Benefits cover health, income replacement, "
            "workplace safety, maternity support, retirement savings, and childcare."
        ),
        "original_language": "es",
        "effective_date": "1943-01-19",
        "last_updated": "2024-01-01",
        "policy_id_external": "IMSS-ENROLLMENT",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "ISSSTE",
        "source_url": "https://www.gob.mx/issste",
        "category": "insurance",
        "title": "ISSSTE — Instituto de Seguridad y Servicios Sociales de los Trabajadores del Estado",
        "summary": (
            "Mexico's social security institute for public-sector employees, "
            "providing healthcare, pensions, housing loans, and other social "
            "benefits to government workers and their families. Operates a parallel "
            "healthcare network to IMSS with its own hospitals and clinics."
        ),
        "original_language": "es",
        "effective_date": "1959-12-30",
        "last_updated": "2024-01-01",
        "policy_id_external": "ISSSTE-GENERAL",
    },

    # 4. Telehealth / Telemedicine
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Salud",
        "source_url": "https://iclg.com/practice-areas/digital-health-laws-and-regulations/mexico",
        "category": "telehealth",
        "title": "Mexico Digital Health and Telemedicine Regulatory Framework",
        "summary": (
            "Mexico has no specific telemedicine law, but the General Health Law "
            "recognises digital health, telehealth, and telemedicine as valid forms "
            "of medical care delivery in accordance with official Mexican standards "
            "(NOMs) issued by the Health Secretariat. Regulation remains dispersed "
            "across multiple instruments and is evolving."
        ),
        "original_language": "es",
        "effective_date": "2020-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-TELEHEALTH-FRAMEWORK",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "DLA Piper",
        "source_url": "https://www.dlapiperintelligence.com/telehealth/countries/index.html?t=02-regulation-of-telehealth&c=MX",
        "category": "telehealth",
        "title": "Mexico Telehealth Regulation Overview",
        "summary": (
            "Telemedicine is permitted in Mexico but lacks a dedicated regulatory "
            "framework. Current regulations do not preclude remote medical care via "
            "ICT. The regulatory body has drafted a NOM for telesalud that was never "
            "officially published as mandatory. Authorities are gradually introducing "
            "policies to regulate telehealth services."
        ),
        "original_language": "es",
        "effective_date": "2020-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-TELEHEALTH-OVERVIEW",
    },

    # 5. Medical Device Regulations
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS",
        "source_url": "https://www.pureglobal.com/markets/mexico/cofepris-medical-device-regulations",
        "category": "medical_devices",
        "title": "COFEPRIS Medical Device Registration Requirements",
        "summary": (
            "Medical devices in Mexico are regulated by the General Health Law, the "
            "Reglamento de Insumos para la Salud, and COFEPRIS NOMs. Devices are "
            "classified into three risk classes (I, II, III). Registration requires "
            "ISO 13485 certification or equivalent, and devices must comply with "
            "Good Manufacturing Practices."
        ),
        "original_language": "es",
        "effective_date": "2010-01-01",
        "last_updated": "2025-07-07",
        "policy_id_external": "COFEPRIS-MD-REG",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS",
        "source_url": "https://www.emergobyul.com/news/mexicos-cofepris-updates-low-risk-and-deregulated-medical-devices-list",
        "category": "medical_devices",
        "title": "COFEPRIS Updated Low-Risk and Deregulated Medical Devices List (2025)",
        "summary": (
            "On July 7, 2025, COFEPRIS published the first update in 11 years to "
            "the list of low-risk and deregulated devices. The update consolidates "
            "regulations into three annexes: low-risk devices requiring registration, "
            "low-risk devices requiring GMP compliance, and products not considered "
            "medical devices."
        ),
        "original_language": "es",
        "effective_date": "2025-07-07",
        "last_updated": "2025-07-07",
        "policy_id_external": "COFEPRIS-LOWRISK-2025",
    },

    # 6. Data Privacy in Healthcare
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.dlapiperdataprotection.com/index.html?t=about&c=MX",
        "category": "data_privacy",
        "title": "Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP)",
        "summary": (
            "Mexico's federal data privacy law for the private sector, updated in "
            "2025. Strengthens consent, transparency, and accountability obligations "
            "for personal data processing. Expressly covers data processors. "
            "Healthcare data is exempt from consent when essential for medical "
            "attention, prevention, diagnosis, or treatment when the patient cannot "
            "give consent."
        ),
        "original_language": "es",
        "effective_date": "2010-07-05",
        "last_updated": "2025-03-21",
        "policy_id_external": "LFPDPPP-2025",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.dlapiperdataprotection.com/index.html?t=about&c=MX",
        "category": "data_privacy",
        "title": "Dissolution of INAI and Transfer to Ministry of Anticorruption and Good Governance",
        "summary": (
            "As of March 21, 2025, the National Institute of Transparency, Access "
            "to Information, and Protection of Personal Data (INAI) was dissolved. "
            "Data protection enforcement responsibilities transferred to the Ministry "
            "of Anticorruption and Good Governance, a body reporting directly to the "
            "executive branch. ARCO rights (access, rectification, cancellation, "
            "objection) are retained."
        ),
        "original_language": "es",
        "effective_date": "2025-03-21",
        "last_updated": "2025-03-21",
        "policy_id_external": "INAI-DISSOLUTION-2025",
    },

    # 7. Medical Licensing Requirements
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Educación Pública",
        "source_url": "https://www.cedulaprofesional.sep.gob.mx/",
        "category": "medical_licensing",
        "title": "Cédula Profesional — Medical Licensing System",
        "summary": (
            "The Cédula Profesional is the mandatory professional licence to practise "
            "medicine in Mexico, issued by the SEP after completion of medical studies. "
            "The public registry allows verification of any doctor's licence status. "
            "Medical specialists require a second cédula confirming completion of an "
            "accredited residency program."
        ),
        "original_language": "es",
        "effective_date": "1945-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "SEP-CEDULA-PROF",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "CONACEM",
        "source_url": "https://conacem.org.mx/",
        "category": "medical_licensing",
        "title": "CONACEM — Comité Normativo Nacional de Consejos de Especialidades Médicas",
        "summary": (
            "The national regulatory committee coordinating medical specialty councils "
            "in Mexico. Board certification through the relevant specialty council is "
            "required for specialists and must be renewed every five years. CONACEM "
            "maintains a public registry for verification of specialist certification."
        ),
        "original_language": "es",
        "effective_date": "1995-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "CONACEM-CERT",
    },

    # 8. Pharmaceutical Regulations
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS",
        "source_url": "https://clinregs.niaid.nih.gov/country/mexico",
        "category": "drug_regulation",
        "title": "Reglamento de Insumos para la Salud (Health Supplies Regulation)",
        "summary": (
            "The secondary regulation under the General Health Law that establishes "
            "specific requirements for marketing authorisation of medicines and "
            "medical devices. Applicants must prove safety and efficacy through "
            "clinical trials, and new molecules require approval from COFEPRIS's "
            "New Molecules Committee."
        ),
        "original_language": "es",
        "effective_date": "1998-02-04",
        "last_updated": "2024-01-01",
        "policy_id_external": "RIS-DOF",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2018.00272/full",
        "category": "drug_regulation",
        "title": "NOM-257-SSA1-2014 — Biotechnological Medicines Registration",
        "summary": (
            "Official Mexican Standard establishing requirements for registration "
            "of biotherapeutic products including biotechnological innovators and "
            "biocomparables. Covers Good Manufacturing Practices, labelling, "
            "stability, clinical trials, biocomparability studies, and "
            "pharmacovigilance requirements."
        ),
        "original_language": "es",
        "effective_date": "2015-02-09",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-257-SSA1-2014",
    },

    # 9. Healthcare Access Programs (IMSS-Bienestar)
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "IMSS-Bienestar",
        "source_url": "https://www.imss.gob.mx/imss-bienestar",
        "category": "healthcare_access",
        "title": "IMSS-Bienestar — Healthcare Services for the Uninsured Population",
        "summary": (
            "Replaced INSABI in 2023 (which itself replaced Seguro Popular in 2020) "
            "as Mexico's programme providing free healthcare to the uninsured "
            "population. Operates under IMSS with transferred human, budgetary, "
            "and material resources (107.5 billion pesos budgeted for 2023). "
            "Functions as both insurer and direct service provider through public "
            "health facilities."
        ),
        "original_language": "es",
        "effective_date": "2023-05-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "IMSS-BIENESTAR",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://mexlaw.com/10-things-you-should-know-about-the-new-health-service-in-mexico/",
        "category": "healthcare_access",
        "title": "Reform to General Health Law — Termination of INSABI and Creation of IMSS-Bienestar",
        "summary": (
            "In April 2023, the Chamber of Deputies approved reforms to the General "
            "Health Law terminating INSABI and transferring its functions to "
            "IMSS-Bienestar. The reform establishes a single decentralized body "
            "providing health services throughout the country, with a 180-day "
            "transition for resource transfer from the Ministry of Health."
        ),
        "original_language": "es",
        "effective_date": "2023-05-29",
        "last_updated": "2024-01-01",
        "policy_id_external": "LGS-REFORM-INSABI-2023",
    },

    # 10. Cross-Border Healthcare with the US
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS / JCI",
        "source_url": "https://www.medicaltourismco.com/medical-tourism-in-mexico/",
        "category": "healthcare_access",
        "title": "Mexico Medical Tourism and Cross-Border Healthcare Regulations",
        "summary": (
            "Mexico's cross-border healthcare is regulated by COFEPRIS, which "
            "enforces standards for hospitals, medications, and equipment. Several "
            "private hospitals hold Joint Commission International (JCI) "
            "accreditation. An estimated 1.3 million Americans traveled to Mexico "
            "for medical care in 2024, contributing $430 million annually to border "
            "economies."
        ),
        "original_language": "es",
        "effective_date": "2010-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-MEDICAL-TOURISM",
    },

    # Additional: NOM-024-SSA3-2012 Electronic Health Records
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Salud",
        "source_url": "https://www.gob.mx/cms/uploads/attachment/file/14549/DOF-30NOV12-NOM-024-SSA3-2012_English.pdf",
        "category": "telehealth",
        "title": "NOM-024-SSA3-2012 — Electronic Health Records and Medical Information Systems",
        "summary": (
            "Official Mexican Standard establishing functional and interoperability "
            "requirements for electronic medical record systems. Mandatory for all "
            "healthcare providers using electronic records. Defines minimum "
            "functionalities for clinical notes, prescriptions, and results, and "
            "requires interoperability with international standards (HL7, FHIR, DICOM)."
        ),
        "original_language": "es",
        "effective_date": "2013-01-30",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-024-SSA3-2012",
    },
]


# ---------------------------------------------------------------------------
# Seeder Logic
# ---------------------------------------------------------------------------

ALL_POLICIES = UK_POLICIES + MEX_POLICIES


def seed_uk_mexico_policies():
    """Seed UK and Mexico healthcare policies into the database."""
    init_db()
    session = get_session()

    stored = 0
    skipped = 0

    for policy_data in ALL_POLICIES:
        # Check for duplicates using country + policy_id_external
        ext_id = policy_data.get("policy_id_external", "")
        country = policy_data["country"]

        if ext_id:
            existing = (
                session.query(HealthPolicy)
                .filter_by(country=country, policy_id_external=ext_id)
                .first()
            )
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

    print(f"UK/Mexico Policy Seeder complete.")
    print(f"  Stored: {stored} new policies")
    print(f"  Skipped: {skipped} duplicates")
    print(f"  Total in dataset: {len(ALL_POLICIES)} "
          f"({len(UK_POLICIES)} UK, {len(MEX_POLICIES)} Mexico)")


if __name__ == "__main__":
    seed_uk_mexico_policies()
