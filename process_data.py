import numpy as np
import pandas as pd
import altair as alt
import streamlit
import vega_datasets
import os

def read_csv(fl):
    to_remove = ['index', 'measure_id','measure_name', 'age_id', 'metric','measure_ID']
    df = pd.read_csv(fl)
    df = df.drop(columns = [col for col in df.columns if col in to_remove])
    df['State'] = df.loc[0,'location_name']
    return df

def read_states():
    main_dir = 'data/states'
    fls = os.listdir(main_dir)
    data_list = []
    for fl in fls:
        if os.path.splitext(os.path.join(main_dir,fl))[1].lower() == '.csv':
            data_list.append(read_csv(os.path.join(main_dir,fl)))
    df_mort = pd.concat(data_list)
    df_mort = df_mort.reset_index(drop=True)
    df_mort = df_mort.dropna(subset=['FIPS'])
    df_mort["id"] = df_mort["FIPS"].astype(int)
    return df_mort