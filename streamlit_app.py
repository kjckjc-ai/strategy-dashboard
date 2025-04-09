
import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv("National datasheeet.csv")

df = load_data()

st.title("1:1 iPad Strategy Advisor for Schools")
st.markdown("""
This tool analyzes school context and leadership priorities using Ofsted reports and national benchmarks to generate tailored recommendations for 1:1 iPad deployment.
""")

school_names = df['EstablishmentName'].dropna().unique()
selected_school = st.selectbox("Select a school", sorted(school_names))

school_data = df[df['EstablishmentName'] == selected_school].iloc[0]
school_website = school_data.get("SchoolWebsite", "N/A")

st.subheader("School Info")
st.write(f"**Local Authority:** {school_data['LA (name)']}")
st.write(f"**Type:** {school_data['TypeOfEstablishment (name)']}")
st.write(f"**Website:** [{school_website}]({school_website})")

st.subheader("Ofsted Report Summary (Mocked)")
st.markdown("""
**Leadership & Vision:**  
The leadership team has demonstrated a clear vision centered on inclusive learning, student engagement, and digital integration.

**Areas for Improvement:**  
- Enhance digital literacy across the curriculum  
- Address attainment gaps using adaptive technology  
- Improve access to remote learning resources
""")

st.subheader("Suggested iPad Deployment Strategy")
default_report = f"""
## Strategic Use of iPads at {selected_school}

Based on the leadership's vision and current challenges highlighted in the Ofsted report, we recommend:

### 1. Leadership Alignment
- Align iPad use with CPD plans and digital strategy documents.
- Embed digital learning in the School Improvement Plan.

### 2. Accessibility & Equity
- Deploy assistive tools (text-to-speech, magnification).
- Provide staff training to personalize learning via iPads.

### 3. Infrastructure & Support
- Ensure filtering, device management (MDM), and secure Wi-Fi per [DfE standards](https://www.gov.uk/guidance/meeting-digital-and-technology-standards-in-schools-and-colleges).
- Implement monitoring tools to safeguard and measure use.

### 4. Curriculum Integration
- Use iPads for adaptive assessments and formative feedback.
- Support cross-subject projects with multimedia capabilities.

*For further development, consider Apple Professional Learning and DfE's EdTech Demonstrator Programme.*
"""

edited_report = st.text_area("Editable Report", default_report, height=400)

if st.button("Export Report (Markdown)"):
    st.download_button("Download", edited_report, file_name=f"{selected_school}_ipad_strategy.md")
