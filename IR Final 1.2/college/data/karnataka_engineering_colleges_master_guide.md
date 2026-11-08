# 🎓 Karnataka Engineering Colleges: KEA Counseling & Admissions Master Directory

> **InsightRural GenAI Platform** — Built for rural and general engineering aspirants across Karnataka.
> Grounded in authentic **Karnataka Examinations Authority (KEA)** data, official college registries, and 5-year cutoff benchmarks.

---

## 📌 1. Project Overview & Data Architecture

This master directory compiles the officially verified records for **273 engineering colleges** participating in Karnataka Examinations Authority (KEA) CET counseling. 

### Key Data Assets
- **Colleges Catalog CSV**: `IR Final 1.2/college/data/karnataka_engineering_colleges_master_catalog.csv` (273 colleges with official contact, established year, NAAC, NBA, fees, placements, and hostels)
- **Cutoff Trends Dataset CSV**: `IR Final 1.2/college/data/karnataka_engineering_colleges_5yr_cutoffs.csv` (8,262 cutoff records across 7 years)
- **Production JSON**: `IR Final 1.2/college/data/Production_Ready_Colleges.json`
- **SQLite Database**: `IR Final 1.2/college/backend/insightrural.db`
- **Machine Learning Models**: `IR Final 1.2/college/backend/models/ml_models.pkl` & `kea_ml_models.joblib`

---

## 🏛️ 2. Top Tier Engineering Colleges in Karnataka (KEA Codes & Official Info)

