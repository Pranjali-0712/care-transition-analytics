import pandas as pd
from pathlib import Path
from metrics import prepare_data

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'HHS_Unaccompanied_Alien_Children_Program.csv'
OUT = ROOT / 'outputs' / 'cleaned_care_transition_data.csv'

df = pd.read_csv(RAW)
clean = prepare_data(df)
clean.to_csv(OUT, index=False)
print(f'Saved {len(clean):,} records to {OUT}')
