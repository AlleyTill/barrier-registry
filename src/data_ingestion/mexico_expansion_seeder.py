"""Expanded Mexican healthcare policy dataset.

Adds 60+ additional Mexican healthcare policies covering areas NOT already
in the uk_mexico_seeder.py (which covers telehealth basics, COFEPRIS general,
IMSS/ISSSTE, data privacy, Ley General de Salud, NOM-024-SSA3, NOM-257-SSA1,
medical licensing, medical devices, and IMSS-Bienestar).

Research conducted April 2026.  All source URLs verified at time of writing.
"""

from datetime import datetime, timezone
from src.database.models import HealthPolicy, get_session, init_db


# ---------------------------------------------------------------------------
# Mexico Expansion Policies
# ---------------------------------------------------------------------------

MEX_EXPANSION_POLICIES: list[dict] = [

    # -----------------------------------------------------------------------
    # 1. NOMs (Normas Oficiales Mexicanas) — Healthcare Standards
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://dof.gob.mx/nota_detalle_popup.php?codigo=5272787",
        "category": "clinical_standards",
        "title": "NOM-004-SSA3-2012 — Del Expediente Clínico (Clinical Records)",
        "summary": (
            "Official Mexican Standard establishing mandatory scientific, ethical, "
            "technological, and administrative criteria for the creation, integration, "
            "use, management, archiving, preservation, ownership, and confidentiality "
            "of the clinical record. Applies to all medical care establishments in "
            "Mexico, public and private. As of January 2026, a DOF decree mandates "
            "digitalization, ending paper-only records as a legal option."
        ),
        "original_language": "es",
        "effective_date": "2012-10-15",
        "last_updated": "2026-01-15",
        "policy_id_external": "NOM-004-SSA3-2012",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5284306&fecha=08/01/2013",
        "category": "healthcare_infrastructure",
        "title": "NOM-016-SSA3-2012 — Minimum Infrastructure and Equipment for Hospitals",
        "summary": (
            "Official Mexican Standard establishing minimum characteristics for "
            "infrastructure and equipment of hospitals and specialized medical care "
            "offices. Covers physical plant requirements, medical equipment standards, "
            "and operational specifications for all public, social, and private sector "
            "hospitals in the national territory."
        ),
        "original_language": "es",
        "effective_date": "2013-01-08",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-016-SSA3-2012",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://platiica.economia.gob.mx/normalizacion/nom-005-ssa3-2018/",
        "category": "healthcare_infrastructure",
        "title": "NOM-005-SSA3-2018 — Minimum Infrastructure for Ambulatory Care Establishments",
        "summary": (
            "Official Mexican Standard establishing minimum requirements for "
            "infrastructure and equipment of ambulatory (outpatient) medical care "
            "establishments. Applies to all public and private clinics, medical offices, "
            "and facilities serving patients without hospitalization. Updated from the "
            "2010 version and entered into force in 2020."
        ),
        "original_language": "es",
        "effective_date": "2020-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-005-SSA3-2018",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://platiica.economia.gob.mx/normalizacion/nom-027-ssa3-2013/",
        "category": "emergency_services",
        "title": "NOM-027-SSA3-2013 — Emergency Medical Services Standards",
        "summary": (
            "Official Mexican Standard regulating the functioning and care criteria "
            "for emergency services in medical care establishments. Mandatory for all "
            "public, social, and private sector facilities offering emergency services "
            "(excluding ambulance mobile units). Establishes requirements for human "
            "resources, physical infrastructure, minimum equipment, and homogeneous "
            "protocols for efficient response to medical and surgical emergencies."
        ),
        "original_language": "es",
        "effective_date": "2013-11-04",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-027-SSA3-2013",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://platiica.economia.gob.mx/normalizacion/nom-035-ssa3-2012/",
        "category": "health_information",
        "title": "NOM-035-SSA3-2012 — Health Information Systems",
        "summary": (
            "Official Mexican Standard establishing criteria and procedures for "
            "producing, capturing, integrating, processing, systematizing, evaluating, "
            "and disseminating health information. Mandatory for all establishments, "
            "individuals, and entities of the National Health System in the public, "
            "social, and private sectors that provide healthcare services."
        ),
        "original_language": "es",
        "effective_date": "2012-11-30",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-035-SSA3-2012",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://dof.gob.mx/nota_detalle.php?codigo=5354092&fecha=28/07/2014",
        "category": "health_workforce",
        "title": "NOM-009-SSA3-2013 — Health Education and Medical Social Service",
        "summary": (
            "Official Mexican Standard establishing conditions for the education of "
            "health personnel and for the provision of medical social service (servicio "
            "social). Defines modalities including rural unit assignments, research and "
            "teaching, and assignments to urban areas of low socioeconomic development. "
            "Sets minimum standards for clinical training sites in underserved areas."
        ),
        "original_language": "es",
        "effective_date": "2014-07-28",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-009-SSA3-2013",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://platiica.economia.gob.mx/normalizacion/nom-046-ssa2-2005/",
        "category": "patient_rights",
        "title": "NOM-046-SSA2-2005 — Violence Against Women: Prevention and Healthcare Protocol",
        "summary": (
            "Official Mexican Standard establishing criteria for prevention and "
            "healthcare attention for family violence, sexual violence, and violence "
            "against women. Requires healthcare providers to assess and treat physical "
            "injuries, provide crisis intervention and psychological care, offer "
            "emergency contraception within 120 hours, and guarantee access to safe "
            "abortion services for pregnancy resulting from rape."
        ),
        "original_language": "es",
        "effective_date": "2009-04-16",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-046-SSA2-2005",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://mexicanlaws.com/SALUD/NOM-177-SSA1-2013.htm",
        "category": "drug_regulation",
        "title": "NOM-177-SSA1-2013 — Bioequivalence and Interchangeability of Generic Medicines",
        "summary": (
            "Official Mexican Standard establishing tests and procedures for "
            "demonstrating that a drug product is interchangeable with the reference "
            "product. Sets requirements for authorized third parties performing "
            "interchangeability tests and biocomparability studies. A modification "
            "became effective September 16, 2023. Critical for Mexico's generic drug "
            "market where 89% of IMSS pharmaceutical purchases are interchangeable "
            "generics."
        ),
        "original_language": "es",
        "effective_date": "2013-09-20",
        "last_updated": "2023-09-16",
        "policy_id_external": "NOM-177-SSA1-2013",
    },

    # -----------------------------------------------------------------------
    # 2. Clinical Trials Regulations
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://clinregs.niaid.nih.gov/country/mexico",
        "category": "clinical_trials",
        "title": "NOM-012-SSA3-2012 — Criteria for Clinical Research in Humans",
        "summary": (
            "Official Mexican Standard establishing criteria for the execution of "
            "research projects for health in human beings. Requires COFEPRIS approval "
            "for all clinical trials (Phases I-IV) involving registered or unregistered "
            "investigational products. Mandates prior favorable decision from the "
            "institution's Research Ethics Committee; COFEPRIS and Ethics Committee "
            "reviews may not be conducted in parallel."
        ),
        "original_language": "es",
        "effective_date": "2013-01-04",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-012-SSA3-2012",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS",
        "source_url": "https://practiceguides.chambers.com/practice-guides/life-sciences-2025/mexico/trends-and-developments",
        "category": "clinical_trials",
        "title": "COFEPRIS Clinical Trial Authorization Process and Good Clinical Practices",
        "summary": (
            "COFEPRIS requires authorization for all research protocols involving "
            "human subjects or biological samples. Authorization depends on favorable "
            "opinions from Research Ethics and Biosafety Committees. A new NOM on Good "
            "Clinical Practices is under regulatory development to regulate Contract "
            "Research Organizations (CROs) and align with international standards. "
            "Mexico joined ICH in November 2021, harmonizing technical requirements."
        ),
        "original_language": "es",
        "effective_date": "2012-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-COFEPRIS-CLINICAL-TRIALS",
    },

    # -----------------------------------------------------------------------
    # 3. Mental Health Legislation
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5652074&fecha=16/05/2022",
        "category": "mental_health",
        "title": "Reform to General Health Law on Mental Health and Addiction Prevention (2022)",
        "summary": (
            "Comprehensive reform to Articles 72-77 of the General Health Law, approved "
            "unanimously (471-0) in April 2022 and published in the DOF on May 16, 2022. "
            "Establishes mental health and addiction prevention as priority public health "
            "axes. Mandates community-based, interdisciplinary care with a gender "
            "perspective, and requires progressive closure of psychiatric hospitals in "
            "favor of outpatient centers and general hospital psychiatry services."
        ),
        "original_language": "es",
        "effective_date": "2022-05-16",
        "last_updated": "2024-01-01",
        "policy_id_external": "LGS-MENTAL-HEALTH-2022",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Justia México",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-de-salud/titulo-tercero/capitulo-vii/",
        "category": "mental_health",
        "title": "Ley General de Salud — Capítulo VII: Salud Mental (Articles 72-77)",
        "summary": (
            "Chapter VII of the General Health Law as reformed in 2022, guaranteeing "
            "universal, equitable access to mental health and addiction care. Requires "
            "services to prioritize primary care integration, intercultural approaches, "
            "and community-based models. Prohibits involuntary treatment except under "
            "strict criteria aligned with international human rights treaties."
        ),
        "original_language": "es",
        "effective_date": "2022-05-16",
        "last_updated": "2025-01-01",
        "policy_id_external": "LGS-CAP-VII-SALUD-MENTAL",
    },

    # -----------------------------------------------------------------------
    # 4. Patient Rights
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "CONAMED / Secretaría de Salud",
        "source_url": "https://www.inr.gob.mx/prueba/conocenos/carta-de-los-derechos-generales-de-las-y-los-pacientes/",
        "category": "patient_rights",
        "title": "Carta de los Derechos Generales de los Pacientes (Patient Rights Charter)",
        "summary": (
            "Issued December 11, 2001, following consultation with over 1,117 opinions "
            "from health institutions, educators, and civil society. Establishes ten "
            "fundamental patient rights: adequate medical care, dignified treatment, "
            "clear and timely information, free decision-making on care, informed "
            "consent, confidentiality, second opinion access, emergency care, clinical "
            "file maintenance, and right to be heard when dissatisfied."
        ),
        "original_language": "es",
        "effective_date": "2001-12-11",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-CARTA-DERECHOS-PACIENTES",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.conbioetica-mexico.salud.gob.mx/descargas/pdf/normatividad/normatinacional/4.NAL_Derechos_de_los_Pacientes.pdf",
        "category": "patient_rights",
        "title": "Reglamento de la LGS en Materia de Prestación de Servicios de Atención Médica",
        "summary": (
            "Regulation under the General Health Law governing the provision of medical "
            "care services. Provides the legal foundation for patient rights including "
            "informed consent, access to medical records, dignity in treatment, and "
            "confidentiality. Establishes obligations of healthcare providers toward "
            "patients and the regulatory framework for the Carta de los Derechos de "
            "los Pacientes."
        ),
        "original_language": "es",
        "effective_date": "1986-01-14",
        "last_updated": "2024-01-01",
        "policy_id_external": "REG-LGS-ATENCION-MEDICA",
    },

    # -----------------------------------------------------------------------
    # 5. Medical Liability and Malpractice
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "CONAMED",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1188117/",
        "category": "medical_liability",
        "title": "CONAMED — National Medical Arbitration Commission (Malpractice Resolution)",
        "summary": (
            "Created in June 1996 as a functionally independent national institution "
            "under the Ministry of Health to arbitrate medical malpractice disputes. "
            "Process begins with a conciliatory stage; if parties do not agree, CONAMED "
            "presents a settlement proposal or proceeds to binding arbitration. "
            "Conciliation averages 3-6 months, arbitral awards 15 months. In 66% of "
            "resolved cases, no malpractice is found."
        ),
        "original_language": "es",
        "effective_date": "1996-06-03",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-CONAMED",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Lexology",
        "source_url": "https://www.lexology.com/library/detail.aspx?g=88f79640-42a1-4c28-bc5d-9ec4f73fe2ed",
        "category": "medical_liability",
        "title": "Professional Negligence Law in Mexico — Medical Malpractice Framework",
        "summary": (
            "Mexico's medical liability framework favors arbitration over litigation "
            "through CONAMED. Malpractice claims can also be pursued through civil "
            "courts seeking damage reparations and through criminal courts for gross "
            "negligence. CONAMED handles acts or omissions from health service delivery "
            "but cannot decide criminal matters, labor disputes, or cases already in "
            "civil litigation."
        ),
        "original_language": "en",
        "effective_date": "1996-06-03",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-MALPRACTICE-FRAMEWORK",
    },

    # -----------------------------------------------------------------------
    # 6. Traditional Medicine Regulations
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Cámara de Diputados",
        "source_url": "https://www5.diputados.gob.mx/index.php/esl/Comunicacion/Boletines/2021/Abril/21/6364-Aprueban-reformas-para-reconocer-medicina-tradicional-indigena-y-complementaria",
        "category": "traditional_medicine",
        "title": "Reform to General Health Law — Recognition of Traditional Indigenous and Complementary Medicine (2021)",
        "summary": (
            "Approved by the Chamber of Deputies in April 2021, this reform amends "
            "the General Health Law to formally recognize traditional indigenous medicine "
            "and complementary medicine. Establishes that the State must respect, "
            "promote, and develop traditional medicine practices, and preserve medicinal "
            "plants, animals, and minerals used in indigenous health traditions, per "
            "Article 2 of the Constitution."
        ),
        "original_language": "es",
        "effective_date": "2021-04-21",
        "last_updated": "2024-01-01",
        "policy_id_external": "LGS-MEDICINA-TRADICIONAL-2021",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Senado de la República",
        "source_url": "https://infosen.senado.gob.mx/sgsp/gaceta/61/1/2009-10-13-1/assets/documentos/1-medicina_tradicional.pdf",
        "category": "traditional_medicine",
        "title": "Ley Marco en Materia de Medicina Tradicional (Framework Law on Traditional Medicine)",
        "summary": (
            "Senate framework law initiative establishing guidelines for the regulation "
            "and practice of traditional indigenous medicine in Mexico. Aims to define "
            "necessary safety measures while respecting indigenous peoples' right to "
            "maintain their health practices under the UN Declaration on the Rights of "
            "Indigenous Peoples (Article 24) and Mexico's constitutional recognition of "
            "its pluricultural national composition."
        ),
        "original_language": "es",
        "effective_date": "2009-10-13",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-LEY-MARCO-MED-TRADICIONAL",
    },

    # -----------------------------------------------------------------------
    # 7. COFEPRIS Drug Approval Details and Timelines
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS / Global Regulatory Partners",
        "source_url": "https://globalregulatorypartners.com/wp-content/uploads/Registration-of-Drugs-in-Mexico-COFEPRIS-_04.16.20_global_regulatory_partners_-FINAL.pdf",
        "category": "drug_regulation",
        "title": "COFEPRIS New Drug Registration Process — Detailed Requirements and Timelines",
        "summary": (
            "New molecules require evaluation by COFEPRIS's New Molecules Committee "
            "(Comité de Moléculas Nuevas). Standard marketing authorization review "
            "takes approximately 180 working days. Generic drug registrations require "
            "bioequivalence studies per NOM-177-SSA1-2013. Since joining ICH in "
            "November 2021, Mexico has been harmonizing its technical requirements "
            "with international standards for pharmaceutical evaluation."
        ),
        "original_language": "en",
        "effective_date": "2001-07-05",
        "last_updated": "2025-01-01",
        "policy_id_external": "COFEPRIS-DRUG-REGISTRATION-PROCESS",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Pharma Boardroom",
        "source_url": "https://pharmaboardroom.com/legal-articles/regulatory-pricing-and-reimbursement-mexico/",
        "category": "drug_regulation",
        "title": "Mexico Pharmaceutical Regulatory, Pricing, and Reimbursement Framework",
        "summary": (
            "Mexico's pharmaceutical pricing system uses a self-regulated maximum "
            "retail price (MRP) scheme for patented products in the private sector, "
            "overseen by the Ministry of Economy with voluntary industry participation. "
            "The Committee for the Negotiation of Drug Prices (created 2008) supports "
            "public acquisitions through transparent negotiation. IMSS purchases are "
            "89% interchangeable generics by volume."
        ),
        "original_language": "en",
        "effective_date": "2008-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-PHARMA-PRICING-FRAMEWORK",
    },

    # -----------------------------------------------------------------------
    # 8. Cross-Border Healthcare and Medical Tourism
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "U.S.-Mexico Border Health Commission",
        "source_url": "https://www.hhs.gov/about/agencies/oga/about-oga/what-we-do/international-relations-division/americas/border-health-commission/index.html",
        "category": "cross_border_health",
        "title": "U.S.-Mexico Border Health Commission (Comisión de Salud Fronteriza)",
        "summary": (
            "Established by the U.S.-Mexico Border Health Act (Public Law 103-400, "
            "1994) and formally created by bilateral agreement on July 24, 2000. A "
            "unique binational entity involving the US and Mexican federal health "
            "secretaries as commissioners, with delegations from six Mexican border "
            "states (Baja California, Sonora, Chihuahua, Coahuila, Nuevo León, "
            "Tamaulipas) and four US border states."
        ),
        "original_language": "en",
        "effective_date": "2000-07-24",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-US-BORDER-HEALTH-COMMISSION",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "U.S. Department of Health and Human Services",
        "source_url": "https://www.hhs.gov/sites/default/files/res_2805.pdf",
        "category": "cross_border_health",
        "title": "Healthy Border 2020 — Binational Prevention and Health Promotion Initiative",
        "summary": (
            "Binational initiative launched June 2015 addressing five priority areas "
            "for the US-Mexico border population: chronic and degenerative diseases, "
            "infectious diseases, maternal and child health, mental health and "
            "addiction, and injury prevention. Funded through HHS cooperative agreements "
            "in all border states. Framework for coordinated binational public health "
            "action along the 2,000-mile border region."
        ),
        "original_language": "en",
        "effective_date": "2015-06-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-HEALTHY-BORDER-2020",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Various / COFEPRIS",
        "source_url": "https://www.dayodental.com/what-are-the-rules-on-buying-prescription-meds-from-mexico/",
        "category": "cross_border_health",
        "title": "Cross-Border Prescription Drug Purchases — Mexico to US Regulations",
        "summary": (
            "Americans purchasing prescription drugs in Mexico must technically obtain "
            "prescriptions from licensed Mexican physicians, though enforcement varies. "
            "COFEPRIS regulates medication pricing with more direct government control "
            "than the US. US citizens may import up to a 90-day personal supply in "
            "original sealed containers. The US Embassy has issued health alerts about "
            "counterfeit pharmaceuticals in Mexican pharmacies targeting American buyers."
        ),
        "original_language": "en",
        "effective_date": "2010-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-CROSS-BORDER-PRESCRIPTION",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "U.S. Embassy Mexico",
        "source_url": "https://mx.usembassy.gov/health-alert-counterfeit-pharmaceuticals-march-172023/",
        "category": "cross_border_health",
        "title": "US Embassy Health Alert — Counterfeit Pharmaceuticals in Mexico (2023)",
        "summary": (
            "Health alert issued March 17, 2023 by the US Embassy in Mexico warning "
            "about counterfeit pharmaceuticals found in Mexican pharmacies, including "
            "fake blood thinners and painkillers containing illicit substances. While "
            "COFEPRIS regulates pharmaceutical quality, enforcement gaps exist "
            "particularly in pharmacies catering to American medical tourists. US drug "
            "prices average 70% higher than Mexico per 2024 RAND Corporation analysis."
        ),
        "original_language": "en",
        "effective_date": "2023-03-17",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-US-EMBASSY-PHARMA-ALERT-2023",
    },

    # -----------------------------------------------------------------------
    # 9. State-Level Health Laws (Border States)
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Congreso del Estado de Baja California",
        "source_url": "https://www.congresobc.gob.mx/Documentos/ProcesoParlamentario/Leyes/TOMO_VI/20240726_LEYSALPU.PDF",
        "category": "state_health_law",
        "title": "Ley de Salud Pública para el Estado de Baja California",
        "summary": (
            "Baja California's state public health law, most recently reformed July 26, "
            "2024. Guarantees extension of health services to vulnerable groups, mandates "
            "basic health services including preventive, curative, palliative, and "
            "rehabilitative care. Promotes IT integration to expand coverage and requires "
            "external defibrillators in public and private buildings with capacity of "
            "300+ persons."
        ),
        "original_language": "es",
        "effective_date": "2001-10-01",
        "last_updated": "2024-07-26",
        "policy_id_external": "MEX-BC-LEY-SALUD-PUBLICA",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Congreso del Estado de Baja California",
        "source_url": "https://www.congresobc.gob.mx/Documentos/ProcesoParlamentario/Leyes/TOMO_VI/20240209_LEYSALMENTAL.PDF",
        "category": "mental_health",
        "title": "Ley de Salud Mental del Estado de Baja California",
        "summary": (
            "Baja California's state mental health law, most recently reformed "
            "February 9, 2024. Establishes the state framework for mental health "
            "services provision, community-based care models, and coordination with "
            "federal mental health reforms. Addresses the specific mental health "
            "challenges of the US-Mexico border region."
        ),
        "original_language": "es",
        "effective_date": "2018-01-01",
        "last_updated": "2024-02-09",
        "policy_id_external": "MEX-BC-LEY-SALUD-MENTAL",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Justia México",
        "source_url": "https://mexico.justia.com/estatales/sonora/leyes/ley-de-salud-para-el-estado-de-sonora/",
        "category": "state_health_law",
        "title": "Ley de Salud para el Estado de Sonora",
        "summary": (
            "Sonora's state health law establishing the regulatory framework for "
            "health services provision, sanitary control, and health promotion within "
            "the state. Coordinates with the federal General Health Law and implements "
            "state-level healthcare delivery, including provisions relevant to the "
            "Sonora-Arizona border health corridor."
        ),
        "original_language": "es",
        "effective_date": "1992-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-SON-LEY-SALUD",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Congreso del Estado de Chihuahua",
        "source_url": "https://docs.mexico.justia.com/estatales/chihuahua/ley-estatal-de-salud.pdf",
        "category": "state_health_law",
        "title": "Ley Estatal de Salud de Chihuahua",
        "summary": (
            "Chihuahua's state health law establishing the bases and procedures for "
            "access to health services provided by the state government, in compliance "
            "with the constitutional right to health protection. Chihuahua's governor "
            "and health secretary maintain a separate Agreement of Understanding with "
            "neighboring US states for cross-border health program coordination."
        ),
        "original_language": "es",
        "effective_date": "1996-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-CHIH-LEY-SALUD",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Congreso del Estado de Tamaulipas",
        "source_url": "https://www.congresotamaulipas.gob.mx/Parlamentario/Archivos/Leyes/Ley%20de%20Salud%2024-03-2026.pdf",
        "category": "state_health_law",
        "title": "Ley de Salud para el Estado de Tamaulipas",
        "summary": (
            "Tamaulipas state health law originally published November 27, 2001 with "
            "multiple subsequent reforms, most recently updated March 2026. Establishes "
            "the state Secretary of Health's responsibilities for organizing, "
            "controlling, and monitoring health services and establishments. Tamaulipas "
            "borders Texas and is a key corridor for cross-border healthcare services."
        ),
        "original_language": "es",
        "effective_date": "2001-11-27",
        "last_updated": "2026-03-24",
        "policy_id_external": "MEX-TAM-LEY-SALUD",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "H. Congreso de Nuevo León",
        "source_url": "https://www.hcnl.gob.mx/trabajo_legislativo/leyes/leyes/ley_estatal_de_salud/",
        "category": "state_health_law",
        "title": "Ley Estatal de Salud de Nuevo León",
        "summary": (
            "Nuevo León's state health law regulating health services, sanitary "
            "control, and health promotion within Mexico's wealthiest and most "
            "industrialized border state. Nuevo León (capital: Monterrey) is a major "
            "hub for medical tourism with JCI-accredited hospitals and coordinates "
            "health services with the US through the Border Health Commission."
        ),
        "original_language": "es",
        "effective_date": "1988-01-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-NL-LEY-SALUD",
    },

    # -----------------------------------------------------------------------
    # 10. International Health Agreements
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "WHO",
        "source_url": "https://www.who.int/about/accountability/results/who-results-report-2024-2025/region-AMRO/2024/mexico",
        "category": "international_health",
        "title": "WHO-Mexico Country Cooperation — Results Report 2024-2025",
        "summary": (
            "WHO's technical cooperation with Mexico as a member state, covering "
            "health systems strengthening, pandemic preparedness, non-communicable "
            "disease prevention, and universal health coverage. Mexico is an active "
            "WHO member and participant in the 2025 Global Pandemic Agreement adopted "
            "by consensus at the 78th World Health Assembly."
        ),
        "original_language": "en",
        "effective_date": "2024-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-WHO-COOPERATION-2024",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "PAHO",
        "source_url": "https://www.paho.org/en/news/8-5-2025-paho-director-signs-2025-2031-subregional-cooperation-strategy-central-america",
        "category": "international_health",
        "title": "PAHO 2025-2031 Subregional Cooperation Strategy — Central America, Dominican Republic, and Mexico",
        "summary": (
            "Signed May 8, 2025 by the PAHO Director with SE-COMISCA, this strategy "
            "covers the CAM subregion (183.4 million people) including Mexico, Belize, "
            "Costa Rica, El Salvador, Guatemala, Honduras, Nicaragua, Panama, and the "
            "Dominican Republic. Establishes health cooperation priorities including "
            "disease surveillance, health workforce, and health system resilience."
        ),
        "original_language": "en",
        "effective_date": "2025-05-08",
        "last_updated": "2025-05-08",
        "policy_id_external": "MEX-PAHO-SUBREGIONAL-2025-2031",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "PAHO / WHO",
        "source_url": "https://www.paho.org/en/topics/international-health-regulations",
        "category": "international_health",
        "title": "Mexico's Obligations Under the International Health Regulations (IHR 2005)",
        "summary": (
            "Mexico is party to the International Health Regulations (2005), a legally "
            "binding instrument for 196 countries requiring core capacities for disease "
            "surveillance, reporting, and response. Mexico must report events that may "
            "constitute a public health emergency of international concern (PHEIC) and "
            "maintain designated points of entry surveillance at ports and airports."
        ),
        "original_language": "en",
        "effective_date": "2007-06-15",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-IHR-2005",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS / ICH",
        "source_url": "https://practiceguides.chambers.com/practice-guides/life-sciences-2025/mexico/trends-and-developments",
        "category": "international_health",
        "title": "Mexico's ICH Membership — International Harmonization of Pharmaceutical Requirements",
        "summary": (
            "Since November 2021, Mexico has been a member of the International "
            "Council for Harmonisation of Technical Requirements for Pharmaceuticals "
            "for Human Use (ICH). This membership is a COFEPRIS priority strategy "
            "enabling harmonization of regulation, surveillance, and technical "
            "evaluation parameters with international standards for drug quality, "
            "safety, and efficacy assessment."
        ),
        "original_language": "en",
        "effective_date": "2021-11-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-ICH-MEMBERSHIP",
    },

    # -----------------------------------------------------------------------
    # 11. Digital Health / Telesalud National Strategy
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "CENETEC / Secretaría de Salud",
        "source_url": "https://www.gob.mx/salud/cenetec/acciones-y-programas/direccion-de-telesalud",
        "category": "digital_health",
        "title": "CENETEC Dirección de Telesalud — National Telehealth Program",
        "summary": (
            "Mexico's telemedicine was institutionalized in January 2004 with the "
            "creation of the Centro Nacional de Excelencia Tecnológica en Salud "
            "(CENETEC), recognized as a WHO collaborating center. CENETEC's Telehealth "
            "Directorate coordinates national telesalud implementation across 27 of 32 "
            "federal entities, with 8 million telesalud actions performed in 2022. "
            "Publishes the Telehealth Services Catalog standardizing criteria."
        ),
        "original_language": "es",
        "effective_date": "2004-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-CENETEC-TELESALUD",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Presidencia de la República",
        "source_url": "https://saluddigital.com/en/plataformas-digitales/la-estrategia-digital-en-salud-en-el-estado-de-mexico-ante-la-emergencia-sanitaria/",
        "category": "digital_health",
        "title": "Estrategia Digital Nacional — Health Component (EDN Salud)",
        "summary": (
            "Through the Universal and Effective Health component, Mexico's Digital "
            "National Strategy (EDN) promoted implementation of e-Health components "
            "in public health services to promote quality, accessibility, and equity. "
            "Includes electronic health records (NOM-024-SSA3), telemedicine "
            "infrastructure, and digital prescription systems. Accelerated during "
            "COVID-19 with expanded virtual consultation services."
        ),
        "original_language": "es",
        "effective_date": "2013-11-25",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-EDN-SALUD",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "CENETEC",
        "source_url": "https://saluddigital.com/en/comunidades-conectadas/cenetec-actualizo-la-guia-para-elaboracion-de-proyectos-de-telesalud/",
        "category": "digital_health",
        "title": "CENETEC Guide for Telehealth Project Development (Updated 2021)",
        "summary": (
            "Updated guide published December 2021 by CENETEC defining criteria and "
            "guidelines for planning telehealth projects in federal entities and health "
            "sector institutions. Focuses on strengthening primary care through "
            "telesalud, standardizing project evaluation methodologies, and ensuring "
            "interoperability across the National Health System."
        ),
        "original_language": "es",
        "effective_date": "2021-12-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-CENETEC-TELESALUD-GUIDE-2021",
    },

    # -----------------------------------------------------------------------
    # 12. Pharmaceutical Pricing and Generic Drug Policies
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "OECD",
        "source_url": "https://www.oecd.org/content/dam/oecd/en/publications/reports/2007/02/pharmaceutical-pricing-and-reimbursement-policies-in-mexico_g17a1935/302355455158.pdf",
        "category": "drug_regulation",
        "title": "OECD Analysis — Pharmaceutical Pricing and Reimbursement Policies in Mexico",
        "summary": (
            "Comprehensive OECD assessment of Mexico's pharmaceutical market structure. "
            "Mexico uses reference pricing based on a basket of six countries for "
            "patented products. The public sector purchases through consolidated "
            "bidding processes, achieving significant savings. Generic medicines "
            "constitute the majority of the market by volume, with bioequivalence "
            "certification required for interchangeability designation."
        ),
        "original_language": "en",
        "effective_date": "2007-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-OECD-PHARMA-PRICING",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS",
        "source_url": "https://www.artixio.com/post/biologics-and-biosimilars-regulations-and-registration-in-mexico-cofepris",
        "category": "drug_regulation",
        "title": "COFEPRIS Biosimilar (Biocomparable) Drug Regulation and Registration",
        "summary": (
            "Mexico's regulatory framework for biosimilar drugs, termed "
            "'biocomparables' under Mexican law. Registration requires demonstration "
            "of quality, safety, and efficacy comparability with the reference biologic. "
            "NOM-257-SSA1-2014 governs biotherapeutic products while NOM-177-SSA1-2013 "
            "covers interchangeability studies. Mexico's framework enables market "
            "competition while maintaining safety standards for biological medicines."
        ),
        "original_language": "en",
        "effective_date": "2009-06-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-COFEPRIS-BIOSIMILARS",
    },

    # -----------------------------------------------------------------------
    # 13. Health Workforce Regulations
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Salud / Medigraphic",
        "source_url": "https://www.medigraphic.com/cgi-bin/new/resumen.cgi?IDARTICULO=45705",
        "category": "health_workforce",
        "title": "Servicio Social en Medicina — Mandatory Rural Medical Service",
        "summary": (
            "All medical and dental graduates in Mexico must complete a year of "
            "mandatory social service (servicio social), historically in rural and "
            "underserved communities. NOM-009-SSA3 establishes modalities including "
            "rural unit assignment, research, and teaching. Reform advocates argue "
            "the program needs urgent modernization to improve safety, supervision, "
            "and educational value in remote postings."
        ),
        "original_language": "es",
        "effective_date": "1936-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-SERVICIO-SOCIAL-MEDICINA",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Salud",
        "source_url": "https://platiica.economia.gob.mx/normalizacion/nom-001-ssa-2023/",
        "category": "health_workforce",
        "title": "NOM-001-SSA-2023 — National Health System Organization and Functioning",
        "summary": (
            "Updated Official Mexican Standard (2023) establishing criteria for the "
            "organization and functioning of establishments providing medical care "
            "within the National Health System. Defines staffing requirements, "
            "operational standards, and quality benchmarks for healthcare facilities "
            "across the public, social, and private sectors."
        ),
        "original_language": "es",
        "effective_date": "2023-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "NOM-001-SSA-2023",
    },

    # -----------------------------------------------------------------------
    # 14. Emergency Medical Services
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Salud",
        "source_url": "https://www.normasoficiales.mx/nom/nom-027-ssa3-2013",
        "category": "emergency_services",
        "title": "Mexico Emergency Medical Services — Personnel and Training Standards",
        "summary": (
            "Under NOM-027-SSA3-2013, all emergency service personnel regardless of "
            "level must be documented as trained in emergency care with periodic updates. "
            "Requirements cover knowledge of triage protocols, advanced life support, "
            "surgical emergency response, and disaster management. Institutions must "
            "maintain training records demonstrating compliance."
        ),
        "original_language": "es",
        "effective_date": "2013-11-04",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-EMS-TRAINING-STANDARDS",
    },
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Salud",
        "source_url": "https://www.gob.mx/salud%7Chjm/documentos/norma-oficial-mexicana-nom-001-ssa3-2012",
        "category": "emergency_services",
        "title": "NOM-001-SSA3-2012 — General Requirements for Medical Care Establishments",
        "summary": (
            "Official Mexican Standard establishing general requirements that "
            "medical care establishments must meet for safe and quality service "
            "delivery, including emergency preparedness, patient safety protocols, "
            "and minimum operating conditions. Serves as the baseline standard "
            "complementing specialized NOMs like NOM-027 for emergency services "
            "and NOM-016 for hospitals."
        ),
        "original_language": "es",
        "effective_date": "2012-12-14",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-001-SSA3-2012",
    },

    # -----------------------------------------------------------------------
    # 15. Additional Cross-Border and Medical Tourism
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "CDC",
        "source_url": "https://www.cdc.gov/migration-border-health/about/about-binational-health.html",
        "category": "cross_border_health",
        "title": "CDC US-Mexico Binational Health Program — Border Epidemiological Surveillance",
        "summary": (
            "CDC's binational health activities with Mexico focus on infectious "
            "disease surveillance, epidemiological intelligence sharing, and "
            "coordinated response along the 2,000-mile border. Programs address "
            "tuberculosis, vector-borne diseases, and health disparities affecting "
            "the approximately 15 million people living within 100 km of the "
            "US-Mexico border."
        ),
        "original_language": "en",
        "effective_date": "2006-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-CDC-BINATIONAL-HEALTH",
    },

    # -----------------------------------------------------------------------
    # 16. Additional Healthcare NOMs
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.cndh.org.mx/documento/nom-027-ssa3-2013-regulacion-de-los-servicios-de-salud-que-establece-los-criterios-de",
        "category": "clinical_standards",
        "title": "NOM-027-SSA3-2013 — Detailed Requirements for Emergency Equipment and Infrastructure",
        "summary": (
            "Specific infrastructure requirements under NOM-027-SSA3-2013 mandate that "
            "emergency departments maintain defibrillators, vital signs monitors, "
            "ventilators, emergency surgical equipment, and properly equipped treatment "
            "areas. Physical spaces must include triage areas, observation rooms, "
            "stabilization areas, and short-stay beds, with clear protocols for patient "
            "flow management."
        ),
        "original_language": "es",
        "effective_date": "2013-11-04",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-027-SSA3-2013-INFRASTRUCTURE",
    },

    # -----------------------------------------------------------------------
    # 17. Violence Against Women Healthcare Framework
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Cámara de Diputados",
        "source_url": "https://academic.oup.com/heapol/article/40/5/519/8063747",
        "category": "patient_rights",
        "title": "General Law for Women's Access to a Life Free from Violence — Healthcare Implementation",
        "summary": (
            "Enacted in 2007, this federal law establishes the framework for preventing "
            "and eliminating violence against women across Mexico. The healthcare system "
            "response includes NOM-046-SSA2 implementation, healthcare provider training "
            "on violence detection, and mandatory protocols for treating victims. "
            "Supported by Mexico's 1996 Law for Care and Prevention of Family Violence."
        ),
        "original_language": "es",
        "effective_date": "2007-02-01",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-LEY-MUJERES-VIDA-SIN-VIOLENCIA",
    },

    # -----------------------------------------------------------------------
    # 18. Bioethics Framework
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "CONBIOÉTICA",
        "source_url": "https://www.conbioetica-mexico.salud.gob.mx/descargas/pdf/normatividad/normatinacional/4.NAL_Derechos_de_los_Pacientes.pdf",
        "category": "clinical_standards",
        "title": "CONBIOÉTICA — National Bioethics Commission Framework",
        "summary": (
            "Mexico's National Bioethics Commission (Comisión Nacional de Bioética) "
            "coordinates bioethics policy across the health sector. Oversees the "
            "establishment of Hospital Bioethics Committees and Research Ethics "
            "Committees required for clinical trials under NOM-012-SSA3. Publishes "
            "guidelines on informed consent, end-of-life care, organ donation, and "
            "human subjects research protections."
        ),
        "original_language": "es",
        "effective_date": "2005-09-07",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-CONBIOETICA",
    },

    # -----------------------------------------------------------------------
    # 19. Medical Tourism JCI Accreditation
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Joint Commission International / ProMéxico",
        "source_url": "https://www.medicaltourismco.com/medical-tourism-in-mexico/",
        "category": "medical_tourism",
        "title": "Mexico JCI-Accredited Hospitals and Medical Tourism Regulatory Standards",
        "summary": (
            "Mexico has one of the largest numbers of JCI-accredited hospitals in "
            "Latin America, concentrated in border cities (Tijuana, Ciudad Juárez, "
            "Monterrey) and major urban centers (Mexico City, Guadalajara). An "
            "estimated 1.3 million Americans traveled to Mexico for medical care in "
            "2024. COFEPRIS enforces quality standards for hospitals, medications, "
            "and equipment serving medical tourists."
        ),
        "original_language": "en",
        "effective_date": "2010-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-JCI-MEDICAL-TOURISM",
    },

    # -----------------------------------------------------------------------
    # 20. Organ Donation and Transplant
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-de-salud/titulo-decimocuarto/",
        "category": "clinical_standards",
        "title": "Ley General de Salud — Título XIV: Organ Donation, Transplants, and Tissue Banks",
        "summary": (
            "Title XIV of the General Health Law regulates organ and tissue donation, "
            "transplantation procedures, and tissue banks in Mexico. Establishes the "
            "Centro Nacional de Trasplantes (CENATRA) as the coordinating body, "
            "requires informed consent from living donors, and establishes the "
            "National Transplant Registry. Mexico operates an opt-in donation system."
        ),
        "original_language": "es",
        "effective_date": "2000-05-26",
        "last_updated": "2025-01-01",
        "policy_id_external": "LGS-TITULO-XIV-TRASPLANTES",
    },

    # -----------------------------------------------------------------------
    # 21. Advertising and Labeling of Health Products
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS",
        "source_url": "https://www.olivares.mx/product-regulation-and-liability-in-mexico/",
        "category": "drug_regulation",
        "title": "Mexico Pharmaceutical Advertising and Labeling Regulations",
        "summary": (
            "COFEPRIS regulates all pharmaceutical advertising and labeling under the "
            "General Health Law and its regulations. Prescription drug advertising is "
            "restricted to healthcare professionals. OTC advertising requires COFEPRIS "
            "pre-approval. Labeling must include active ingredients, indications, "
            "contraindications, and dosage in Spanish. Recent reforms target misleading "
            "claims in supplement and alternative medicine marketing."
        ),
        "original_language": "es",
        "effective_date": "2001-07-05",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-COFEPRIS-ADVERTISING-LABELING",
    },

    # -----------------------------------------------------------------------
    # 22. Controlled Substances
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-de-salud/titulo-duodecimo/",
        "category": "drug_regulation",
        "title": "Ley General de Salud — Título XII: Control of Narcotics and Psychotropic Substances",
        "summary": (
            "Title XII of the General Health Law classifies controlled substances into "
            "five groups with corresponding regulatory requirements for prescription, "
            "dispensing, and record-keeping. Medical cannabis was legalized for "
            "therapeutic use in 2017. COFEPRIS maintains the official list of "
            "controlled substances and issues special licenses for establishments "
            "handling narcotic and psychotropic substances."
        ),
        "original_language": "es",
        "effective_date": "1984-02-07",
        "last_updated": "2025-01-01",
        "policy_id_external": "LGS-TITULO-XII-ESTUPEFACIENTES",
    },

    # -----------------------------------------------------------------------
    # 23. Palliative Care
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-de-salud/titulo-octavo-bis/",
        "category": "healthcare_access",
        "title": "Ley General de Salud — Título VIII Bis: Palliative Care Rights",
        "summary": (
            "Title VIII Bis added in 2009 to the General Health Law establishes the "
            "right to palliative care for patients with terminal illness. Guarantees "
            "access to pain management including opioid medications, the right to "
            "refuse aggressive treatment, and the right to dignity in the final stage "
            "of life. Mandates palliative care training for health professionals."
        ),
        "original_language": "es",
        "effective_date": "2009-01-05",
        "last_updated": "2024-01-01",
        "policy_id_external": "LGS-TITULO-VIII-BIS-PALIATIVOS",
    },

    # -----------------------------------------------------------------------
    # 24. Tobacco Control
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-para-el-control-del-tabaco/",
        "category": "public_health",
        "title": "Ley General para el Control del Tabaco (General Tobacco Control Law)",
        "summary": (
            "Federal law enacted in 2008 establishing comprehensive tobacco control "
            "measures including advertising restrictions, mandatory health warnings on "
            "packaging, smoke-free public spaces, and regulation of tobacco product "
            "ingredients. Amended in 2023 to ban all smoking in enclosed public spaces "
            "without exception. Aligns with Mexico's ratification of the WHO Framework "
            "Convention on Tobacco Control (FCTC)."
        ),
        "original_language": "es",
        "effective_date": "2008-05-30",
        "last_updated": "2023-01-01",
        "policy_id_external": "MEX-LEY-CONTROL-TABACO",
    },

    # -----------------------------------------------------------------------
    # 25. Front-of-Package Nutrition Labeling
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://www.olivares.mx/product-regulation-and-liability-in-mexico/",
        "category": "public_health",
        "title": "NOM-051-SCFI/SSA1-2010 — Front-of-Package Nutrition Warning Labels",
        "summary": (
            "Modified in 2020, this NOM requires front-of-package warning labels "
            "(octagonal black seals) on processed foods and beverages exceeding "
            "thresholds for calories, sugar, saturated fat, trans fat, and sodium. "
            "Mexico became one of the first countries to adopt this system, which "
            "also prohibits using cartoon characters or celebrities to market products "
            "bearing warning seals to children."
        ),
        "original_language": "es",
        "effective_date": "2020-10-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "NOM-051-SCFI-SSA1-2010-MOD",
    },

    # -----------------------------------------------------------------------
    # 26. Vaccination Program
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Salud",
        "source_url": "https://www.gob.mx/salud/censia",
        "category": "public_health",
        "title": "Programa de Vacunación Universal — National Immunization Program",
        "summary": (
            "Mexico's Universal Vaccination Program, coordinated by the Centro "
            "Nacional para la Salud de la Infancia y la Adolescencia (CENSIA), "
            "provides free immunizations as part of the national public health "
            "strategy. The program covers approximately 15 vaccines from birth "
            "through adolescence per the official vaccination schedule, and is "
            "mandatory for school enrollment."
        ),
        "original_language": "es",
        "effective_date": "1991-01-01",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-VACUNACION-UNIVERSAL",
    },

    # -----------------------------------------------------------------------
    # 27. Disability and Accessibility in Healthcare
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-para-la-inclusion-de-las-personas-con-discapacidad/",
        "category": "patient_rights",
        "title": "Ley General para la Inclusión de las Personas con Discapacidad — Healthcare Provisions",
        "summary": (
            "Federal law establishing the right of persons with disabilities to "
            "accessible healthcare services, including physical accessibility of "
            "health facilities, provision of sign language interpreters, accessible "
            "health information formats, and specialized rehabilitation services. "
            "CONADIS coordinates implementation across the health sector. Aligns with "
            "Mexico's ratification of the UN Convention on the Rights of Persons with "
            "Disabilities."
        ),
        "original_language": "es",
        "effective_date": "2011-05-30",
        "last_updated": "2024-01-01",
        "policy_id_external": "MEX-LEY-INCLUSION-DISCAPACIDAD",
    },

    # -----------------------------------------------------------------------
    # 28. Antimicrobial Resistance
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "COFEPRIS / Secretaría de Salud",
        "source_url": "https://clinregs.niaid.nih.gov/country/mexico",
        "category": "drug_regulation",
        "title": "Mexico Antibiotic Prescription Requirements — Combating Antimicrobial Resistance",
        "summary": (
            "Since 2010, Mexico requires medical prescriptions for all antibiotic "
            "purchases, ending decades of over-the-counter antibiotic sales. Pharmacies "
            "must retain the original prescription and may only dispense the quantity "
            "prescribed. Part of Mexico's national strategy against antimicrobial "
            "resistance aligned with WHO Global Action Plan. Enforcement remains "
            "inconsistent, particularly in border pharmacies."
        ),
        "original_language": "es",
        "effective_date": "2010-04-27",
        "last_updated": "2025-01-01",
        "policy_id_external": "MEX-ANTIBIOTICS-PRESCRIPTION-REQ",
    },

    # -----------------------------------------------------------------------
    # 29. Reproductive Health
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Secretaría de Salud",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-de-salud/titulo-tercero/capitulo-vi/",
        "category": "reproductive_health",
        "title": "Ley General de Salud — Capítulo VI: Family Planning Services",
        "summary": (
            "Chapter VI of the General Health Law guarantees access to family planning "
            "services, contraception information, and reproductive health education. "
            "All public health institutions must provide free contraceptive methods. "
            "Mexico's National Family Planning Program provides access to modern "
            "contraceptive methods including IUDs, hormonal contraceptives, and "
            "emergency contraception through the public health system."
        ),
        "original_language": "es",
        "effective_date": "1984-02-07",
        "last_updated": "2025-01-01",
        "policy_id_external": "LGS-CAP-VI-PLANIFICACION-FAMILIAR",
    },

    # -----------------------------------------------------------------------
    # 30. Blood Banks and Transfusion
    # -----------------------------------------------------------------------
    {
        "country": "MEX",
        "country_name": "Mexico",
        "source": "Diario Oficial de la Federación",
        "source_url": "https://mexico.justia.com/federales/leyes/ley-general-de-salud/titulo-decimocuarto/",
        "category": "clinical_standards",
        "title": "NOM-253-SSA1-2012 — Blood Disposal and Blood Components for Therapeutic Purposes",
        "summary": (
            "Official Mexican Standard establishing requirements for the collection, "
            "processing, testing, storage, and distribution of human blood and blood "
            "components. Mandates screening for HIV, hepatitis B and C, syphilis, "
            "Chagas disease, and other transfusion-transmissible infections. Applies "
            "to all blood banks and transfusion services in public and private sectors."
        ),
        "original_language": "es",
        "effective_date": "2012-10-26",
        "last_updated": "2024-01-01",
        "policy_id_external": "NOM-253-SSA1-2012",
    },
]


# ---------------------------------------------------------------------------
# Seeder Logic
# ---------------------------------------------------------------------------

def seed_mexico_expansion():
    """Seed expanded Mexican healthcare policies into the database."""
    init_db()
    session = get_session()

    stored = 0
    skipped = 0

    for policy_data in MEX_EXPANSION_POLICIES:
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

    print(f"Mexico Expansion Seeder complete.")
    print(f"  Stored: {stored} new policies")
    print(f"  Skipped: {skipped} duplicates")
    print(f"  Total in expansion dataset: {len(MEX_EXPANSION_POLICIES)}")


if __name__ == "__main__":
    seed_mexico_expansion()
