"""Seed ALL CMS NCDs from the three batches we pulled."""

import json
from src.data_ingestion.cms_seeder import seed_from_preloaded

# Batch 3 (final 94 NCDs) - inline since we have them
BATCH3 = [
    {"document_id": 140, "document_display_id": "70.3", "title": "Physician's Office within an Institution Coverage of Services and Supplies Incident to a Physician's Services", "chapter": "70", "is_lab": 0, "last_updated": "06/12/2020", "url": "/data/ncd?ncdid=140&ncdver=1"},
    {"document_id": 244, "document_display_id": "160.19", "title": "Phrenic Nerve Stimulator", "chapter": "160", "is_lab": 0, "last_updated": "06/12/2020", "url": "/data/ncd?ncdid=244&ncdver=1"},
    {"document_id": 27, "document_display_id": "130.2", "title": "Outpatient Hospital Services for Treatment of Alcoholism", "chapter": "130", "is_lab": 0, "last_updated": "06/12/2020", "url": "/data/ncd?ncdid=27&ncdver=1"},
    {"document_id": 93, "document_display_id": "110.16", "title": "Nonselective (Random) Transfusions and Living Related Donor Specific Transfusions (DST) in Kidney Transplantation", "chapter": "110", "is_lab": 0, "last_updated": "06/12/2020", "url": "/data/ncd?ncdid=93&ncdver=1"},
    {"document_id": 89, "document_display_id": "170.2", "title": "Melodic Intonation Therapy", "chapter": "170", "is_lab": 0, "last_updated": "06/12/2020", "url": "/data/ncd?ncdid=89&ncdver=1"},
    {"document_id": 133, "document_display_id": "40.4", "title": "Insulin Syringe", "chapter": "40", "is_lab": 0, "last_updated": "06/11/2020", "url": "/data/ncd?ncdid=133&ncdver=1"},
    {"document_id": 317, "document_display_id": "280.15", "title": "INDEPENDENCE iBOT 4000 Mobility System", "chapter": "280", "is_lab": 0, "last_updated": "06/11/2020", "url": "/data/ncd?ncdid=317&ncdver=1"},
    {"document_id": 233, "document_display_id": "80.4", "title": "Hydrophilic Contact Lenses", "chapter": "80", "is_lab": 0, "last_updated": "06/11/2020", "url": "/data/ncd?ncdid=233&ncdver=1"},
    {"document_id": 136, "document_display_id": "80.1", "title": "Hydrophilic Contact Lens For Corneal Bandage", "chapter": "80", "is_lab": 0, "last_updated": "06/11/2020", "url": "/data/ncd?ncdid=136&ncdver=1"},
    {"document_id": 210, "document_display_id": "290.2", "title": "Home Health Nurses' Visits to Patients Requiring Heparin Injection", "chapter": "290", "is_lab": 0, "last_updated": "06/11/2020", "url": "/data/ncd?ncdid=210&ncdver=1"},
    {"document_id": 162, "document_display_id": "20.13", "title": "HIS Bundle Study", "chapter": "20", "is_lab": 0, "last_updated": "06/11/2020", "url": "/data/ncd?ncdid=162&ncdver=1"},
    {"document_id": 4, "document_display_id": "240.3", "title": "Heat Treatment, Including the Use of Diathermy and Ultra-Sound for Pulmonary Conditions", "chapter": "240", "is_lab": 0, "last_updated": "06/11/2020", "url": "/data/ncd?ncdid=4&ncdver=1"},
    {"document_id": 163, "document_display_id": "230.5", "title": "Gravlee Jet Washer", "chapter": "230", "is_lab": 0, "last_updated": "06/10/2020", "url": "/data/ncd?ncdid=163&ncdver=1"},
    {"document_id": 146, "document_display_id": "20.22", "title": "Ethylenediamine-Tetra-Acetic (EDTA) Chelation Therapy for Treatment of Atherosclerosis", "chapter": "20", "is_lab": 0, "last_updated": "06/10/2020", "url": "/data/ncd?ncdid=146&ncdver=1"},
    {"document_id": 237, "document_display_id": "50.2", "title": "Electronic Speech Aids", "chapter": "50", "is_lab": 0, "last_updated": "06/10/2020", "url": "/data/ncd?ncdid=237&ncdver=1"},
    {"document_id": 31, "document_display_id": "130.4", "title": "Electrical Aversion Therapy for Treatment of Alcoholism", "chapter": "130", "is_lab": 0, "last_updated": "06/10/2020", "url": "/data/ncd?ncdid=31&ncdver=1"},
    {"document_id": 206, "document_display_id": "280.11", "title": "Corset Used as Hernia Support", "chapter": "280", "is_lab": 0, "last_updated": "06/10/2020", "url": "/data/ncd?ncdid=206&ncdver=1"},
    {"document_id": 170, "document_display_id": "70.2", "title": "Consultation Services Rendered by a Podiatrist in a Skilled Nursing Facility", "chapter": "70", "is_lab": 0, "last_updated": "06/10/2020", "url": "/data/ncd?ncdid=170&ncdver=1"},
    {"document_id": 86, "document_display_id": "20.21", "title": "Chelation Therapy for Treatment of Atherosclerosis", "chapter": "20", "is_lab": 0, "last_updated": "06/10/2020", "url": "/data/ncd?ncdid=86&ncdver=1"},
    {"document_id": 48, "document_display_id": "20.1", "title": "Vertebral Artery Surgery", "chapter": "20", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=48&ncdver=1"},
    {"document_id": 202, "document_display_id": "230.2", "title": "Uroflowmetric Evaluations", "chapter": "230", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=202&ncdver=1"},
    {"document_id": 203, "document_display_id": "230.14", "title": "Ultrafiltration Monitor", "chapter": "230", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=203&ncdver=1"},
    {"document_id": 106, "document_display_id": "230.1", "title": "Treatment of Kidney Stones", "chapter": "230", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=106&ncdver=1"},
    {"document_id": 47, "document_display_id": "270.4", "title": "Treatment of Decubitus Ulcers", "chapter": "270", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=47&ncdver=1"},
    {"document_id": 258, "document_display_id": "30.9", "title": "Transillumination Light Scanning or Diaphanography", "chapter": "30", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=258&ncdver=1"},
    {"document_id": 143, "document_display_id": "160.20", "title": "Transfer Factor for Treatment of Multiple Sclerosis", "chapter": "160", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=143&ncdver=1"},
    {"document_id": 79, "document_display_id": "20.3", "title": "Thoracic Duct Drainage (TDD) in Renal Transplants", "chapter": "20", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=79&ncdver=1"},
    {"document_id": 164, "document_display_id": "220.11", "title": "Thermography", "chapter": "220", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=164&ncdver=1"},
    {"document_id": 7, "document_display_id": "30.2", "title": "Thermogenic Therapy", "chapter": "30", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=7&ncdver=1"},
    {"document_id": 216, "document_display_id": "160.5", "title": "Stereotaxic Depth Electrode Implantation", "chapter": "160", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=216&ncdver=1"},
    {"document_id": 147, "document_display_id": "110.6", "title": "Scalp Hypothermia During Chemotherapy to Prevent Hair Loss", "chapter": "110", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=147&ncdver=1"},
    {"document_id": 260, "document_display_id": "220.10", "title": "Portable Hand-Held X-Ray Instrument", "chapter": "220", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=260&ncdver=1"},
    {"document_id": 139, "document_display_id": "270.5", "title": "Porcine Skin and Gradient Pressure Dressings", "chapter": "270", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=139&ncdver=1"},
    {"document_id": 9, "document_display_id": "80.10", "title": "Phaco-Emulsification Procedure - Cataract Extraction", "chapter": "80", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=9&ncdver=1"},
    {"document_id": 71, "document_display_id": "260.2", "title": "Pediatric Liver Transplantation", "chapter": "260", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=71&ncdver=1"},
    {"document_id": 122, "document_display_id": "20.26", "title": "Partial Ventriculectomy", "chapter": "20", "is_lab": 0, "last_updated": "04/20/2020", "url": "/data/ncd?ncdid=122&ncdver=1"},
    {"document_id": 84, "document_display_id": "160.14", "title": "Invasive Intracranial Pressure Monitoring", "chapter": "160", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=84&ncdver=1"},
    {"document_id": 56, "document_display_id": "80.6", "title": "Intraocular Photography", "chapter": "80", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=56&ncdver=1"},
    {"document_id": 95, "document_display_id": "100.10", "title": "Injection Sclerotherapy for Esophageal Variceal Bleeding", "chapter": "100", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=95&ncdver=1"},
    {"document_id": 66, "document_display_id": "110.1", "title": "Hyperthermia for Treatment of Cancer", "chapter": "110", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=66&ncdver=1"},
    {"document_id": 144, "document_display_id": "110.5", "title": "Granulocyte Transfusions", "chapter": "110", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=144&ncdver=1"},
    {"document_id": 172, "document_display_id": "100.12", "title": "Gastrophotography", "chapter": "100", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=172&ncdver=1"},
    {"document_id": 76, "document_display_id": "150.8", "title": "Fluidized Therapy Dry Heat for Certain Musculoskeletal Disorders", "chapter": "150", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=76&ncdver=1"},
    {"document_id": 51, "document_display_id": "20.23", "title": "Fabric Wrapping of Abdominal Aneurysms", "chapter": "20", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=51&ncdver=1"},
    {"document_id": 200, "document_display_id": "160.10", "title": "Evoked Response Tests", "chapter": "160", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=200&ncdver=1"},
    {"document_id": 81, "document_display_id": "100.2", "title": "Endoscopy", "chapter": "100", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=81&ncdver=1"},
    {"document_id": 94, "document_display_id": "160.15", "title": "Electrotherapy for Treatment of Facial Nerve Paralysis (Bell's Palsy)", "chapter": "160", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=94&ncdver=1"},
    {"document_id": 234, "document_display_id": "230.15", "title": "Electrical Continence Aid", "chapter": "230", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=234&ncdver=1"},
    {"document_id": 262, "document_display_id": "20.24", "title": "Displacement Cardiography", "chapter": "20", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=262&ncdver=1"},
    {"document_id": 255, "document_display_id": "220.9", "title": "Digital Subtraction Angiography", "chapter": "220", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=255&ncdver=1"},
    {"document_id": 264, "document_display_id": "100.5", "title": "Diagnostic Breath Analyses", "chapter": "100", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=264&ncdver=1"},
    {"document_id": 261, "document_display_id": "80.9", "title": "Computer Enhanced Perimetry", "chapter": "80", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=261&ncdver=1"},
    {"document_id": 2, "document_display_id": "100.7", "title": "Colonic Irrigation", "chapter": "100", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=2&ncdver=1"},
    {"document_id": 92, "document_display_id": "40.3", "title": "Closed-Loop Blood Glucose Control Device (CBGCD)", "chapter": "40", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=92&ncdver=1"},
    {"document_id": 30, "document_display_id": "130.3", "title": "Chemical Aversion Therapy for Treatment of Alcoholism", "chapter": "130", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=30&ncdver=1"},
    {"document_id": 187, "document_display_id": "110.12", "title": "Challenge Ingestion Food Testing", "chapter": "110", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=187&ncdver=1"},
    {"document_id": 6, "document_display_id": "30.8", "title": "Cellular Therapy", "chapter": "30", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=6&ncdver=1"},
    {"document_id": 8, "document_display_id": "20.18", "title": "Carotid Body Resection/Carotid Body Denervation", "chapter": "20", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=8&ncdver=1"},
    {"document_id": 259, "document_display_id": "20.27", "title": "Cardiointegram (CIG) as an Alternative to Stress Test or Thallium Stress Test", "chapter": "20", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=259&ncdver=1"},
    {"document_id": 138, "document_display_id": "10.5", "title": "Autogenous Epidural Blood Graft", "chapter": "10", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=138&ncdver=1"},
    {"document_id": 155, "document_display_id": "110.9", "title": "Antigens Prepared for Sublingual Administration", "chapter": "110", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=155&ncdver=1"},
    {"document_id": 150, "document_display_id": "110.3", "title": "Anti-Inhibitor Coagulant Complex (AICC)", "chapter": "110", "is_lab": 0, "last_updated": "04/17/2020", "url": "/data/ncd?ncdid=150&ncdver=1"},
    {"document_id": 368, "document_display_id": "140.9", "title": "Gender Dysphoria and Gender Reassignment Surgery", "chapter": "140", "is_lab": 0, "last_updated": "10/25/2019", "url": "/data/ncd?ncdid=368&ncdver=1"},
    {"document_id": 265, "document_display_id": "190.9", "title": "Serologic Testing for Acquired Immunodeficiency Syndrome (AIDS)", "chapter": "190", "is_lab": 0, "last_updated": "03/09/2018", "url": "/data/ncd?ncdid=265&ncdver=1"},
    {"document_id": 3, "document_display_id": "150.1", "title": "Manipulation", "chapter": "150", "is_lab": 0, "last_updated": "03/08/2018", "url": "/data/ncd?ncdid=3&ncdver=1"},
    {"document_id": 21, "document_display_id": "30.6", "title": "Intravenous Histamine Therapy", "chapter": "30", "is_lab": 0, "last_updated": "01/24/2017", "url": "/data/ncd?ncdid=21&ncdver=1"},
    {"document_id": 99, "document_display_id": "20.11", "title": "Intraoperative Ventricular Mapping", "chapter": "20", "is_lab": 0, "last_updated": "01/24/2017", "url": "/data/ncd?ncdid=99&ncdver=1"},
    {"document_id": 77, "document_display_id": "160.8", "title": "Electroencephalographic Monitoring During Surgical Procedures Involving the Cerebral Vasculature", "chapter": "160", "is_lab": 0, "last_updated": "01/23/2017", "url": "/data/ncd?ncdid=77&ncdver=2"},
    {"document_id": 149, "document_display_id": "230.12", "title": "Dimethyl Sulfoxide (DMSO)", "chapter": "230", "is_lab": 0, "last_updated": "01/23/2017", "url": "/data/ncd?ncdid=149&ncdver=1"},
    {"document_id": 141, "document_display_id": "110.2", "title": "Certain Drugs Distributed by the National Cancer Institute", "chapter": "110", "is_lab": 0, "last_updated": "01/20/2017", "url": "/data/ncd?ncdid=141&ncdver=1"},
    {"document_id": 160, "document_display_id": "20.8.1", "title": "Cardiac Pacemaker Evaluation Services", "chapter": "20", "is_lab": 0, "last_updated": "01/20/2017", "url": "/data/ncd?ncdid=160&ncdver=1"},
    {"document_id": 137, "document_display_id": "30.7", "title": "Laetrile and Related Substances", "chapter": "30", "is_lab": 0, "last_updated": "08/16/2016", "url": "/data/ncd?ncdid=137&ncdver=1"},
    {"document_id": 247, "document_display_id": "50.4", "title": "Tracheostomy Speaking Valve", "chapter": "50", "is_lab": 0, "last_updated": "10/06/2015", "url": "/data/ncd?ncdid=247&ncdver=1"},
    {"document_id": 311, "document_display_id": "200.1", "title": "Nesiritide for Treatment of Heart Failure Patients", "chapter": "200", "is_lab": 0, "last_updated": "10/02/2015", "url": "/data/ncd?ncdid=311&ncdver=1"},
    {"document_id": 321, "document_display_id": "200.2", "title": "Nebulized Beta Adrenergic Agonist Therapy for Lung Diseases", "chapter": "200", "is_lab": 0, "last_updated": "10/02/2015", "url": "/data/ncd?ncdid=321&ncdver=1"},
    {"document_id": 278, "document_display_id": "160.25", "title": "Multiple Electroconvulsive Therapy (MECT)", "chapter": "160", "is_lab": 0, "last_updated": "10/01/2015", "url": "/data/ncd?ncdid=278&ncdver=1"},
    {"document_id": 325, "document_display_id": "260.10", "title": "Heartsbreath Test for Heart Transplant Rejection", "chapter": "260", "is_lab": 0, "last_updated": "09/30/2015", "url": "/data/ncd?ncdid=325&ncdver=1"},
    {"document_id": 346, "document_display_id": "210.9", "title": "Screening for Depression in Adults", "chapter": "210", "is_lab": 0, "last_updated": "09/25/2015", "url": "/data/ncd?ncdid=346&ncdver=1"},
    {"document_id": 42, "document_display_id": "30.1.1", "title": "Biofeedback Therapy for the Treatment of Urinary Incontinence", "chapter": "30", "is_lab": 0, "last_updated": "09/24/2015", "url": "/data/ncd?ncdid=42&ncdver=1"},
    {"document_id": 88, "document_display_id": "250.1", "title": "Treatment of Psoriasis", "chapter": "250", "is_lab": 0, "last_updated": "02/24/2015", "url": "/data/ncd?ncdid=88&ncdver=1"},
    {"document_id": 19, "document_display_id": "160.1", "title": "Induced Lesions of Nerve Tracts", "chapter": "160", "is_lab": 0, "last_updated": "02/24/2015", "url": "/data/ncd?ncdid=19&ncdver=1"},
    {"document_id": 196, "document_display_id": "70.5", "title": "Hospital and Skilled Nursing Facility Admission Diagnostic Procedures", "chapter": "70", "is_lab": 0, "last_updated": "02/24/2015", "url": "/data/ncd?ncdid=196&ncdver=1"},
    {"document_id": 250, "document_display_id": "170.1", "title": "Institutional and Home Care Patient Education Programs", "chapter": "170", "is_lab": 0, "last_updated": "12/13/2002", "url": "/data/ncd?ncdid=250&ncdver=1"},
    {"document_id": 180, "document_display_id": "250.2", "title": "Hemorheograph", "chapter": "250", "is_lab": 0, "last_updated": "12/13/2002", "url": "/data/ncd?ncdid=180&ncdver=1"},
    {"document_id": 43, "document_display_id": "50.5", "title": "Oxygen Treatment of Inner Ear/Carbon Therapy", "chapter": "50", "is_lab": 0, "last_updated": "12/12/2002", "url": "/data/ncd?ncdid=43&ncdver=1"},
    {"document_id": 168, "document_display_id": "280.2", "title": "White Cane for Use by a Blind Person", "chapter": "280", "is_lab": 0, "last_updated": "12/11/2002", "url": "/data/ncd?ncdid=168&ncdver=1"},
    {"document_id": 266, "document_display_id": "110.11", "title": "Food Allergy Testing and Treatment", "chapter": "110", "is_lab": 0, "last_updated": "12/09/2002", "url": "/data/ncd?ncdid=266&ncdver=1"},
    {"document_id": 191, "document_display_id": "100.4", "title": "Esophageal Manometry", "chapter": "100", "is_lab": 0, "last_updated": "12/06/2002", "url": "/data/ncd?ncdid=191&ncdver=1"},
    {"document_id": 189, "document_display_id": "190.6", "title": "Hair Analysis", "chapter": "190", "is_lab": 0, "last_updated": "12/06/2002", "url": "/data/ncd?ncdid=189&ncdver=1"},
    {"document_id": 183, "document_display_id": "70.4", "title": "Pronouncement of Death", "chapter": "70", "is_lab": 0, "last_updated": "12/06/2002", "url": "/data/ncd?ncdid=183&ncdver=1"},
    {"document_id": 87, "document_display_id": "100.6", "title": "Gastric Freezing", "chapter": "100", "is_lab": 0, "last_updated": "12/03/2002", "url": "/data/ncd?ncdid=87&ncdver=1"},
    {"document_id": 68, "document_display_id": "130.8", "title": "Hemodialysis for Treatment of Schizophrenia", "chapter": "130", "is_lab": 0, "last_updated": "12/02/2002", "url": "/data/ncd?ncdid=68&ncdver=1"},
    {"document_id": 67, "document_display_id": "50.7", "title": "Cochleostomy with Neurovascular Transplant for Meniere's Disease", "chapter": "50", "is_lab": 0, "last_updated": "12/02/2002", "url": "/data/ncd?ncdid=67&ncdver=1"},
    {"document_id": 5, "document_display_id": "50.8", "title": "Ultrasonic Surgery", "chapter": "50", "is_lab": 0, "last_updated": "12/02/2002", "url": "/data/ncd?ncdid=5&ncdver=1"},
]

if __name__ == "__main__":
    import json

    # Load batch 2 from saved file
    with open("data/cms_batch2.json", "r") as f:
        batch2 = json.load(f)

    print(f"Seeding batch 2: {len(batch2)} NCDs...")
    seed_from_preloaded(batch2)

    print(f"Seeding batch 3: {len(BATCH3)} NCDs...")
    seed_from_preloaded(BATCH3)

    print("Done! All CMS NCDs seeded.")
