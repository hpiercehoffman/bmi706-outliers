import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

import process_data

@st.cache_data

# Cache state data from CSV files, dropping entries without a FIPS code
def collect_state_data():
    state_df = process_data.read_states()
    state_df = state_df.dropna(subset=['FIPS'])
    state_df["id"] = state_df["FIPS"].astype(int)
    return state_df

state_df = collect_state_data()

# Chart title
st.write("Mortality rates by county")

# Multi-select widget for mortality causes
display_causes = st.multiselect(
    label="Select one or more mortality causes",
    options=state_df["cause_name"].unique(),
    default="Alcohol use disorders"
)
subset_df = state_df[state_df.cause_name.isin(display_causes)]

# Radio buttons to select sex
display_sex = st.radio(
    label="Select a sex to display",
    options=("Male", "Female", "Both"),
    index=0
)
subset_df = subset_df[subset_df.sex == display_sex]

# Slider widget to select year
display_year = st.slider(
    label="Select a year",
    min_value=1980,
    max_value=2014,
    value=1990
)
subset_df = subset_df[subset_df.year_id == display_year]

counties = alt.topo_feature(data.us_10m.url, 'counties')
source = subset_df

us_mort = alt.Chart(counties).mark_geoshape().encode(
    color=alt.Color('mx:Q')
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(data=source, key='id', fields=['mx'])
).project(
    "albersUsa"
).properties(
    width=800,
    height=500
)

chart_mort = alt.vconcat(us_mort).resolve_scale(
        color = 'independent')

st.altair_chart(chart_mort,
    use_container_width=False)
