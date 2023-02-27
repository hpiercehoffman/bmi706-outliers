import numpy as np
import pandas as pd
import altair as alt
import streamlit
import vega_datasets
from glob import glob

def read_csv(fl):
    to_remove = ['index', 'measure_id','measure_name', 'age_id', 'metric','measure_ID']
    df = pd.read_csv(fl)
    df = df.drop(columns = [col for col in df.columns if col in to_remove])
    df['State'] = df.loc[0,'location_name']
    return df

def read_states():
    fls = glob('data/states/*')
    data_list = []
    for fl in fls:
        data_list.append(read_csv(fl))
    df_mort = pd.concat(data_list)
    df_mort = df_mort.reset_index(drop=True)
    return df_mort