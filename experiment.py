"""Synthetic research demonstrator. No field data; no rig control. Python 3.10+."""
from pathlib import Path
import json, platform, sys
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'; FIG=ROOT/'figures'
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
FEATURES=['depth_m','wob_klbf','rpm','flow_lpm','mud_sg','gamma_api','inclination_deg']
SEED=899

def generate(seed=SEED):
    rng=np.random.default_rng(seed); rows=[]
    for well in range(48):
        effect=rng.normal(0,2.0)
        for interval in range(100):
            depth=800+interval*22+rng.uniform(-8,8)
            wob=rng.uniform(10,35); rpm=rng.uniform(70,190)
            flow=rng.uniform(600,1200); mud=rng.uniform(1.05,1.5)
            gamma=np.clip(65+25*np.sin(interval/14+well)+rng.normal(0,12),15,125)
            inc=rng.uniform(0,85)
            signal=(25+.22*wob+.12*rpm-.003*(rpm-115)**2-.03*(wob-22)**2
                    +.012*(flow-900)-.000015*(flow-900)**2-.15*gamma-.0014*depth
                    -3*(mud-1.15)-.045*inc+3*np.sin(wob/9)*np.cos(rpm/55)+effect)
            unclipped=signal+rng.normal(0,2.5)
            rop=np.clip(unclipped,3,75)
            rows.append([well,interval,depth,wob,rpm,flow,mud,gamma,inc,rop,unclipped])
    return pd.DataFrame(rows,columns=['well_id','interval_id']+FEATURES+['rop_mph','simulator_rop_unclipped'])

def metrics(y,p):
    return dict(MAE=float(mean_absolute_error(y,p)),RMSE=float(np.sqrt(mean_squared_error(y,p))),R2=float(r2_score(y,p)))

def rf(depth,leaf):
    return make_pipeline(SimpleImputer(strategy='median'),RandomForestRegressor(n_estimators=180,max_depth=depth,min_samples_leaf=leaf,random_state=SEED,n_jobs=-1))

def scenario(u,npt_reduction,realization,ai_cost=250000,day_cost=100000,length=3000,rop=20,npt=5,other=15,wells=10,fixed=1000000):
    drill_days=length/rop/24
    saved=realization*(drill_days*(u/(1+u))+npt*npt_reduction)
    baseline=drill_days+npt+other
    net=saved*day_cost-ai_cost
    return dict(rop_uplift=u,npt_reduction=npt_reduction,realization=realization,days_saved=saved,
                baseline_days=baseline,new_days=baseline-saved,gross_saving=saved*day_cost,
                ai_cost=ai_cost,net_per_well=net,campaign_net=wells*net-fixed,
                break_even_day_cost=(ai_cost+fixed/wells)/saved if saved>0 else None,
                break_even_realization=(ai_cost+fixed/wells)/(day_cost*(drill_days*u/(1+u)+npt*npt_reduction)) if (u>0 or npt_reduction>0) else None)

def quality_gate(frame,trained):
    missing=frame.isna().sum(axis=1)>1
    out_of_range=((frame<trained.min()) | (frame>trained.max())).any(axis=1)
    # Deliberately simple engineering guard, not calibrated uncertainty.
    return ~(missing|out_of_range)

