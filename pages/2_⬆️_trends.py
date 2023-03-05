import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

import process_data

# Configure how the page appears in browser tab
st.set_page_config(page_title="Explore Trends", page_icon="⬆️")

@st.cache_data

def collect_diff_data():
    diff_df = process_data.read_diff_csv()
    return diff_df

def collect_state_data():
    state_df = process_data.read_states()
    state_df = state_df.dropna(subset=['FIPS'])
    state_df["id"] = state_df["FIPS"].astype(int)
    return state_df

diff_df = collect_diff_data()
state_df = collect_state_data()

st.title("Explore trends in the data")

with st.sidebar:
    # Selectbox widget for mortality cause
    display_cause = st.selectbox(
        label="Select a mortality cause",
        options=state_df["cause_name"].unique(),
        index=0
    )
    # Radio buttons to select sex
    display_sex = st.radio(
        label="Select a sex to display",
        options=("Male", "Female", "Both"),
        index=0
    )

subset_df = diff_df[diff_df.cause_name == display_cause]
subset_df = subset_df[subset_df.sex == display_sex]

# Map of the U.S. by counties
counties = alt.topo_feature(data.us_10m.url, 'counties')
source_diff = diff_df

# Map showing the US colored by percent change in mortality
mort_diff = alt.Chart(counties).mark_geoshape().encode(
    color=alt.Color("pc_change_val:Q", title="Percent change in mortality")
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(data=source_diff,
                         key='id',
                         fields=['pc_change_val'])
).project(
    "albersUsa"
).properties(
    title="Percent Change in Mortality",
    width=800,
    height=600
)

chart_trend = alt.hconcat(mort_diff).resolve_scale(
    color='independent'
)

st.altair_chart(chart_trend,
    use_container_width=False)
