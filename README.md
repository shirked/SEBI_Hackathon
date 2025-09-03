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