def main():
    df=generate(); df.to_csv(OUT/'synthetic_drilling.csv',index=False)
    train=df[df.well_id<32]; val=df[(df.well_id>=32)&(df.well_id<40)]; test=df[df.well_id>=40]
    x,y=train[FEATURES],train.rop_mph
    configs=[(8,5),(14,3),(None,8)]; candidates=[]; fitted=[]
    for depth,leaf in configs:
        m=rf(depth,leaf);m.fit(x,y);score=mean_absolute_error(val.rop_mph,m.predict(val[FEATURES]))
        candidates.append(dict(max_depth=depth,min_samples_leaf=leaf,validation_MAE=float(score))); fitted.append(m)
    best=int(np.argmin([v['validation_MAE'] for v in candidates]))
    # Lock the winning configuration; fit train+validation once, before all tests.
    combined=pd.concat([train,val]);cx=combined[FEATURES];cy=combined.rop_mph
    models={'Mean baseline':make_pipeline(SimpleImputer(strategy='median'),DummyRegressor(strategy='mean')),
            'Ridge regression':make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),Ridge(alpha=10)),
            'Random forest':rf(*configs[best])}
    scores=[];pred={}
    for name,m in models.items():
        m.fit(cx,cy);p=m.predict(test[FEATURES]);pred[name]=p
        scores.append(dict(model=name,**metrics(test.rop_mph,p)))
    pd.DataFrame(scores).to_csv(OUT/'clean_metrics.csv',index=False)
    prediction=test[['well_id','interval_id','rop_mph']].copy()
    for name,p in pred.items(): prediction[name]=p
    prediction.to_csv(OUT/'test_predictions.csv',index=False)
    err=prediction.assign(ridge_abs=abs(prediction.rop_mph-prediction['Ridge regression']),rf_abs=abs(prediction.rop_mph-prediction['Random forest'])).groupby('well_id')[['ridge_abs','rf_abs']].mean()
    differences=err.ridge_abs.to_numpy()-err.rf_abs.to_numpy()
    rng=np.random.default_rng(900);boots=rng.choice(differences,size=(2000,len(differences)),replace=True).mean(axis=1)
    ci=np.quantile(boots,[.025,.975]).tolist()
    stress=[]
    for rate in [0,.1,.3,.5]:
        damaged=test[FEATURES].copy(); rng=np.random.default_rng(1000+int(rate*100))
        damaged=damaged.mask(rng.random(damaged.shape)<rate)
        accept=quality_gate(damaged,cx)
        for name,m in models.items():
            p=m.predict(damaged)
            row=dict(condition=f'{rate:.0%} missing',model=name,coverage=float(accept.mean()),**metrics(test.rop_mph,p))
            row['accepted_MAE']=float(mean_absolute_error(test.rop_mph[accept],p[accept])) if accept.any() else None
            stress.append(row)
    # Covariate shift: higher RPM +30, gamma +20, target generated from same response
    # difference except noise/effect retained. Tests extrapolation, not a new field.
    shifted=test[FEATURES].copy(); original_rpm=shifted.rpm.copy(); original_gamma=shifted.gamma_api.copy()
    shifted.rpm+=30;shifted.gamma_api+=20
    delta=(.12*30-.003*((shifted.rpm-115)**2-(original_rpm-115)**2)-.15*20
           +3*np.sin(shifted.wob_klbf/9)*(np.cos(shifted.rpm/55)-np.cos(original_rpm/55)))
    shifted_y=np.clip(test.simulator_rop_unclipped+delta,3,75)
    accept=quality_gate(shifted,cx)
    for name,m in models.items():
        p=m.predict(shifted)
        stress.append(dict(condition='Shifted RPM and gamma',model=name,coverage=float(accept.mean()),accepted_MAE=float(mean_absolute_error(shifted_y[accept],p[accept])) if accept.any() else None,**metrics(shifted_y,p)))
    pd.DataFrame(stress).to_csv(OUT/'stress_metrics.csv',index=False)
    replicates=[]
    for rep_seed in [900,901,902,903,904]:
        rep=generate(rep_seed);rt=rep[rep.well_id<40];re=rep[rep.well_id>=40]
        for name,model in [('Ridge regression',make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),Ridge(alpha=10))),('Random forest',rf(*configs[best]))]:
            model.fit(rt[FEATURES],rt.rop_mph)
            replicates.append(dict(seed=rep_seed,model=name,**metrics(re.rop_mph,model.predict(re[FEATURES]))))
    pd.DataFrame(replicates).to_csv(OUT/'replicate_metrics.csv',index=False)
    cases=[dict(name='No benefit',**scenario(0,0,.5)),dict(name='Conservative',**scenario(.05,.05,.5)),dict(name='Central',**scenario(.15,.15,.75)),dict(name='Favourable',**scenario(.30,.25,.9))]
    pd.DataFrame(cases).to_csv(OUT/'economic_scenarios.csv',index=False)
    sensitivity=[dict(day_cost=c,ai_cost=a,**{k:v for k,v in scenario(.15,.15,.75,ai_cost=a,day_cost=c).items() if k not in ['ai_cost']}) for c in [50000,100000,200000] for a in [100000,250000,400000]]
    pd.DataFrame(sensitivity).to_csv(OUT/'sensitivity.csv',index=False)
    manifest=dict(seed=SEED,rows=len(df),wells=48,train_wells=list(range(32)),validation_wells=list(range(32,40)),test_wells=list(range(40,48)),features=FEATURES,candidates=candidates,selected=candidates[best],bootstrap_difference_mean=float(differences.mean()),bootstrap_95_percentile_interval=ci,bootstrap_resamples=2000,python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__,platform=platform.platform(),evidence='Entirely synthetic; not calibrated to Nigeria or SLB; no field validation')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    joblib.dump(models['Random forest'],OUT/'random_forest.joblib')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(7,4));ax.bar([s['model'] for s in scores],[s['MAE'] for s in scores],color=['#8b969b','#668b9a','#176355']);ax.set_ylabel('Held out well MAE (m/h)');ax.set_title('Synthetic data only');fig.tight_layout();fig.savefig(FIG/'model_comparison.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,4.5));ax.scatter(test.rop_mph,pred['Random forest'],s=9,alpha=.35,color='#176355');ax.plot([0,50],[0,50],color='black',lw=1);ax.set(xlabel='Synthetic observed ROP (m/h)',ylabel='Predicted ROP (m/h)',title='Random forest on eight unseen synthetic wells');fig.tight_layout();fig.savefig(FIG/'predicted_observed.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4));ax.bar([v['name'] for v in cases],[v['campaign_net']/1e6 for v in cases],color=['#aa5555','#ba8653','#668b9a','#176355']);ax.axhline(0,color='black',lw=.8);ax.set_ylabel('Ten well campaign net value (USD million)');ax.set_title('Assumptions only — not an industry forecast');fig.tight_layout();fig.savefig(FIG/'economic_scenarios.png',dpi=180);plt.close(fig)
    print(pd.DataFrame(scores).to_string(index=False));print(pd.DataFrame(cases)[['name','days_saved','net_per_well','campaign_net','break_even_day_cost']].to_string(index=False));print('CI ridge minus RF MAE',ci)
    print(pd.DataFrame(stress).to_string(index=False))
if __name__=='__main__': main()
