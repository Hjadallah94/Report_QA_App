import io
import os
import time
from typing import List, Dict

import streamlit as st
import pandas as pd

from rules_engine.rules_loader import load_rules
from rules_engine.engine import evaluate
# Optional checks (removed from pipeline): availability helpers removed
from parsers.docx_parser import parse_docx
from parsers.pdf_parser import parse_pdf

st.set_page_config(page_title="Report QA", layout="wide")

st.title("Report QA")
st.caption("Upload a report (DOCX or digitally-born PDF), run checks, and export issues to CSV.")

# --- Sidebar controls ---
lang = st.sidebar.selectbox("Language", ["English", "Arabic"])
severity_filter = st.sidebar.multiselect("Filter by severity", ["Critical", "Major", "Minor"], default=["Critical","Major","Minor"])
st.sidebar.markdown("---")
st.sidebar.write("**Usage**")
st.sidebar.write("- File types: .docx / .pdf")
st.sidebar.write("- Max size: 20 MB (≈ 40 pages)")

# Load rules YAML
RULES_PATH = "config/rules_en.yml" if lang == "English" else "config/rules_ar.yml"
rules_cfg = load_rules(RULES_PATH)

# Note: spaCy and ML subjectivity checks were removed from the runtime pipeline.
# --- Per-check toggles and verbosity ---
st.sidebar.markdown("---")
st.sidebar.write("**Checks (enable/disable)**")
# List of checks (key, label) shown in the sidebar
AVAILABLE_CHECKS = [
    ("required_sections", "Required sections"),
    ("first_person", "First-person pronouns"),
    ("forbidden_phrases", "Forbidden phrases"),
    ("subjective_language", "Subjective language"),
    ("bias_language", "Bias phrases"),
    ("vagueness", "Placeholders & vague phrases"),
    ("repetition", "Repetition"),
    ("passive_voice_ratio", "Passive-voice ratio"),
    ("missing_image_caption", "Missing image captions"),
]

enabled_checks = []
for key, label in AVAILABLE_CHECKS:
    if st.sidebar.checkbox(label, value=True, key=f"chk_{key}"):
        enabled_checks.append(key)

# Show a compact summary of enabled checks
st.sidebar.markdown("---")
st.sidebar.write(f"**Enabled checks:** {len(enabled_checks)}")

# Verbosity / confidence threshold (0-100). Higher = fewer suggestions.
verbosity = st.sidebar.slider("Verbosity (higher = fewer suggestions)", 0, 100, 30)
rules_cfg["_enabled_checks"] = enabled_checks
rules_cfg["_verbosity"] = verbosity

uploaded = st.file_uploader("Upload a DOCX or PDF (<= 20 MB)", type=["docx", "pdf"])

def _validate_size(uploaded_file, max_mb: int) -> bool:
    if uploaded_file is None:
        return False
    size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
    return size_mb <= max_mb

results_df = None

if uploaded is not None:
    ok_size = _validate_size(uploaded, max_mb=rules_cfg.get("max_file_mb", 20))
    if not ok_size:
        st.error(f"File is larger than {rules_cfg.get('max_file_mb', 20)} MB limit. Please upload a smaller file.")
    else:
        filetype = uploaded.name.lower().split(".")[-1]
        with st.spinner("Reading file…"):
            start = time.time()
            if filetype == "docx":
                parsed = parse_docx(uploaded)
            elif filetype == "pdf":
                parsed = parse_pdf(uploaded)
            else:
                st.error("Unsupported file type.")
                st.stop()

            # Parsers may return (full_text, paragraphs) or (full_text, paragraphs, meta)
            if isinstance(parsed, tuple) and len(parsed) == 3:
                full_text, paragraphs, parser_meta = parsed
            elif isinstance(parsed, tuple) and len(parsed) == 2:
                full_text, paragraphs = parsed
                parser_meta = {}
            else:
                st.error("Parser returned unexpected format.")
                st.stop()

            # Merge parser-provided meta (e.g., images) with document meta
            meta = {"filename": uploaded.name, "language": lang, "paragraphs": paragraphs}
            if isinstance(parser_meta, dict):
                # parser_meta may include 'images' or other layout info
                meta.update(parser_meta)

            read_secs = time.time() - start

        st.success(f"File loaded in {read_secs:.1f}s. Length: {len(full_text):,} characters.")

        # Analyze button
        if st.button("Analyze", type="primary"):
            with st.spinner("Running checks…"):
                start = time.time()
                issues: List[Dict] = evaluate(full_text, {"filename": uploaded.name, "language": lang, "paragraphs": paragraphs, "meta": meta}, rules_cfg)
                took = time.time() - start

            if not issues:
                st.success(f"No issues found. Analysis completed in {took:.1f}s.")
            else:
                st.info(f"Found {len(issues)} issues. Analysis completed in {took:.1f}s.")
                results_df = pd.DataFrame(issues)

                # Apply severity filter
                if severity_filter:
                    results_df = results_df[results_df["severity"].isin(severity_filter)]

                st.subheader("Issues")
                st.dataframe(results_df, use_container_width=True)

                # Reviewer feedback: allow marking issues as false positives
                st.markdown("**Reviewer feedback**")
                idx_options = list(results_df.index)
                def _format_choice(i):
                    row = results_df.loc[i]
                    return f"{i}: {row.get('rule_id')} — {str(row.get('snippet'))[:80]}"

                selected = st.multiselect("Select issues to ignore (mark as false positives)", idx_options, format_func=_format_choice)
                if st.button("Save feedback (ignore selected)"):
                    # Save by uploaded filename (sanitise)
                    fname = os.path.splitext(uploaded.name)[0]
                    saved = save_feedback(fname, selected)
                    st.success(f"Saved feedback to {saved}")

                # Download CSV
                csv = results_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download CSV",
                    csv,
                    file_name=f"{os.path.splitext(uploaded.name)[0]}_issues.csv",
                    mime="text/csv",
                )

st.markdown("---")
st.caption("Report QA tool. Spelling: English only. Passive tone: heuristic. Files are not stored after analysis.")