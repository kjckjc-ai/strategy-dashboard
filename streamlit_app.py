
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("National datasheeet.csv")

df = load_data()

# Text search for school
st.title("1:1 iPad Strategy Generator for Schools")
query = st.text_input("Enter school name to search:")

matched_school = None
if query:
    matches = df[df['EstablishmentName'].str.contains(query, case=False, na=False)]
    if not matches.empty:
        matched_school = matches.iloc[0]
        st.success(f"Match found: {matched_school['EstablishmentName']}")
    else:
        st.warning("No school found. Try refining the name.")

# If a school is matched, show details
if matched_school is not None:
    st.subheader("School Information")
    st.write(f"**Local Authority:** {matched_school['LA (name)']}")
    st.write(f"**Phase of Education:** {matched_school.get('PhaseOfEducation (name)', 'N/A')}")
    st.write(f"**Age Range:** {matched_school.get('StatutoryLowAge', 'N/A')} - {matched_school.get('StatutoryHighAge', 'N/A')}")
    st.write(f"**Website:** [{matched_school['SchoolWebsite']}]({matched_school['SchoolWebsite']})")

    # Try to fetch and scrape website
    school_url = matched_school["SchoolWebsite"]
    st.subheader("Website Intelligence")

    try:
        response = requests.get(school_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Look for Ofsted-related links
        ofsted_links = [a['href'] for a in soup.find_all('a', href=True) if 'ofsted' in a['href'].lower()]
        strategy_links = [a['href'] for a in soup.find_all('a', href=True) if any(term in a['href'].lower() for term in ['strategy', 'improvement', 'vision'])]

        if ofsted_links:
            st.markdown("**Found potential Ofsted link(s):**")
            for link in ofsted_links:
                full_link = link if link.startswith("http") else school_url.rstrip("/") + "/" + link.lstrip("/")
                st.markdown(f"- [Ofsted]({full_link})")
        else:
            st.markdown("_No Ofsted links found on homepage._")

        if strategy_links:
            st.markdown("**Found potential strategy/vision link(s):**")
            for link in strategy_links:
                full_link = link if link.startswith("http") else school_url.rstrip("/") + "/" + link.lstrip("/")
                st.markdown(f"- [Strategy]({full_link})")
        else:
            st.markdown("_No strategy/vision links found on homepage._")

    except Exception as e:
        st.error(f"Could not fetch school website: {e}")

    # Nuanced, editable report
    st.subheader("Generated iPad Strategy Report")
    smart_report = f"""
## Strategic iPad Deployment Report for {matched_school['EstablishmentName']}

Based on findings from the school's website and leadership context, this tailored report outlines how 1:1 iPad use can strategically support the school's development:

### Leadership Alignment
- Integrate iPads into the School Improvement Plan and staff CPD frameworks.
- Ensure alignment with any digital leadership statements found on the school website.

### Inclusive Learning & Accessibility
- Use assistive technology features (text-to-speech, color filters, etc.).
- Ensure all learners benefit from differentiated digital learning environments.

### Technical Standards & Infrastructure
- Meet all [DfE digital standards](https://www.gov.uk/guidance/meeting-digital-and-technology-standards-in-schools-and-colleges).
- Ensure secure Wi-Fi, MDM, and internet filtering.

### Pedagogy & Curriculum
- Empower teachers with tools for formative assessment, feedback, and digital creativity.
- Encourage cross-curricular use (STEAM, media-rich projects).

### Monitoring & Evaluation
- Use analytics tools to monitor usage and impact.
- Review digital learning outcomes termly as part of SLT reviews.

_This strategy is adaptable based on further insights from Ofsted reports and published improvement plans._
"""
    edited = st.text_area("Edit the report as needed:", smart_report, height=500)

    st.download_button("Download Report (.md)", edited, file_name=f"{matched_school['EstablishmentName'].replace(' ', '_')}_ipad_strategy.md")
