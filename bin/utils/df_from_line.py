import pandas as pd

def df_from_line(line): 
    pairs = line.strip('[]').split(', ')
    data = {k: v for k, v in (pair.split(':') for pair in pairs)}

    return pd.DataFrame([data])