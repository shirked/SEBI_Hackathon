import io
from datetime import datetime
from typing import Tuple, List

import pandas as pd
import streamlit as st
import plotly.express as px
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


# ---------------------------
# App Config and Styling
# ---------------------------
st.set_page_config(
	page_title="CompliScore – Compliance Health Dashboard",
	layout="wide",
	initial_sidebar_state="expanded",
)

PRIMARY_TITLE = "CompliScore – Compliance Health Dashboard"
SUBTITLE = "Low‑cost compliance monitoring for small and mid‑sized brokers"


def get_demo_dataset(n: int = 30) -> pd.DataFrame:
	"""Generate a realistic demo dataset with n broker entries."""
	broker_prefixes = [
		"Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Theta", "Lambda",
		"Orion", "Nova", "Apex", "Summit", "Pioneer", "Vertex", "Atlas", "Crown",
		"Harbor", "Cobalt", "Sterling", "Quantum", "Falcon", "Aurora", "Nimbus",
		"Horizon", "Frontier", "Regal", "Everest", "Beacon", "Crescent", "Keystone",
	]
	broker_suffixes = [
		"Securities", "Capital", "Investments", "Wealth", "Brokerage", "Advisors",
		"Markets", "Partners", "Financial", "Holdings",
	]

	def name(i: int) -> str:
		p = broker_prefixes[i % len(broker_prefixes)]
		s = broker_suffixes[(i * 3) % len(broker_suffixes)]
		return f"{p} {s}"

	# Construct varied values with some intentional spread
	data = []
	for i in range(n):
		broker_name = name(i)
		kyc_completed = "Y" if (i % 3 != 0) else "N"
		capital_adequacy = 90 + ((i * 11) % 40)  # 90% to 129%
		client_complaints = (i * 2) % 7  # 0..6
		reporting_delay = (i % 4)  # 0..3 days
		data.append(
			{
				"Broker Name": broker_name,
				"KYC Completed (Y/N)": kyc_completed,
				"Capital Adequacy %": capital_adequacy,
				"Client Complaints": client_complaints,
				"Reporting Delay (days)": reporting_delay,
			}
		)
	return pd.DataFrame(data)


def compute_score_and_flags(row: pd.Series) -> Tuple[int, List[str]]:
	"""Compute compliance score (0..100) and failed checks list for a broker."""
	score = 0
	failed: List[str] = []

	# KYC Completed
	if str(row.get("KYC Completed (Y/N)", "")).strip().upper() == "Y":
		score += 20
	else:
		failed.append("KYC not completed")

	# Capital Adequacy
	try:
		cap = float(row.get("Capital Adequacy %", 0))
	except Exception:
		cap = 0.0
	if cap >= 100:
		score += 20
	else:
		failed.append("Capital adequacy < 100%")

	# Client Complaints
	try:
		complaints = int(row.get("Client Complaints", 0))
	except Exception:
		complaints = 0
	if complaints <= 2:
		score += 20
	else:
		failed.append("Complaints > 2")

	# Reporting Delay
	try:
		delay = float(row.get("Reporting Delay (days)", 0))
	except Exception:
		delay = 0.0
	if delay <= 1:
		score += 20
	else:
		failed.append("Reporting delay > 1 day")

	# No major breaches condition
	if complaints <= 2 and delay <= 1:
		score += 20
	else:
		failed.append("Major breaches present")

	return score, failed


def status_from_score(score: int) -> str:
	# Relatable terms instead of color names
	if score >= 80:
		return "Compliant"
	elif score >= 50:
		return "Needs Attention"
	return "Non-Compliant"


def color_for_status(status: str) -> str:
	return {
		"Compliant": "#2e7d32",
		"Needs Attention": "#f9a825",
		"Non-Compliant": "#c62828",
	}.get(status, "#424242")


def load_input_dataframe(uploaded_file) -> pd.DataFrame:
	if uploaded_file is None:
		return get_demo_dataset(30)

	name = uploaded_file.name.lower()
	if name.endswith(".csv"):
		return pd.read_csv(uploaded_file)
	elif name.endswith(".xls") or name.endswith(".xlsx"):
		return pd.read_excel(uploaded_file)
	else:
		raise ValueError("Unsupported file format. Please upload CSV or Excel.")


def prepare_scored_dataframe(df: pd.DataFrame) -> pd.DataFrame:
	required_cols = [
		"Broker Name",
		"KYC Completed (Y/N)",
		"Capital Adequacy %",
		"Client Complaints",
		"Reporting Delay (days)",
	]
	missing = [c for c in required_cols if c not in df.columns]
	if missing:
		raise ValueError(f"Missing required columns: {', '.join(missing)}")

	# Compute score and flags
	scores, flags = [], []
	for _, row in df.iterrows():
		s, f = compute_score_and_flags(row)
		scores.append(s)
		flags.append(", ".join(f) if f else "")

	result = df.copy()
	result["Compliance Score"] = scores
	result["Status"] = result["Compliance Score"].apply(status_from_score)
	result["Failed Checks"] = flags
	return result


