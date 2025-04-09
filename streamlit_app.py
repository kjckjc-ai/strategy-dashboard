
import streamlit as st
import pandas as pd
from thefuzz import process
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("National datasheeet.csv")

df = load_data()

st.title("Multi-Academy Trust Dashboard v5")

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
    trust_schools = df[df['Trusts (name)'] == selected_trust]

    st.header(f"Schools in Trust: {selected_trust}")
    total_pupils = pd.to_numeric(trust_schools['NumberOfPupils'], errors='coerce').dropna().sum()
    st.metric("Total Pupils", f"{int(total_pupils):,}")

    # Filters
    with st.expander("Filters"):
        cols = st.columns(3)
        phases = df['PhaseOfEducation (name)'].dropna().unique()
        genders = df['Gender (name)'].dropna().unique()
        religions = df['ReligiousCharacter (name)'].dropna().unique()

        selected_phase = cols[0].selectbox("Phase", ["All"] + list(phases))
        selected_gender = cols[1].selectbox("Gender", ["All"] + list(genders))
        selected_religion = cols[2].selectbox("Religious", ["All"] + list(religions))

        if selected_phase != "All":
            trust_schools = trust_schools[trust_schools['PhaseOfEducation (name)'] == selected_phase]
        if selected_gender != "All":
            trust_schools = trust_schools[trust_schools['Gender (name)'] == selected_gender]
        if selected_religion != "All":
            trust_schools = trust_schools[trust_schools['ReligiousCharacter (name)'] == selected_religion]

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
                st.markdown(f"- Pupils: {school['NumberOfPupils']}")
                st.markdown(f"- FSM %: {school.get('PercentageFSM', 'N/A')}")
                st.markdown(f"- Address: {school.get('Street', '')}, {school.get('Town', '')}, {school.get('Postcode', '')}")
                head = f"{school.get('HeadTitle', '')} {school.get('HeadFirstName', '')} {school.get('HeadLastName', '')}"
                st.markdown(f"- Head: {head.strip()}")

    # Comparison tool
    st.subheader("Compare Selected Schools")
    compare_names = st.multiselect("Select schools to compare", trust_schools['EstablishmentName'])

    if compare_names:
        compare_df = trust_schools[trust_schools['EstablishmentName'].isin(compare_names)]
        st.dataframe(compare_df.reset_index(drop=True))

# Embed Ofsted Report Search Page
st.subheader("Search Ofsted Reports")
components.iframe("https://reports.ofsted.gov.uk/", height=600)
