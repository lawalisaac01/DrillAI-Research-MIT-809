# Start here

This package supports the MIT899 thesis draft **Design and Evaluation of an AI Based Drilling Decision Support System for the Nigerian Oil and Gas Industry**.

The full draft follows the supplied guide's five-chapter structure and Harvard author–date referencing. It contains a working research prototype and executed computational comparisons. The experiments use explicitly synthetic data. This is a complete research draft for review, not an already approved or field-validated submission.

## What is completed

- Review of AI applications across exploration, drilling, reservoirs, production, midstream, downstream and safety.
- Critical discussion of SLB Stream, Neuro, autonomous drilling and geosteering examples.
- Correction of the original national-target premise and separation of reserves from production.
- An executable seven-input drilling-rate predictor with a limited input quality gate.
- Mean, ridge and random forest comparisons on held out synthetic wells.
- Missing-data tests, a controlled input shift, five additional generator seeds and paired well resampling.
- An independent cost and schedule calculator, four scenarios and nine cost sensitivity combinations.
- Five substantive thesis chapters, references, data dictionary, evidence register and proposed field-validation protocol.
- Eleven computational consistency checks and four local HTTP endpoint checks. JavaScript syntax was checked. A real browser rendering test could not be completed in the build environment because its browser executable was unavailable. No field-user usability study was conducted.

## Where you need to come in

### 1. Obtain a decision on the research design today

Give your supervisor the title, abstract and Chapters Three and Four first. The critical question is whether an MIT899 software project evaluated with transparent synthetic data is acceptable for your submission. The attached guide describes a software design and development project, but it does not itself approve the changed topic or synthetic evaluation.

A concise explanation you can adapt is:

“I propose a focused software design and evaluation project on AI drilling decision support, with Nigerian economic implications. The prototype compares prediction methods using a transparent synthetic dataset and independently evaluates adoption cost scenarios. It does not claim Nigerian field results. May I proceed with this bounded design, or is an authorised field dataset or another form of validation mandatory?”

This is a suggested discussion prompt. Nothing has been sent to anyone.

If field data are mandatory, do not relabel the generated records as real. Seek permission for an existing anonymised dataset or an extension. We would need to rerun the study and revise the results and conclusions. A last-minute invented survey would not solve this problem.

### 2. Complete the administrative pages

Fill in your official full name, matriculation number, department/programme wording, supervisor and Head of Department. Personalise the dedication and acknowledgements. The certification page is deliberately an unsigned template. Complete it only through the actual institutional process. Check the university's rules on AI-assisted writing and coding and add any required disclosure.

The supplied guide does not specify a page minimum, exact paper size, margins or font. The draft uses Times New Roman, 12-point body text, 1.5 line spacing, Letter paper and a wider left margin. Confirm any additional departmental formatting requirements before printing; changing these will change pagination.

### 3. Reproduce and understand the work

Run the experiment and verification scripts. Inspect the CSV outputs. Open the app. Be able to explain why wells, rather than individual rows, are separated; what a regression error means; why the data are synthetic; why the gate can abstain; and why the cost scenarios are separate from the model's accuracy.

Your comparative analysis is already executed in the supplied package. Your task is to inspect, understand, reproduce and discuss it. You do not need to manufacture new responses or manually calculate hundreds of predictions.

### 4. Add genuine industry input only if available and permitted

A short technical review by an authorised drilling professional could improve the feature definitions and adoption discussion. Appendix D gives a proposed protocol. Such a review would be expert feedback, not proof that the model works on a Nigerian rig. Do not claim interviews, validation, a sample size or ethics approval unless they actually exist.

Actual cost quotations would improve the economic scenarios, but they must be permitted for use and clearly dated. With no quotation, retain the explicit illustrative labels. Every changed parameter requires a consistent update to the result table, discussion and conclusion.

## A practical three-day completion plan

| Period | Your action | Concrete result |
|---|---|---|
| Day 1 | Discuss title and synthetic design with supervisor; read abstract and Chapters 1, 3 and 4 | Confirmed research scope or a clear required change |
| Day 1 | Insert student details and inspect source references | Correct administrative pages and source familiarity |
| Day 2 | Run the package; reproduce baseline and stress results; try valid and unsuitable app inputs | Your own execution record and understanding of the results |
| Day 2 | Review with a relevant professional if permitted; incorporate only genuine feedback | Better technical interpretation without invented evidence |
| Day 3 | Read all chapters aloud or closely; resolve supervisor feedback; verify figures and references | Reviewed final text |
| Day 3 | Regenerate contents and lists after edits, confirm formatting, obtain actual signatures and submit | Institution-ready document after the necessary approvals |

Do not spend the three days building an autonomous drilling controller, conducting a rushed national survey or promising a causal GDP study. The defensible contribution here is the focused decision-support implementation and transparent evaluation.

## Run on Windows

