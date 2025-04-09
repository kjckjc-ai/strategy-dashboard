
import streamlit as st
import pandas as pd
from thefuzz import process

@st.cache_data
def load_data():
    return pd.read_csv("National datasheeet.csv")

df = load_data()

st.set_page_config(layout="wide")
st.title("Multi-Academy Trust Dashboard v4")

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
    
    st.header(f"Overview: {selected_trust}")
    
    total_pupils = pd.to_numeric(trust_schools['NumberOfPupils'], errors='coerce').dropna().sum()
    fsm_vals = pd.to_numeric(trust_schools['FSM'], errors='coerce').dropna()
    avg_fsm = fsm_vals.mean() if not fsm_vals.empty else 0

    st.metric("Total Pupils", f"{int(total_pupils):,}")
    st.metric("Average FSM %", f"{avg_fsm:.1f}%")

    # Optional Filters
    with st.expander("Filters"):
        cols = st.columns(4)
        phases = df['PhaseOfEducation (name)'].dropna().unique()
        genders = df['Gender (name)'].dropna().unique()
        religions = df['ReligiousCharacter (name)'].dropna().unique()
        types = df['TypeOfEstablishment (name)'].dropna().unique()

        selected_phase = cols[0].selectbox("Phase", ["All"] + list(phases))
        selected_gender = cols[1].selectbox("Gender", ["All"] + list(genders))
        selected_religion = cols[2].selectbox("Religious", ["All"] + list(religions))
        selected_type = cols[3].selectbox("Type", ["All"] + list(types))

        if selected_phase != "All":
            trust_schools = trust_schools[trust_schools['PhaseOfEducation (name)'] == selected_phase]
        if selected_gender != "All":
            trust_schools = trust_schools[trust_schools['Gender (name)'] == selected_gender]
        if selected_religion != "All":
            trust_schools = trust_schools[trust_schools['ReligiousCharacter (name)'] == selected_religion]
        if selected_type != "All":
            trust_schools = trust_schools[trust_schools['TypeOfEstablishment (name)'] == selected_type]

    st.subheader("Schools in this Trust")

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
                st.markdown(f"- Type: {school['TypeOfEstablishment (name)']}")
                st.markdown(f"- Pupils: {school['NumberOfPupils']}")
                st.markdown(f"- FSM %: {school['FSM']}")

    st.subheader("School Comparison")
    comparison_selection = st.multiselect("Select schools to compare", trust_schools['EstablishmentName'])

    if comparison_selection:
        compare_df = trust_schools[trust_schools['EstablishmentName'].isin(comparison_selection)]
        st.dataframe(compare_df.reset_index(drop=True))
