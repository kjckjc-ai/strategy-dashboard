
import streamlit as st
import pandas as pd
from thefuzz import process
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("National datasheeet.csv")
    return df

df = load_data()

# Trust Search
st.title("Multi-Academy Trust Explorer")
st.markdown("Search for a Trust to view and explore all schools associated with it.")

trust_query = st.text_input("Enter Trust name (fuzzy search):")
selected_trust = None

if trust_query:
    unique_trusts = df['Trusts (name)'].dropna().unique()
    match, score = process.extractOne(trust_query, unique_trusts)
    if match:
        st.success(f"Best match: **{match}** (score: {score})")
        if st.button("Confirm Trust"):
            selected_trust = match

# Once confirmed, show schools in the trust
if selected_trust:
    trust_schools = df[df['Trusts (name)'] == selected_trust]

    st.header(f"Schools in: {selected_trust}")
    st.markdown(f"Total schools: **{trust_schools.shape[0]}**")

    # Filters
    phases = trust_schools['PhaseOfEducation (name)'].dropna().unique()
    selected_phases = st.multiselect("Filter by Phase of Education", phases, default=phases)

    filtered_schools = trust_schools[trust_schools['PhaseOfEducation (name)'].isin(selected_phases)]

    # Display school table
    st.subheader("School Details")
    st.dataframe(filtered_schools[[
        'EstablishmentName', 
        'TypeOfEstablishment (name)',
        'PhaseOfEducation (name)',
        'LA (name)',
        'SchoolWebsite'
    ]].reset_index(drop=True))

    # Plot map if coordinates exist
    st.subheader("Geographic Map of Schools")
    if 'Easting' in filtered_schools.columns and 'Northing' in filtered_schools.columns:
        # Convert Easting/Northing to Lat/Lon if necessary (simplified for demo)
        try:
            fig = px.scatter_mapbox(
                filtered_schools,
                lat=filtered_schools['Northing'],
                lon=filtered_schools['Easting'],
                hover_name='EstablishmentName',
                hover_data=['PhaseOfEducation (name)'],
                color='PhaseOfEducation (name)',
                zoom=5,
                height=500
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Map error: {e}")
    else:
        st.info("Easting/Northing data not available for mapping.")