1. Install Python 3.12 from the official Python installer if it is not installed. Enable the installer option that adds Python to PATH.
2. Extract this ZIP to a normal folder, for example `Documents\\DrillAI_Research_Package`.
3. Open that folder in File Explorer. Click its address bar, type `cmd`, and press Enter.
4. Run these commands, one line at a time:

```bat
py -3.12 -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.venv\\Scripts\\python.exe experiment.py
.venv\\Scripts\\python.exe verify.py
.venv\\Scripts\\python.exe app.py
```

5. Leave the command window open. In your browser, open `http://127.0.0.1:8990`.
6. Press Ctrl+C in the command window to stop the app.

If the `py` launcher is unavailable but `python --version` shows Python 3.12, use `python -m venv .venv` for the first command. If installation fails because a package version requires a newer interpreter, install Python 3.12 and recreate the environment instead of changing versions silently.

The first dependency installation needs internet access. After installation, experiments and the local app do not need an external API. The app is served only on your computer; it is not a phone-accessible deployment or a Vercel build.

## Run on macOS or Linux

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python experiment.py
.venv/bin/python verify.py
.venv/bin/python app.py
```

Open `http://127.0.0.1:8990` and stop with Ctrl+C.

## Quick demonstration

Use depth 2200 m, weight on bit 22 klbf, speed 120 rpm, flow 900 L/min, mud specific gravity 1.2, gamma ray 65 API and inclination 40 degrees. The status should be REVIEW with a synthetic rate prediction. Change speed to 500 rpm and submit again: the status should be ABSTAIN with the prediction withheld. Leave two fields blank: it should also abstain. These are input-guard demonstrations, not operational safety tests.

In the economics section, retain the central defaults to see negative campaign value. Change avoidable daily cost to 200000 and per-well AI cost to 100000. With the other defaults retained, campaign value should be approximately positive USD 347826. That demonstrates conditional economics; it does not establish a real quotation or an expected investment return.

## Read the output files

| File | Meaning |
|---|---|
| `results/synthetic_drilling.csv` | All 4800 artificial interval records |
| `results/manifest.json` | Seeds, well partitions, configuration and versions |
| `results/clean_metrics.csv` | Final mean, ridge and forest test results |
| `results/test_predictions.csv` | Held out observed synthetic targets and predictions |
| `results/stress_metrics.csv` | Missing-input and controlled-shift results |
| `results/replicate_metrics.csv` | Results for five additional generator seeds |
| `results/economic_scenarios.csv` | Four independent assumed adoption cases |
| `results/sensitivity.csv` | Nine cost combinations under central operational assumptions |
| `results/verification.json` | Eleven checks produced by verify.py |
| `results/http_verification.json` | Four endpoint checks completed in the build environment |
| `results/random_forest.joblib` | Fitted research model; regenerate when changing environments |

`simulator_rop_unclipped` is a debug target used for controlled-shift calculation, never a model input. No operator, SLB or confidential Nigerian records are included. Supplied books and articles are not redistributed in this package.

## Defence preparation

**What is innovative?** The integration of a small prediction workflow, explicit abstention and independent economic thresholds, with reproducible well-based evaluation. It is not a new machine learning algorithm or an assertion of first-ever novelty.

**Why not simply “benefits of AI in oil and gas”?** That topic is too broad for the guide's software implementation and experiment requirements. The thesis retains the broad review but evaluates one technical core.

**Why synthetic data?** No authorised field dataset was supplied. The generated dataset permits an honest, executable laboratory study. It limits external validity and cannot establish Nigerian drilling performance.

**Why random forest?** It can represent nonlinear structure in tabular data and was compared with simple alternatives. The generator deliberately contains nonlinear terms, so model superiority is interpreted narrowly.

**Why separate wells?** Intervals from a single well share characteristics. Splitting rows could let related observations appear in both fit and evaluation partitions and exaggerate generalisation.

**What does 29.1% mean?** The forest's mean absolute prediction error was approximately 29.1% lower than ridge regression on the primary synthetic test. It is not an achieved 29.1% drilling speed increase.

**Why are the default cost results negative?** Assumed avoidable savings are smaller than the specified adoption costs. Reporting this is a valid result, not a failure to prove a predetermined benefit.

**How does this support the Nigerian economy?** It identifies a method and conditions for evaluating adoption. National benefits would require verified field outcomes, cost evidence, local participation and a separate economic design. GDP and reserve additions were not measured.

**What does the gate guarantee?** Only compliance with its limited missingness and marginal-range rules. It is not calibrated uncertainty, well control or a safety-certified barrier.

## Final document editing

The Word draft is editable. Its contents and lists have page numbers matched to the delivered layout. They are static, so Ctrl+A and F9 will not regenerate those particular lists. If you change text or paper size, update the page entries manually, or replace the lists with Word's automatic contents and caption-based lists before your final print. The chapter and section headings already use Word heading styles. Check every final page.

The included `thesis_sources` folder preserves the chapter text and Harvard reference data for later revision. It is not a substitute for reviewing the Word document. A paper can later be developed from a narrower contribution, preferably after external validation.
