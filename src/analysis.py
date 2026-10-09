import pandas as pd
from pathlib import Path
from metrics import prepare_data, monthly_summary

ROOT = Path(__file__).resolve().parents[1]
df = prepare_data(pd.read_csv(ROOT/'data'/'HHS_Unaccompanied_Alien_Children_Program.csv'))
monthly_summary(df).to_csv(ROOT/'outputs'/'monthly_summary.csv', index=False)
print('Analysis tables generated.')
