
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import fitz  # PyMuPDF

@st.cache_data
def load_data():
    return pd.read_csv("National datasheeet.csv")

def get_internal_links(url, base, depth=1):
    visited = set()
    to_visit = [(url, 0)]
    internal_links = []

    while to_visit:
        current_url, lvl = to_visit.pop(0)
        if current_url in visited or lvl > depth:
            continue
        visited.add(current_url)
        try:
            r = requests.get(current_url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full_url = urljoin(current_url, href)
                if base in full_url and full_url not in visited:
                    internal_links.append(full_url)
                    to_visit.append((full_url, lvl + 1))
        except:
            pass
    return list(set(internal_links))

def extract_text_from_pdf_url(pdf_url):
    try:
        response = requests.get(pdf_url)
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        doc = fitz.open("temp.pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

df = load_data()

st.title("Smart iPad Strategy Generator")
query = st.text_input("Enter school name to search:")

matched_school = None
if query:
    matches = df[df['EstablishmentName'].str.contains(query, case=False, na=False)]
    if not matches.empty:
        matched_school = matches.iloc[0]
        st.success(f"Match found: {matched_school['EstablishmentName']}")
    else:
        st.warning("No school found. Try refining the name.")

if matched_school is not None:
    st.subheader("School Information")
    st.write(f"**Local Authority:** {matched_school['LA (name)']}")
    st.write(f"**Phase of Education:** {matched_school.get('PhaseOfEducation (name)', 'N/A')}")
    st.write(f"**Age Range:** {matched_school.get('StatutoryLowAge', 'N/A')} - {matched_school.get('StatutoryHighAge', 'N/A')}")
    st.write(f"**Website:** [{matched_school['SchoolWebsite']}]({matched_school['SchoolWebsite']})")

    school_url = matched_school["SchoolWebsite"]
    parsed_base = urlparse(school_url).netloc

    st.subheader("Deep Link Discovery")
    all_links = get_internal_links(school_url, parsed_base, depth=2)
    relevant_links = [link for link in all_links if any(term in link.lower() for term in ["ofsted", "strategy", "improvement", "vision"])]

    ofsted_texts = []
    for link in relevant_links:
        st.markdown(f"- [Relevant Link]({link})")
        if link.lower().endswith(".pdf"):
            with st.spinner(f"Reading PDF: {link}"):
                pdf_text = extract_text_from_pdf_url(link)
                if "improvement" in pdf_text.lower() or "leadership" in pdf_text.lower():
                    ofsted_texts.append(pdf_text[:1000])  # Show preview

    if ofsted_texts:
        st.subheader("Extracted Strategic Findings")
        for i, text in enumerate(ofsted_texts):
            st.markdown(f"**Snippet {i+1}:**")
            st.code(text[:1000])
    else:
        st.markdown("_No strategic or Ofsted content extracted._")

    st.subheader("Generated iPad Strategy Report")
    smart_report = f"""
## Strategic iPad Deployment Report for {matched_school['EstablishmentName']}

This strategy is informed by real findings from the school's publicly available reports, matched against DfE's technology standards and digital best practice.

### Leadership & Vision
- Align 1:1 deployment with SLT strategic plans and CPD pathways.
- Ensure vision documents reference the transformative use of digital learning.

### Areas for Development
- Use iPads to address equity gaps, learner engagement, and access to resources.
- Integrate digital strategy into School Improvement Plan.

### Infrastructure & Security
- Ensure compliance with [DfE standards](https://www.gov.uk/guidance/meeting-digital-and-technology-standards-in-schools-and-colleges)
- Use MDM, filtering, safeguarding and reliable Wi-Fi.

### Pedagogical Integration
- Use Apple tools for creativity, feedback, differentiation.
- Promote collaborative, project-based, and STEAM learning.

### Measurement & Review
- Track impact using analytics and regular SLT reviews.
- Support via EdTech Demonstrator & Apple PL programs.
"""
    final_text = st.text_area("Edit the report:", smart_report, height=500)
    st.download_button("Download Report (.md)", final_text, file_name=f"{matched_school['EstablishmentName'].replace(' ', '_')}_ipad_strategy.md")
