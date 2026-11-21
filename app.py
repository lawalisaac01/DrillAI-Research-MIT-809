"""Local research UI. Bind loopback only. Never use for operational rig decisions."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json, math
import joblib
import pandas as pd
from experiment import FEATURES, scenario, quality_gate
ROOT=Path(__file__).resolve().parent
MODEL=joblib.load(ROOT/'results/random_forest.joblib')
TRAIN=pd.read_csv(ROOT/'results/synthetic_drilling.csv').query('well_id < 40')[FEATURES]

def evaluate(data):
    values=[]
    for name in FEATURES:
        value=data.get(name)
        if value is None or value=='': values.append(float('nan'));continue
        value=float(value)
        if not math.isfinite(value): raise ValueError('Inputs must be finite numbers or blank.')
        values.append(value)
    row=pd.DataFrame([values],columns=FEATURES)
    allowed=bool(quality_gate(row,TRAIN).iloc[0])
    reasons=[]
    if row.isna().sum(axis=1).iloc[0]>1: reasons.append('More than one input is missing.')
    for feature in FEATURES:
        value=row[feature].iloc[0]
        if not pd.isna(value) and not TRAIN[feature].min()<=value<=TRAIN[feature].max(): reasons.append(feature+' is outside the training range.')
    return dict(status='REVIEW' if allowed else 'ABSTAIN',prediction_mph=float(MODEL.predict(row)[0]) if allowed else None,reasons=reasons,notice='Synthetic model only. Human review required. No rig control or field validation.')

class Handler(BaseHTTPRequestHandler):
    def send_json(self,obj,status=200):
        body=json.dumps(obj,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=='/':
            body=(ROOT/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(body)
        elif self.path=='/api/results': self.send_json(dict(metrics=pd.read_csv(ROOT/'results/clean_metrics.csv').to_dict('records'),ranges={c:[float(TRAIN[c].min()),float(TRAIN[c].max())] for c in FEATURES}))
        else:self.send_json({'error':'Not found'},404)
    def do_POST(self):
        if self.path!='/api/predict': self.send_json({'error':'Not found'},404);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n>16384:raise ValueError('Request too large')
            data=json.loads(self.rfile.read(n))
            if not isinstance(data,dict):raise ValueError('Expected an object')
            self.send_json(evaluate(data))
        except (ValueError,TypeError) as e:self.send_json({'error':str(e)},400)
if __name__=='__main__':
    print('Open http://127.0.0.1:8990 — Ctrl+C stops the research demonstrator')
    HTTPServer(('127.0.0.1',8990),Handler).serve_forever()
