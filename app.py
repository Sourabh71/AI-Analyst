
import streamlit as st
import pdfplumber
import requests
import json
import os

# ------------------------ Tailwind-style Styling ------------------------
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f9f9f9;
    }
    .main {padding: 20px;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        border-radius: 12px;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #2b2b2b; }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------ Page Title ------------------------
st.title("📊 AI Assistant for Financial Statement Analysis")
st.markdown("Upload a financial PDF file (Press Release, Balance Sheet, P&L, etc.), and get AI-powered financial ratios and insights.")

# ------------------------ PDF Upload ------------------------
uploaded_file = st.file_uploader("📄 Upload PDF File", type=["pdf"])

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    st.success("✅ Text extracted from PDF successfully!")

    # ------------------------ AI Extraction via OpenRouter ------------------------
    st.subheader("🧠 Step 1: AI-Based Financial Value Extraction")
    if st.button("Run LLM Extraction"):
        with st.spinner("Calling AI..."):

            OPENROUTER_API_KEY = "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"

            prompt = f"""
Read the following financial press release or statement and extract the key financial values:
- Total Revenue
- EBITDA
- PAT (Net Profit)
- EPS
- Any other useful financial numbers
Then calculate: PAT Margin, EBITDA Margin, ROE (assume 7389 Cr equity if not found), and interpret the financial health.

Text:
\"\"\"
{full_text[:12000]}
\"\"\"
"""

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "mistralai/mixtral-8x7b-instruct",
                "messages": [{"role": "user", "content": prompt}],
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )

            if response.status_code == 200:
                result = response.json()
                try:
                    output_text = result['choices'][0]['message']['content']
                    st.success("✅ AI Analysis Ready!")
                    st.markdown(f"### 🧾 AI Output:\n\n{output_text}")
                except Exception:
                    st.error("❌ Couldn't extract AI content from response.")
            else:
                st.error(f"❌ API Error: {response.status_code}\n\n{response.text}")

    # ------------------------ Basic Table Detection ------------------------
    st.subheader("📊 Step 2: Detect Tables (like Balance Sheet/P&L)")
    if st.button("Parse Tables"):
        found_table = False
        with pdfplumber.open(uploaded_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    found_table = True
                    st.write(f"📄 Table found on page {page_num + 1}")
                    for table in tables:
                        st.table(table)
        if not found_table:
            st.warning("⚠️ No tables found in PDF pages using `extract_tables()`.")

    # ------------------------ Optional: Statement Type Detector ------------------------
    st.subheader("🔍 Step 3: Auto-Detect Statement Type")
    if "balance sheet" in full_text.lower():
        st.info("📘 This document likely contains a Balance Sheet.")
    elif "profit and loss" in full_text.lower() or "p&l" in full_text.lower():
        st.info("📙 This document likely contains a Profit & Loss Statement.")
    elif "cash flow" in full_text.lower():
        st.info("📗 This document likely contains a Cash Flow Statement.")
    else:
        st.warning("❓ Could not confidently detect statement type.")

# ------------------------ Footer ------------------------
st.markdown("---")
st.caption("🚀 Built with ❤️ using Streamlit + LLMs | By Saurabh Yadav")
