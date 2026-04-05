"""One-time script to seed CMS data from pre-fetched results."""

from src.data_ingestion.cms_seeder import seed_from_preloaded

# Data pulled from CMS Coverage API via Claude Code's built-in tool
# These are real National Coverage Determinations (NCDs) from cms.gov
CMS_NCDS = [
    {"document_id": 382, "document_display_id": "20.40", "title": "Renal Denervation (RDN) for Uncontrolled Hypertension", "chapter": "20", "is_lab": 0, "last_updated": "03/24/2026", "url": "/data/ncd?ncdid=382&ncdver=1"},
    {"document_id": 383, "document_display_id": "20.39", "title": "Cardiac Contractility Modulation (CCM) for Heart Failure (HF)", "chapter": "20", "is_lab": 0, "last_updated": "03/09/2026", "url": "/data/ncd?ncdid=383&ncdver=1"},
    {"document_id": 358, "document_display_id": "150.13", "title": "Percutaneous Image-Guided Lumbar Decompression for Lumbar Spinal Stenosis", "chapter": "150", "is_lab": 0, "last_updated": "03/04/2026", "url": "/data/ncd?ncdid=358&ncdver=2"},
    {"document_id": 119, "document_display_id": "240.1", "title": "Lung Volume Reduction Surgery (Reduction Pneumoplasty)", "chapter": "240", "is_lab": 0, "last_updated": "03/03/2026", "url": "/data/ncd?ncdid=119&ncdver=3"},
    {"document_id": 361, "document_display_id": "210.13", "title": "Screening for Hepatitis C Virus (HCV) in Adults", "chapter": "210", "is_lab": 0, "last_updated": "02/24/2026", "url": "/data/ncd?ncdid=361&ncdver=1"},
    {"document_id": 322, "document_display_id": "110.21", "title": "Erythropoiesis Stimulating Agents (ESAs) in Cancer and Related Neoplastic Conditions", "chapter": "110", "is_lab": 0, "last_updated": "02/10/2026", "url": "/data/ncd?ncdid=322&ncdver=1"},
    {"document_id": 354, "document_display_id": "160.27", "title": "Transcutaneous Electrical Nerve Stimulation (TENS) for Chronic Low Back Pain (CLBP)", "chapter": "160", "is_lab": 0, "last_updated": "02/10/2026", "url": "/data/ncd?ncdid=354&ncdver=1"},
    {"document_id": 110, "document_display_id": "20.4", "title": "Implantable Cardioverter Defibrillators (ICDs)", "chapter": "20", "is_lab": 0, "last_updated": "02/10/2026", "url": "/data/ncd?ncdid=110&ncdver=5"},
    {"document_id": 331, "document_display_id": "220.6.17", "title": "Positron Emission Tomography (FDG) for Oncologic Conditions", "chapter": "220", "is_lab": 0, "last_updated": "02/06/2026", "url": "/data/ncd?ncdid=331&ncdver=4"},
    {"document_id": 230, "document_display_id": "160.18", "title": "Vagus Nerve Stimulation (VNS)", "chapter": "160", "is_lab": 0, "last_updated": "02/06/2026", "url": "/data/ncd?ncdid=230&ncdver=3"},
    {"document_id": 309, "document_display_id": "110.18", "title": "Aprepitant for Chemotherapy-Induced Emesis", "chapter": "110", "is_lab": 0, "last_updated": "02/06/2026", "url": "/data/ncd?ncdid=309&ncdver=2"},
    {"document_id": 129, "document_display_id": "250.4", "title": "Treatment of Actinic Keratosis", "chapter": "250", "is_lab": 0, "last_updated": "02/06/2026", "url": "/data/ncd?ncdid=129&ncdver=1"},
    {"document_id": 372, "document_display_id": "90.2", "title": "Next Generation Sequencing (NGS)", "chapter": "90", "is_lab": 0, "last_updated": "02/06/2026", "url": "/data/ncd?ncdid=372&ncdver=2"},
    {"document_id": 352, "document_display_id": "210.10", "title": "Screening for STIs and High-Intensity Behavioral Counseling", "chapter": "210", "is_lab": 0, "last_updated": "02/06/2026", "url": "/data/ncd?ncdid=352&ncdver=1"},
    {"document_id": 190, "document_display_id": "280.1", "title": "Durable Medical Equipment Reference List", "chapter": "280", "is_lab": 0, "last_updated": "02/03/2026", "url": "/data/ncd?ncdid=190&ncdver=4"},
    {"document_id": 380, "document_display_id": "240.9", "title": "Noninvasive Positive Pressure Ventilation (NIPPV) for COPD", "chapter": "240", "is_lab": 0, "last_updated": "01/30/2026", "url": "/data/ncd?ncdid=380&ncdver=1"},
    {"document_id": 167, "document_display_id": "190.34", "title": "Fecal Occult Blood Test", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=167&ncdver=1"},
    {"document_id": 166, "document_display_id": "190.33", "title": "Hepatitis Panel/Acute Hepatitis Panel", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=166&ncdver=1"},
    {"document_id": 153, "document_display_id": "190.32", "title": "Gamma Glutamyl Transferase", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=153&ncdver=1"},
    {"document_id": 152, "document_display_id": "190.31", "title": "Prostate Specific Antigen", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=152&ncdver=1"},
    {"document_id": 100, "document_display_id": "190.21", "title": "Glycated Hemoglobin/Glycated Protein", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=100&ncdver=1"},
    {"document_id": 98, "document_display_id": "190.20", "title": "Blood Glucose Testing", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=98&ncdver=2"},
    {"document_id": 101, "document_display_id": "190.22", "title": "Thyroid Testing", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=101&ncdver=1"},
    {"document_id": 102, "document_display_id": "190.23", "title": "Lipid Testing", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=102&ncdver=2"},
    {"document_id": 53, "document_display_id": "190.14", "title": "Human Immunodeficiency Virus (HIV) Testing (Diagnosis)", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=53&ncdver=3"},
    {"document_id": 61, "document_display_id": "190.15", "title": "Blood Counts", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=61&ncdver=1"},
    {"document_id": 80, "document_display_id": "190.17", "title": "Prothrombin Time (PT)", "chapter": "190", "is_lab": 1, "last_updated": "01/06/2026", "url": "/data/ncd?ncdid=80&ncdver=1"},
    {"document_id": 377, "document_display_id": "210.15", "title": "Pre-Exposure Prophylaxis (PrEP) for HIV Prevention", "chapter": "210", "is_lab": 0, "last_updated": "09/30/2025", "url": "/data/ncd?ncdid=377&ncdver=1"},
    {"document_id": 281, "document_display_id": "210.3", "title": "Colorectal Cancer Screening Tests", "chapter": "210", "is_lab": 0, "last_updated": "09/30/2025", "url": "/data/ncd?ncdid=281&ncdver=7"},
    {"document_id": 185, "document_display_id": "210.2", "title": "Screening Pap Smears and Pelvic Examinations", "chapter": "210", "is_lab": 0, "last_updated": "09/30/2025", "url": "/data/ncd?ncdid=185&ncdver=3"},
    {"document_id": 379, "document_display_id": "20.37", "title": "Transcatheter Tricuspid Valve Replacement (TTVR)", "chapter": "20", "is_lab": 0, "last_updated": "09/23/2025", "url": "/data/ncd?ncdid=379&ncdver=1"},
    {"document_id": 366, "document_display_id": "110.23", "title": "Stem Cell Transplantation", "chapter": "110", "is_lab": 0, "last_updated": "10/27/2025", "url": "/data/ncd?ncdid=366&ncdver=2"},
    {"document_id": 291, "document_display_id": "110.17", "title": "Anti-Cancer Chemotherapy for Colorectal Cancer", "chapter": "110", "is_lab": 0, "last_updated": "12/09/2025", "url": "/data/ncd?ncdid=291&ncdver=1"},
    {"document_id": 249, "document_display_id": "230.18", "title": "Sacral Nerve Stimulation For Urinary Incontinence", "chapter": "230", "is_lab": 0, "last_updated": "12/08/2025", "url": "/data/ncd?ncdid=249&ncdver=1"},
    {"document_id": 267, "document_display_id": "20.16", "title": "Cardiac Output Monitoring by Thoracic Electrical Bioimpedance", "chapter": "20", "is_lab": 0, "last_updated": "09/30/2025", "url": "/data/ncd?ncdid=267&ncdver=3"},
]

if __name__ == "__main__":
    seed_from_preloaded(CMS_NCDS)
