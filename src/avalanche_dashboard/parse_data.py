import pandas as pd
from constants import state_centroids


def fill_latlon(df: pd.DataFrame) -> pd.DataFrame:
    # Replace (0, 0) coordinates with state centroids
    for idx, row in df.iterrows():
        if row['lat'] == 0.0 and row['lon'] == 0.0:
            state = row['State']
            centroid = state_centroids.get(state, (0, 0))  # Default to (0, 0) if state not found
            df.at[idx, 'lat'] = centroid[0]
            df.at[idx, 'lon'] = centroid[1]
            
    
    return df
    