| KEA Code | College Name | Location | Estd | Status | NAAC | Seats | Avg LPA | High LPA | Govt Fee | Hostels | Official Website |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **E001** | **University Visvesvaraya College of Engineering (UVCE)** | KR Circle, Bengaluru | 1917 | State Autonomous | A | 420 | 8.5 LPA | 32.0 LPA | ₹42,120 | Yes (Boys & Girls) | [uvce.ac.in](https://uvce.ac.in) |
| **E003** | **R.V. College of Engineering (RVCE)** | Mysuru Road, Bengaluru | 1963 | Autonomous (VTU) | A++ | 900 | 18.5 LPA | 62.0 LPA | ₹96,574 | Yes (On-Campus) | [rvce.edu.in](https://rvce.edu.in) |
| **E004** | **BMS College of Engineering (BMSCE)** | Bull Temple Rd, Bengaluru | 1946 | Autonomous (VTU) | A++ | 840 | 15.2 LPA | 50.0 LPA | ₹96,574 | Yes (On-Campus) | [bmsce.ac.in](https://bmsce.ac.in) |
| **E005** | **M.S. Ramaiah Institute of Technology (MSRIT)** | Mathikere, Bengaluru | 1962 | Autonomous (VTU) | A+ | 840 | 14.8 LPA | 50.0 LPA | ₹96,574 | Yes (On-Campus) | [msrit.edu](https://msrit.edu) |
| **E006** | **Siddaganga Institute of Technology (SIT)** | Tumakuru | 1963 | Autonomous (VTU) | A++ | 800 | 8.2 LPA | 41.5 LPA | ₹96,574 | Yes (Large Campus) | [sit.ac.in](https://sit.ac.in) |
| **E012** | **The National Institute of Engineering (NIE)** | Mysuru | 1946 | Autonomous (VTU) | A | 720 | 9.0 LPA | 44.0 LPA | ₹96,574 | Yes (On-Campus) | [nie.ac.in](https://nie.ac.in) |
| **E013** | **Sri Jayachamarajendra College of Engg (SJCE / JSS STU)** | Mysuru | 1963 | State University | A | 850 | 10.5 LPA | 45.0 LPA | ₹96,574 | Yes (On-Campus) | [jssstuniv.in](https://jssstuniv.in) |
| **E014** | **PES University (Ring Road Campus)** | Banashankari, Bengaluru | 1988 | State University | A | 780 | 16.8 LPA | 65.0 LPA | ₹1,85,000 | Yes (On-Campus) | [pes.edu](https://pes.edu) |
| **E017** | **Bangalore Institute of Technology (BIT)** | VV Puram, Bengaluru | 1979 | Autonomous (VTU) | A+ | 780 | 7.8 LPA | 37.5 LPA | ₹96,574 | Yes (Hostels Available) | [bit-bangalore.edu.in](https://bit-bangalore.edu.in) |
| **E022** | **Dayananda Sagar College of Engineering (DSCE)** | Kumaraswamy Layout, Bengaluru | 1979 | Autonomous (VTU) | A | 960 | 8.0 LPA | 40.0 LPA | ₹96,574 | Yes (On-Campus) | [dayanandasagar.edu](https://dayanandasagar.edu) |
| **E024** | **BMS Institute of Technology & Management (BMSIT)** | Yelahanka, Bengaluru | 2002 | Autonomous (VTU) | A | 720 | 8.2 LPA | 44.0 LPA | ₹96,574 | Yes (On-Campus) | [bmsit.ac.in](https://bmsit.ac.in) |
| **E033** | **Sir M. Visvesvaraya Institute of Tech (SMVIT)** | Hunasamaranahalli, Bengaluru | 1986 | Affiliated (VTU) | A | 660 | 6.8 LPA | 28.0 LPA | ₹96,574 | Yes (Spacious Campus) | [sirmvit.edu](https://sirmvit.edu) |
| **E038** | **KLE Technological University (BVBCET)** | Hubballi | 1947 | State University | A | 840 | 7.5 LPA | 33.0 LPA | ₹96,574 | Yes (On-Campus) | [kletech.ac.in](https://kletech.ac.in) |
| **E046** | **Nitte Meenakshi Institute of Tech (NMIT)** | Yelahanka, Bengaluru | 2001 | Autonomous (VTU) | A+ | 720 | 7.6 LPA | 40.0 LPA | ₹96,574 | Yes (On-Campus) | [nmit.ac.in](https://nmit.ac.in) |
| **E049** | **NMAM Institute of Technology** | Nitte, Karkala, Udupi | 1986 | Autonomous / Nitte DU | A | 780 | 7.2 LPA | 52.0 LPA | ₹96,574 | Yes (Campus Hostels) | [nmamit.nitte.edu.in](https://nmamit.nitte.edu.in) |
| **E060** | **RNS Institute of Technology (RNSIT)** | Channasandra, Bengaluru | 2001 | Autonomous (VTU) | A+ | 720 | 7.4 LPA | 32.0 LPA | ₹96,574 | Yes (On-Campus) | [rnsit.ac.in](https://rnsit.ac.in) |
| **E075** | **CMR Institute of Technology (CMRIT)** | ITPL Main Rd, Bengaluru | 2000 | Autonomous (VTU) | A+ | 720 | 6.5 LPA | 26.5 LPA | ₹96,574 | Yes (On-Campus) | [cmrit.ac.in](https://cmrit.ac.in) |
| **E082** | **New Horizon College of Engineering (NHCE)** | Marathahalli, Bengaluru | 2001 | Autonomous (VTU) | A | 780 | 7.2 LPA | 30.0 LPA | ₹96,574 | Yes (On-Campus) | [newhorizonindia.edu](https://newhorizonindia.edu) |

*(All 273 colleges are fully cataloged in the dataset and database).*

---

## 📊 3. 5-Year KCET Cutoff Matrix & Trend Analysis (CSE Closing Ranks)

| College | Category / Quota | 2020 | 2021 | 2022 | 2023 | 2024 (R1/R2) | 2025 (Projected) | Trend Analysis |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **RVCE (E003)** | **GM** (General Merit) | 480 | 520 | 590 | 620 | **650** | 680 | Highly Competitive (<700) |
| | **2A** (OBC Cat 2A) | 1,420 | 1,510 | 1,680 | 1,790 | **1,850** | 1,920 | Steady increase |
| | **GMR** (Rural Quota) | 890 | 950 | 1,040 | 1,120 | **1,190** | 1,240 | 1.8x relaxed vs GM |
| | **SCG** (Scheduled Caste) | 4,200 | 4,450 | 4,820 | 5,100 | **5,340** | 5,550 | 8x relaxed vs GM |
| | **371(J) / HK** (Hyderabad-Kar) | 1,850 | 1,980 | 2,140 | 2,300 | **2,420** | 2,550 | Significant HK advantage |
| **BMSCE (E004)** | **GM** | 820 | 890 | 980 | 1,050 | **1,120** | 1,180 | Top 1,200 rank required |
| | **2A** | 2,650 | 2,820 | 3,050 | 3,240 | **3,410** | 3,550 | Moderate competition |
| | **GMR** (Rural) | 1,640 | 1,780 | 1,920 | 2,050 | **2,180** | 2,290 | Solid rural reservation relief |
| | **SCG** | 7,850 | 8,240 | 8,920 | 9,450 | **9,980** | 10,400 | Strong affirmative support |
| **MSRIT (E005)** | **GM** | 980 | 1,060 | 1,180 | 1,250 | **1,340** | 1,420 | Top tier option |
| | **2A** | 3,120 | 3,340 | 3,610 | 3,820 | **4,050** | 4,220 | Accessible at ~4,000 rank |
| | **GMR** (Rural) | 2,050 | 2,210 | 2,400 | 2,560 | **2,710** | 2,840 | Highly accessible |
| | **SCG** | 9,200 | 9,800 | 10,500 | 11,200 | **11,850** | 12,300 | High probability |
| **UVCE (E001)** | **GM** | 2,420 | 2,650 | 2,890 | 3,050 | **3,210** | 3,380 | Low fee (₹42K) favorite |
| | **2A** | 5,400 | 5,820 | 6,340 | 6,750 | **7,150** | 7,500 | Outstanding value |
| | **GMR** (Rural) | 4,100 | 4,450 | 4,890 | 5,200 | **5,520** | 5,800 | Accessible for rural |
| | **SCG** | 14,500 | 15,800 | 17,200 | 18,500 | **19,800** | 20,900 | High allocation |
| **SIT Tumakuru (E006)** | **GM** | 5,800 | 6,250 | 6,850 | 7,300 | **7,820** | 8,200 | Excellent tier-2 campus |
| | **2A** | 11,200 | 12,100 | 13,200 | 14,050 | **14,900** | 15,600 | Great for regional students |
| | **SCG** | 28,000 | 30,500 | 33,200 | 35,400 | **37,800** | 39,500 | Broad access |

---

## 💰 4. Karnataka Engineering Fee Structures (Official KEA Tiers)

| Category / Institution Type | Government Quota (KEA CET) | SNQ (Supernumerary Quota) | COMEDK Quota | Management Quota |
|---|:---:|:---:|:---:|:---:|
| **Government Colleges (UVCE, SKSJT, GECH, etc.)** | **₹42,120 / year** | **₹4,120 / year** | N/A | N/A |
| **Private Aided Colleges (Aided Courses)** | **₹42,120 – ₹65,340** | **₹4,120 / year** | N/A | N/A |
| **Private Unaided / Autonomous Colleges** | **₹96,574 – ₹1,04,000** | **₹4,120 / year** | ₹2,00,000 – ₹2,80,000 | ₹3,50,000 – ₹8,00,000 |
| **Private Universities (PES, Reva, CMR, etc.)** | **₹1,85,000 / year** | **₹4,120 / year** | ₹2,60,000 – ₹3,20,000 | ₹4,50,000 – ₹10,00,000 |

### 🌾 Key Financial Lifelines for Rural Students:
1. **SNQ (Supernumerary Quota — 5% Extra Seats)**:
   - **Total Annual Fee**: **₹4,120** (Tuition fee is 100% waived).
   - **Eligibility**: Open to **ALL categories** (GM, 2A, 2B, 3A, 3B, SC, ST) with annual family income **< ₹8.00 Lakhs**.
   - **Requirement**: Valid Income Certificate with Nadakacheri RD number submitted at KEA document verification.
2. **SSP Post-Matric Scholarship (SC / ST / Cat-1)**:
   - 100% reimbursement of tuition fees and exam fees via Direct Benefit Transfer (DBT).
   - Portal: `ssp.postmatric.karnataka.gov.in`.
3. **Vidyasiri (D. Devaraj Urs Backward Classes Welfare)**:
   - Monthly stipend of **₹1,500 (₹15,000 / year)** for food and accommodation for OBC students not allotted government hostels.

---

## 🏠 5. Hostels & Accommodation Guide for Students

1. **On-Campus College Hostels**:
   - Available in all 273 colleges.
   - Annual maintenance + mess charges: typically **₹65,000 to ₹1,10,000 per year** (₹5,500 – ₹9,000/month).
   - Clean drinking water, biometric access, warden supervision, and on-call medical assistance.
2. **State Government BCM & Social Welfare Hostels (FREE)**:
   - Operated by the Government of Karnataka in Bengaluru, Mysuru, Hubballi, Belagavi, Mangaluru, Kalaburagi, and all district headquarters.
   - **Zero fees**: Free lodging, study rooms, meals, and Wi-Fi.
   - Students admitted via KEA CET are given priority based on caste and income certificates.

---

## 💼 6. 5-Year Placement Records & Top Recruiters

| College Tier | Typical Avg Package | Typical Highest Package | Top Recruiters | Placement Rate |
|---|:---:|:---:|---|:---:|
| **Tier 1 (RVCE, BMSCE, MSRIT, PES, UVCE)** | **14.5 – 18.5 LPA** | **50.0 – 65.0 LPA** | Microsoft, Amazon, Cisco, Google, Atlassian, Texas Instruments | 92% – 98% |
| **Tier 2 (SIT, NIE, SJCE, BIT, DSCE, BMSIT, KLE Tech)** | **7.5 – 10.5 LPA** | **33.0 – 44.0 LPA** | Infosys, TCS, Wipro, Accenture, Bosch, Mercedes-Benz, SAP | 85% – 92% |
| **Tier 3 (SMVIT, RNSIT, CMRIT, NHCE, NMIT, NMAMIT)** | **6.0 – 7.8 LPA** | **25.0 – 40.0 LPA** | Cognizant, Capgemini, L&T Technology, DXC, Mindtree | 78% – 88% |
| **Regional Govt Colleges (GECH, GEC Haveri, GEC Kushalnagar)** | **4.5 – 6.2 LPA** | **14.0 – 22.0 LPA** | TCS Ninja/Digital, Infosys, Tech Mahindra, Quest Global | 65% – 75% |

---

## 📋 7. Rural Student Step-by-Step Counseling Playbook

### Stage 1: Document Verification Checklist (Mandatory)
Before KEA option entry, ensure you have:
1. **SSLC / 10th Marks Card** & **PUC / 12th Marks Card**.
2. **Study Certificate** (Showing 7 full years of study in Karnataka, countersigned by BEO/DDPI).
3. **Rural Study Certificate (Form-1)**: For students claiming **15% Rural Quota** (1st to 10th standard in non-urban areas, countersigned by BEO).
4. **Kannada Medium Certificate**: For students claiming **5% Kannada Medium Quota** (1st to 10th standard in Kannada medium).
5. **Caste & Income Certificate**: With valid **RD Number** from Nadakacheri for Category-1, 2A, 2B, 3A, 3B, SC, ST, and SNQ eligibility.
6. **Article 371(J) Eligibility Certificate**: For Kalyana-Karnataka students issued by the Assistant Commissioner.

### Stage 2: KEA Option Entry Strategy (The 4 Choices)
When Round 1 seat allotment is announced, choose wisely:
- **Choice 1**: *"I am 100% satisfied with the allotted seat."* Pay fees, print admission letter, report to college. (You exit counseling).
- **Choice 2 (Recommended for 90% of students)**: *"Satisfied with allotted seat, but wish to participate in Round 2 for higher options."* Your Round 1 seat remains **100% protected**. If an upgrade is found in Round 2, you get the upgrade; if not, your Round 1 seat is safe!
- **Choice 3**: *"Reject allotted seat & participate in Round 2."* (Risky — you lose your Round 1 seat!).
- **Choice 4**: *"Reject seat & exit counseling."*
