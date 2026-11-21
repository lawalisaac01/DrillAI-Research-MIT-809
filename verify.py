"""Meaningful consistency checks; not field or user validation."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from app import evaluate
from experiment import scenario, FEATURES
ROOT=Path(__file__).resolve().parent
checks=[]
def check(name,condition):
    checks.append({'check':name,'passed':bool(condition)})
    if not condition: raise AssertionError(name)
m=json.loads((ROOT/'results/manifest.json').read_text())
check('Disjoint train validation test wells',not(set(m['train_wells'])&set(m['validation_wells']) or set(m['train_wells'])&set(m['test_wells']) or set(m['validation_wells'])&set(m['test_wells'])))
df=pd.read_csv(ROOT/'results/synthetic_drilling.csv')
check('Exactly 4800 rows and 48 wells',len(df)==4800 and df.well_id.nunique()==48)
check('No response or simulator debug target in features','rop_mph' not in FEATURES and 'simulator_rop_unclipped' not in FEATURES)
s=scenario(.15,.15,.75)
check('Central days saved match independent arithmetic',np.isclose(s['days_saved'],.75*((3000/20/24)*(1-1/1.15)+5*.15)))
check('Fixed campaign cost included',np.isclose(s['campaign_net'],10*(s['gross_saving']-250000)-1000000))
check('Zero benefit still incurs costs',scenario(0,0,.75)['campaign_net']==-3500000)
payload=dict(depth_m=2200,wob_klbf=22,rpm=120,flow_lpm=900,mud_sg=1.2,gamma_api=65,inclination_deg=40)
check('Valid synthetic input produces review prediction',evaluate(payload)['status']=='REVIEW')
check('Out of range measurement withholds prediction',evaluate(dict(payload,rpm=500))['prediction_mph'] is None)
check('Two missing measurements cause abstention',evaluate(dict(payload,rpm=None,flow_lpm=None))['status']=='ABSTAIN')
check('One missing measurement can be imputed',evaluate(dict(payload,rpm=None))['status']=='REVIEW')
try: evaluate(dict(payload,rpm='NaN'));failed=False
except ValueError: failed=True
check('Nonfinite input rejected',failed)
(ROOT/'results/verification.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
