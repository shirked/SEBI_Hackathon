CompliScore – Compliance Health Dashboard
========================================

A Streamlit app for quick compliance health scoring of brokers. Upload a CSV/Excel file or use the built-in demo data.

Features
--------
- File upload (CSV/XLS/XLSX) or automatic demo dataset (30 brokers)
- Scoring (max 100): KYC, capital adequacy, complaints, reporting delay, and major breaches
- Status with relatable terms: Compliant, Needs Attention, Non-Compliant
- Table with failed checks, KPI summary, Plotly bar chart
- PDF export (A4 landscape, wrapped cells, fixed widths)

Input format
------------
Required columns:
- Broker Name
- KYC Completed (Y/N)
- Capital Adequacy %
- Client Complaints
- Reporting Delay (days)

## 🧮 Rule-based Evaluation Across 5 Dimensions

Each broker is evaluated across five compliance checks.  
Each check contributes **20 points**, for a total score of **100**.  
Failed checks are flagged and listed in the report.

---

### ✅ Scoring Breakdown

- **KYC Completed?**
  - ✔️ Yes → +20 Points  
  - ❌ No → Flag: KYC not completed

- **Capital Adequacy ≥ 100%?**
  - ✔️ Yes → +20 Points  
  - ❌ No → Flag: Capital adequacy < 100%

- **Client Complaints ≤ 2?**
  - ✔️ Yes → +20 Points  
  - ❌ No → Flag: Complaints > 2

- **Reporting Delay ≤ 1 day?**
  - ✔️ Yes → +20 Points  
  - ❌ No → Flag: Reporting delay > 1 day

- **Major Breaches Present?** *(i.e., complaints > 2 or delay > 1)*
  - ❌ Yes → Flag: Major breaches present  
  - ✔️ No → +20 Points

---

### 🧠 Final Score Classification

| **Score Range** | **Status**         |
|-----------------|--------------------|
| 80–100          | ✅ Compliant        |
| 50–79           | ⚠️ Needs Attention |
| 0–49            | ❌ Non-Compliant    |

Run locally
-----------
```bash
pip install -r requirements.txt
streamlit run app.py
```

Notes
-----
- If no file is uploaded, demo mode loads automatically.
- PDF text normalization avoids missing glyphs for dashes/quotes.

License
-------
MIT

