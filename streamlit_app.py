
import streamlit as st
import pandas as pd
from thefuzz import process
from io import BytesIO

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
    trust_schools = df[df['Trusts (name)'] == selected_trust]
    st.header(f"Schools in Trust: {selected_trust}")
    st.markdown(f"**Total number of schools:** {trust_schools.shape[0]}")

    # KPI Section
    total_pupils = pd.to_numeric(trust_schools['NumberOfPupils'], errors='coerce').dropna().sum()
    avg_size = total_pupils / trust_schools.shape[0] if trust_schools.shape[0] > 0 else 0
    gender_counts = trust_schools['Gender (name)'].value_counts().to_dict()
    most_common_gender = max(gender_counts, key=gender_counts.get) if gender_counts else "N/A"

    cols = st.columns(3)
    cols[0].metric("Total Pupils", f"{int(total_pupils):,}")
    cols[1].metric("Avg School Size", f"{int(avg_size):,}")
    cols[2].metric("Most Common Gender", most_common_gender)

    # Group schools by phase
    st.subheader("Grouped School Profiles")
    grouped = trust_schools.groupby('PhaseOfEducation (name)')

    for phase, group in grouped:
        st.markdown(f"### Phase: {phase}")
        for i in range(0, len(group), 4):
            row = group.iloc[i:i + 4]
            cols = st.columns(len(row))
            for j, (_, school) in enumerate(row.iterrows()):
                with cols[j]:
                    st.markdown(f"**[{school['EstablishmentName']}]({school['SchoolWebsite']})**")
                    st.markdown(f"- Gender: {school['Gender (name)']}")
                    st.markdown(f"- Religious: {school['ReligiousCharacter (name)']}")
                    st.markdown(f"- LA: {school['LA (name)']}")
                    st.markdown(f"- Pupils: {school['NumberOfPupils']}")
                    st.markdown(f"- FSM %: {school.get('PercentageFSM', 'N/A')}")
                    st.markdown(f"- Address: {school.get('Street', '')}, {school.get('Town', '')}, {school.get('Postcode', '')}")
                    head = f"{school.get('HeadTitle', '')} {school.get('HeadFirstName', '')} {school.get('HeadLastName', '')}"
                    st.markdown(f"- Head: {head.strip()}")

    # Export section
    st.subheader("Download Data")
    csv_data = trust_schools.to_csv(index=False).encode('utf-8')
    st.download_button("Download as CSV", csv_data, file_name="trust_schools.csv", mime="text/csv")

    # Excel download
    excel_io = BytesIO()
    trust_schools.to_excel(excel_io, index=False, sheet_name="Trust Schools")
    st.download_button("Download as Excel", data=excel_io.getvalue(), file_name="trust_schools.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