def build_pdf_report(scored_df: pd.DataFrame, avg: float, hi: int, lo: int) -> bytes:
	buffer = io.BytesIO()
	# Landscape for wider tables
	doc = SimpleDocTemplate(
		buffer,
		pagesize=landscape(A4),
		leftMargin=2*cm,
		rightMargin=2*cm,
		topMargin=1.5*cm,
		bottomMargin=1.5*cm,
	)
	styles = getSampleStyleSheet()
	cell_style = ParagraphStyle(
		name="Cell",
		parent=styles['Normal'],
		fontSize=9,
		leading=11,
	)
	story = []

	# Normalize helper to avoid missing glyphs (e.g., en dash, non‑breaking hyphen)
	def _normalize(text: str) -> str:
		if text is None:
			return ""
		s = str(text)
		replacements = {
			"–": "-",  # en dash
			"—": "-",  # em dash
			"‑": "-",  # non-breaking hyphen
			"−": "-",  # minus sign
			"“": '"',
			"”": '"',
			"‘": "'",
			"’": "'",
		}
		for k, v in replacements.items():
			s = s.replace(k, v)
		return s

	# Title
	story.append(Paragraph(_normalize("CompliScore – Compliance Health Dashboard"), styles['Title']))
	story.append(Paragraph(_normalize("Low‑cost compliance monitoring for small and mid‑sized brokers"), styles['Normal']))
	story.append(Spacer(1, 0.4 * cm))

	# Summary
	story.append(Paragraph(_normalize(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), styles['Normal']))
	story.append(Paragraph(_normalize(f"Average Score: <b>{avg:.1f}</b>"), styles['Normal']))
	story.append(Paragraph(_normalize(f"Highest Score: <b>{hi}</b>"), styles['Normal']))
	story.append(Paragraph(_normalize(f"Lowest Score: <b>{lo}</b>"), styles['Normal']))
	story.append(Spacer(1, 0.5 * cm))

	# Table with wrapped cells and fixed column widths
	columns = ["Broker Name", "Compliance Score", "Status", "Failed Checks"]
	# Header row as Paragraphs to ensure consistent sizing
	header_row = [Paragraph(_normalize(col), ParagraphStyle(name="Header", parent=styles['BodyText'], fontSize=9)) for col in columns]
	data_rows = []
	for _, r in scored_df[columns].iterrows():
		broker = Paragraph(_normalize(str(r["Broker Name"])), cell_style)
		score = Paragraph(_normalize(str(r["Compliance Score"])), cell_style)
		status = Paragraph(_normalize(str(r["Status"])), cell_style)
		failed_text = str(r["Failed Checks"]) if str(r["Failed Checks"]) else "-"
		failed = Paragraph(_normalize(failed_text), cell_style)
		data_rows.append([broker, score, status, failed])

	# Column widths tuned for A4 landscape content width (~25.7 cm)
	col_widths = [7*cm, 3*cm, 3.5*cm, 12*cm]
	t = Table([header_row] + data_rows, colWidths=col_widths, repeatRows=1)
	t.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('ALIGN', (1, 1), (2, -1), 'CENTER'),  # score & status centered
		('VALIGN', (0, 0), (-1, -1), 'TOP'),
		('BOTTOMPADDING', (0, 0), (-1, 0), 6),
		('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
	]))
	story.append(t)

	doc.build(story)
	buffer.seek(0)
	return buffer.read()


def main() -> None:
	# Header
	st.markdown(f"## {PRIMARY_TITLE}")
	st.markdown(f"{SUBTITLE}")
	st.markdown("---")

	with st.sidebar:
		st.markdown("**Data Input**")
		uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xls", "xlsx"]) 
		st.caption("If no file is uploaded, demo data will be used.")

	try:
		input_df = load_input_dataframe(uploaded)
		if uploaded is None:
			st.info("Demo mode: Using built‑in sample dataset.")
	except Exception as e:
		st.error(str(e))
		return

	# Normalize column names (strip spaces and standard exact headers)
	input_df.columns = [str(c).strip() for c in input_df.columns]

	# Score
	try:
		scored_df = prepare_scored_dataframe(input_df)
	except Exception as e:
		st.error(str(e))
		return

	# Summary metrics
	avg_score = float(scored_df["Compliance Score"].mean())
	highest = int(scored_df["Compliance Score"].max())
	lowest = int(scored_df["Compliance Score"].min())

	# KPI Cards
	col1, col2, col3 = st.columns(3)
	col1.metric("Average Score", f"{avg_score:.1f}")
	col2.metric("Highest Score", f"{highest}")
	col3.metric("Lowest Score", f"{lowest}")

	# Table with colored status
	styled = scored_df.copy()
	def color_status(val: str) -> str:
		return f"color: white; background-color: {color_for_status(val)}" if val in ["Green", "Yellow", "Red"] else ""
	st.markdown("### Broker Compliance Table")
	st.dataframe(
		styled[[
			"Broker Name",
			"KYC Completed (Y/N)",
			"Capital Adequacy %",
			"Client Complaints",
			"Reporting Delay (days)",
			"Compliance Score",
			"Status",
			"Failed Checks",
		]].style.applymap(color_status, subset=["Status"]),
		width='stretch',
		hide_index=True,
	)

	# Bar chart
	st.markdown("### Compliance Scores Distribution")
	fig = px.bar(
		scored_df.sort_values("Compliance Score", ascending=False),
		x="Broker Name",
		y="Compliance Score",
		color="Status",
		color_discrete_map={
			"Compliant": "#2e7d32",
			"Needs Attention": "#f9a825",
			"Non-Compliant": "#c62828",
		},
		height=500,
	)
	fig.update_layout(xaxis_tickangle=-30, template="plotly_white")
	st.plotly_chart(fig, width='stretch')

	# Export PDF
	st.markdown("### Export Report")
	pdf_bytes = build_pdf_report(scored_df, avg_score, highest, lowest)
	st.download_button(
		label="Download PDF Report",
		data=pdf_bytes,
		file_name=f"CompliScore_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
		mime="application/pdf",
	)


if __name__ == "__main__":
	main()


