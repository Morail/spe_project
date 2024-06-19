import numpy as np
from scipy import stats as st
import pandas as pd


def load_df(stats):
    return pd.DataFrame(stats)

def compute_confidence_interval(data, confidence=0.95):
    mean = np.mean(data)
    sem = st.sem(data)
    interval = st.t.interval(confidence, len(data) - 1, loc=mean, scale=sem)
    return mean, interval
