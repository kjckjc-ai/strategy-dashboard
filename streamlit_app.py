
import streamlit as st
import pandas as pd
from thefuzz import process
from io import BytesIO, StringIO
import os

st.set_page_config(layout="wide")

def authenticate(username, password):
    USERS = {"admin": "pass123", "user": "school2024"}
    return USERS.get(username) == password

with st.sidebar:
    st.title("Login")
    uname = st.text_input("Username", key="auth_user")
    pword = st.text_input("Password", type="password", key="auth_pass")
    if not authenticate(uname, pword):
        st.warning("Please enter valid credentials.")
        st.stop()
    else:
        st.success("Logged in")

@st.cache_data
def load_data():
    return pd.read_csv("National datasheeet.csv")

def fix_url(url):
    return "http://" + url if isinstance(url, str) and not url.startswith("http") else url

df = load_data()
df['SchoolWebsite'] = df['SchoolWebsite'].apply(fix_url)

trust_notes_dir = "trust_notes"
school_notes_dir = "school_notes"
os.makedirs(trust_notes_dir, exist_ok=True)
os.makedirs(school_notes_dir, exist_ok=True)

st.title("Multi-Academy Trust Dashboard")
trust_query = st.text_input("Enter Trust name (fuzzy search):", key="trust_query")
selected_trust = None
trust_key = ""

if trust_query:
    trusts = df['Trusts (name)'].dropna().unique()
    match, score = process.extractOne(trust_query, trusts)
    if match:
        st.success(f"Best match: **{match}** (score: {score})")
        if st.button("Confirm Trust"):
            st.session_state.selected_trust = match

selected_trust = st.session_state.get("selected_trust", None)

if selected_trust:
    trust_key = selected_trust.replace(" ", "_").replace("/", "_")
    trust_schools = df[df['Trusts (name)'] == selected_trust]

    st.header(f"Schools in Trust: {selected_trust}")
    st.markdown(f"**Total number of schools:** {trust_schools.shape[0]}")

    trust_note_path = os.path.join(trust_notes_dir, f"{trust_key}.txt")
    if trust_key not in st.session_state:
        if os.path.exists(trust_note_path):
            with open(trust_note_path, "r", encoding="utf-8") as f:
                st.session_state[trust_key] = f.read()
        else:
            st.session_state[trust_key] = ""

    st.subheader("Trust Notes")
    trust_notes = st.text_area("Write or edit notes below. Click 'Save Notes' to persist.", value=st.session_state[trust_key], key="trust_notes_area")
    if st.button("Save Trust Notes"):
        with open(trust_note_path, "w", encoding="utf-8") as f:
            f.write(trust_notes)
        st.success("Trust notes saved.")
        st.session_state[trust_key] = trust_notes

    st.text_input("Highlight schools by keyword (e.g., town, head)", key="search_term")

    total_pupils = pd.to_numeric(trust_schools['NumberOfPupils'], errors='coerce').dropna().sum()
    avg_size = total_pupils / trust_schools.shape[0] if trust_schools.shape[0] > 0 else 0
    most_common_gender = trust_schools['Gender (name)'].mode()[0] if not trust_schools.empty else "N/A"

    cols = st.columns(3)
    cols[0].metric("Total Pupils", f"{int(total_pupils):,}")
    cols[1].metric("Avg School Size", f"{int(avg_size):,}")
    cols[2].metric("Most Common Gender", most_common_gender)

    md_output = StringIO()
    md_output.write(f"# Trust Report: {selected_trust}\n\n")
    md_output.write(f"**Total Schools:** {trust_schools.shape[0]}\n\n")
    md_output.write(f"**Total Pupils:** {int(total_pupils):,}\n\n")
    md_output.write(f"**Average School Size:** {int(avg_size):,}\n\n")
    md_output.write(f"**Most Common Gender:** {most_common_gender}\n\n")
    md_output.write(f"## Trust Notes\n\n{trust_notes}\n\n")

    grouped = trust_schools.groupby('PhaseOfEducation (name)')
    for phase, group in grouped:
        st.markdown(f"### Phase: {phase}")
        md_output.write(f"### Phase: {phase}\n\n")
        for i in range(0, len(group), 2):
            row = group.iloc[i:i + 2]
            cols = st.columns(len(row))
            for j, (_, school) in enumerate(row.iterrows()):
                urn = str(school['URN'])
                school_key = f"{trust_key}_{urn}"
                school_note_path = os.path.join(school_notes_dir, f"{school_key}.txt")
                note_field_key = f"note_{school_key}"

                if note_field_key not in st.session_state:
                    if os.path.exists(school_note_path):
                        with open(school_note_path, "r", encoding="utf-8") as f:
                            st.session_state[note_field_key] = f.read()
                    else:
                        st.session_state[note_field_key] = ""

                with cols[j]:
                    highlight = st.session_state.search_term.lower() in str(school['Town']).lower() or                                     st.session_state.search_term.lower() in str(school['HeadFirstName']).lower() or                                     st.session_state.search_term.lower() in str(school['HeadLastName']).lower()

                    st.markdown(f"[{school['EstablishmentName']}]({school['SchoolWebsite']})")
                    st.markdown(f"- Gender: {school['Gender (name)']}")
                    st.markdown(f"- Religious: {school['ReligiousCharacter (name)']}")
                    st.markdown(f"- LA: {school['LA (name)']}")
                    st.markdown(f"- Pupils: {school['NumberOfPupils']}")
                    st.markdown(f"- FSM %: {school.get('PercentageFSM', 'N/A')}")
                    st.markdown(f"- Address: {school.get('Street', '')}, {school.get('Town', '')}, {school.get('Postcode', '')}")
                    head = f"{school.get('HeadTitle', '')} {school.get('HeadFirstName', '')} {school.get('HeadLastName', '')}"
                    st.markdown(f"- Head: {head.strip()}")

                    with st.form(key=f"form_{school_key}"):
                        note = st.text_area("Notes:", value=st.session_state[note_field_key], height=100, key=f"field_{school_key}")
                        if st.form_submit_button("Save Notes"):
                            with open(school_note_path, "w", encoding="utf-8") as f:
                                f.write(note)
                            st.success("Notes saved.")
                            st.session_state[note_field_key] = note

                    md_output.write(f"#### {school['EstablishmentName']}\n")
                    md_output.write(f"- Gender: {school['Gender (name)']}\n")
                    md_output.write(f"- Religious: {school['ReligiousCharacter (name)']}\n")
                    md_output.write(f"- LA: {school['LA (name)']}\n")
                    md_output.write(f"- Pupils: {school['NumberOfPupils']}\n")
                    md_output.write(f"- FSM %: {school.get('PercentageFSM', 'N/A')}\n")
                    md_output.write(f"- Address: {school.get('Street', '')}, {school.get('Town', '')}, {school.get('Postcode', '')}\n")
                    md_output.write(f"- Head: {head.strip()}\n")
                    md_output.write(f"- Notes: {st.session_state[note_field_key]}\n\n")

    st.subheader("Export Trust Report")
    st.download_button("Download Trust Report (Markdown)", md_output.getvalue(), file_name=f"{trust_key}_report.md")
    st.info("PDF export coming soon. This will convert the markdown summary into a downloadable PDF.")

    st.subheader("Download Raw Data")
    csv_data = trust_schools.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv_data, file_name=f"{trust_key}_schools.csv", mime="text/csv")
    excel_io = BytesIO()
    trust_schools.to_excel(excel_io, index=False, sheet_name="Trust Schools")
    st.download_button("Download Excel", data=excel_io.getvalue(), file_name=f"{trust_key}_schools.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
