
import streamlit as st
import pandas as pd
import plotly.express as px
from thefuzz import process
from pyproj import Transformer

@st.cache_data
def load_data():
    return pd.read_csv("National datasheeet.csv")

# Convert coordinates
def convert_coordinates(df):
    transformer = Transformer.from_crs("epsg:27700", "epsg:4326", always_xy=True)
    df = df.copy()
    df['Latitude'], df['Longitude'] = transformer.transform(df['Easting'].fillna(0), df['Northing'].fillna(0))
    df.loc[df['Latitude'] == 0, ['Latitude', 'Longitude']] = None
    return df

df = convert_coordinates(load_data())

st.title("Multi-Academy Trust Dashboard")

trust_query = st.text_input("Enter Trust name (fuzzy search):")
selected_trust = None

if trust_query:
    unique_trusts = df['Trusts (name)'].dropna().unique()
    match, score = process.extractOne(trust_query, unique_trusts)
    if match:
        st.success(f"Best match: **{match}** (score: {score})")
        if st.button("Confirm Trust"):
            selected_trust = match

if selected_trust:
    trust_schools = df[df['Trusts (name)'] == selected_trust]

    st.header("Trust Overview")
    st.markdown(f"**Trust Name:** {selected_trust}")
    websites = trust_schools['SchoolWebsite'].dropna().unique()
    if len(websites) > 0:
        st.markdown(f"**Sample School Website:** [{websites[0]}]({websites[0]})")
    total_pupils = trust_schools['NumberOfPupils'].dropna().astype(float).sum()
    avg_fsm = trust_schools['FSM'].dropna().astype(float).mean()
    st.metric("Total Pupils", f"{int(total_pupils):,}")
    st.metric("Average FSM %", f"{avg_fsm:.1f}%")

    # Filters
    st.subheader("Filter Schools")
    phases = trust_schools['PhaseOfEducation (name)'].dropna().unique()
    genders = trust_schools['Gender (name)'].dropna().unique()
    religions = trust_schools['ReligiousCharacter (name)'].dropna().unique()
    types = trust_schools['TypeOfEstablishment (name)'].dropna().unique()

    selected_phases = st.multiselect("Phase of Education", phases, default=list(phases))
    selected_genders = st.multiselect("Gender", genders, default=list(genders))
    selected_religions = st.multiselect("Religious Character", religions, default=list(religions))
    selected_types = st.multiselect("Type of Establishment", types, default=list(types))

    filtered = trust_schools[
        trust_schools['PhaseOfEducation (name)'].isin(selected_phases) &
        trust_schools['Gender (name)'].isin(selected_genders) &
        trust_schools['ReligiousCharacter (name)'].isin(selected_religions) &
        trust_schools['TypeOfEstablishment (name)'].isin(selected_types)
    ]

    st.subheader("School Table")
    st.dataframe(filtered[[
        'EstablishmentName', 'PhaseOfEducation (name)', 'Gender (name)', 
        'ReligiousCharacter (name)', 'TypeOfEstablishment (name)', 
        'NumberOfPupils', 'FSM', 'SchoolWebsite'
    ]].reset_index(drop=True))

    st.subheader("Visual Breakdown")
    st.plotly_chart(px.pie(filtered, names='TypeOfEstablishment (name)', title='School Types'))
    st.plotly_chart(px.bar(filtered, x='PhaseOfEducation (name)', title='Schools by Phase', color='PhaseOfEducation (name)'))
    st.plotly_chart(px.pie(filtered, names='Gender (name)', title='Gender Distribution'))
    st.plotly_chart(px.pie(filtered, names='ReligiousCharacter (name)', title='Religious Character'))
    st.plotly_chart(px.histogram(filtered, x='NumberOfPupils', nbins=20, title='Distribution of Pupil Numbers'))
    st.plotly_chart(px.histogram(filtered, x='FSM', nbins=20, title='FSM % Distribution'))

    st.subheader("Geographic Map")
    mappable = filtered.dropna(subset=['Latitude', 'Longitude'])
    if not mappable.empty:
        fig = px.scatter_mapbox(
            mappable,
            lat="Latitude",
            lon="Longitude",
            hover_name="EstablishmentName",
            color="PhaseOfEducation (name)",
            zoom=5,
            height=500
        )
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig)
    else:
        st.info("No geographic data available.")
