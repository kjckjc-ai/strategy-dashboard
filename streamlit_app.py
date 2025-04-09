
import streamlit as st
import pandas as pd
from thefuzz import process
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("National datasheeet.csv")

df = load_data()

st.title("Multi-Academy Trust Dashboard")

trust_query = st.text_input("Enter Trust name (fuzzy search):")
selected_trust = None

if trust_query:
    trusts = df['Trusts (name)'].dropna().unique()
    match, score = process.extractOne(trust_query, trusts)
    if match:
        st.success(f"Best match: **{match}** (score: {score})")
        if st.button("Confirm Trust"):
            selected_trust = match

if selected_trust:
    trust_schools_all = df[df['Trusts (name)'] == selected_trust]

    st.header(f"Schools in Trust: {selected_trust}")
    st.markdown(f"**Total number of schools:** {trust_schools_all.shape[0]}")
    total_pupils = pd.to_numeric(trust_schools_all['NumberOfPupils'], errors='coerce').dropna().sum()
    st.metric("Total Pupils", f"{int(total_pupils):,}")

    # Filter by phase only
    with st.expander("Filter by Phase"):
        phase_options = trust_schools_all['PhaseOfEducation (name)'].dropna().unique()
        selected_phase = st.selectbox("Select Phase", ["All"] + list(phase_options))

    trust_schools = trust_schools_all.copy()
    if selected_phase != "All":
        trust_schools = trust_schools[trust_schools['PhaseOfEducation (name)'] == selected_phase]

    # Grid layout for school data
    st.subheader("School Profiles")
    schools_per_row = 4
    for i in range(0, len(trust_schools), schools_per_row):
        row = trust_schools.iloc[i:i + schools_per_row]
        cols = st.columns(len(row))
        for j, (_, school) in enumerate(row.iterrows()):
            with cols[j]:
                st.markdown(f"### [{school['EstablishmentName']}]({school['SchoolWebsite']})")
                st.markdown(f"- Phase: {school['PhaseOfEducation (name)']}")
                st.markdown(f"- Gender: {school['Gender (name)']}")
                st.markdown(f"- Religious: {school['ReligiousCharacter (name)']}")
                st.markdown(f"- LA: {school['LA (name)']}")
                st.markdown(f"- Pupils: {school['NumberOfPupils']}")
                st.markdown(f"- FSM %: {school.get('PercentageFSM', 'N/A')}")
                st.markdown(f"- Address: {school.get('Street', '')}, {school.get('Town', '')}, {school.get('Postcode', '')}")
                head = f"{school.get('HeadTitle', '')} {school.get('HeadFirstName', '')} {school.get('HeadLastName', '')}"
                st.markdown(f"- Head: {head.strip()}")

    # Download CSV
    st.subheader("Download Data")
    csv_data = trust_schools.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data as CSV", csv_data, file_name="trust_schools.csv", mime="text/csv")

# Embed Ofsted Report Search Page
st.subheader("Search Ofsted Reports")
components.iframe("https://reports.ofsted.gov.uk/", height=800, scrolling=True)
