# Algorithms, frameworks, tools and libraries, with the reasons

Source text for the Word file (a subsection at the end of Section 16, "Model training and calibrated risk"). Written on 1 November 2026. Versions were read from the environment of the tested laptop (`importlib.metadata`, `node_modules`, `docker --version`). `backend/requirements.txt` and `frontend/package.json` give only lower bounds.

<!-- word:start -->
## Algorithms, frameworks, tools and libraries

This subsection records what was chosen for each part of the pipeline, why, and which alternative from the literature was not chosen. The reasons rely on the evidence tables of Sections 4 to 7 and on the references M1 to M6. They justify the choices for a small, inspectable prototype; they do not claim that the choices are the best possible.

<!-- widths 1700,2600,3000,2593 -->
| Part | Choice in the prototype | Reason | Alternative not chosen, and why |
|---|---|---|---|
| Unit of detection | A session: one user on one PC from Logon to Logoff | An analyst gets a bounded window to inspect. S1 is the closest task match. | Daily windows or single events (S5, S8) are a different task and harder to review. Session graphs (S7) need graph-building rules. |
| Class imbalance | Class weights in Logistic Regression, a positive-class weight in XGBoost; validation and test parts keep their natural prevalence | Held-out data stays unchanged, so precision is not inflated (Section 8). | Oversampling such as SMOTE (S2, S12, S16) changes the training distribution and the outcome depends on the sampler. |
| Model 1 | Logistic Regression with scaled inputs and balanced class weights | A simple supervised comparison for the other models. | None; it is the reference. |
| Model 2 | XGBoost: 200 trees, depth 4, learning rate 0.1, subsample 0.9 | S1 reports it as the strongest method for session detection; it handles nonlinear tabular features. The shap library has a tree explainer for it. | Deep networks (S2, S5) need more data and are harder to explain. Sequence input is not available from session counts. |
| Model 3 | Isolation Forest, 200 trees, trained without labels | A label-free signal that complements the supervised scores (S19, M3). | Sequence detectors such as LSTM (S11) need event sequences, which the session counts do not keep. |
| Personal baseline | Running mean and standard deviation per user (Welford), deviation capped at 10, trusted after 5 sessions, standard deviation floor 0.5 | Uses only earlier sessions, updates in one pass and gives an explanation such as “3 standard deviations above this user’s normal”. | Peer-group comparison is out of scope. Learned user representations would be harder to explain. |
| Calibration | A two-parameter sigmoid (Platt scaling) per model, fitted on validation data only, with mild regularization | Puts three different scores on one probability scale before they are combined (M6). | Isotonic regression has more freedom and so needs more malicious examples than the small validation part holds (see M6). |
| Combination | Weighted average of the calibrated scores; each weight is the model’s share of the validation F1 | Simple, and the weights are stored with the run so that they can be inspected. | Equal weights are compared in experiment C. Stacking needs more labelled data. |
| Flag threshold | The threshold with the best F1 on validation data, used for the combined score and for each single model | No test label takes part in any choice. | A fixed cut such as 50 ignores prevalence. A threshold chosen on test labels is too optimistic. |
| Explanation | SHAP contributions of XGBoost (top three positive) and the top three differences from the user’s baseline, in plain words | The analyst sees model reasons and user-relative reasons together (M4). | Explaining all three models was not done; the dashboard states that the reasons belong to XGBoost. |
| Data split | Time order: first 70% training, next 15% validation, last 15% test | Past data predicts later data, so no future information is used (Section 3). | A random split suits only some tasks (Section 3). |
| Assistant | Evidence ids from one stored session; hosted model through the Anthropic Messages API with a statement check; local template as fallback | Read-only, evidence only, and it still works without a key. | A free-text hosted answer without checks could state facts that the evidence does not hold. |

<!-- widths 1900,3000,2000,2993 -->
| Tool or library | Role | Version tested | Why it was chosen |
|---|---|---|---|
| Python | Language of the engine, API and scripts | 3.14.6 | One language for all backend code and the test suite. |
| pandas | Chunked CSV reading, merging events into sessions, grouping | 3.0.6 (needs 2.2 or newer) | read_csv with chunks and selected columns keeps memory low; merge_asof attaches an event to the session that contains it. |
| NumPy | Array calculations | 2.5.4 (needs 1.26 or newer) | Required by the other numerical libraries. |
| scikit-learn | Logistic Regression, Isolation Forest, scaling, sigmoid fitting, metrics | 1.9.1 (needs 1.4 or newer) | One library for three of the four modelling jobs and for precision, recall, F1, average precision and Brier score. |
| XGBoost | Main classifier | 3.4.1 (needs 2.0 or newer) | See Model 2 above. |
| SHAP | Contributions of XGBoost features | 0.54.1 (needs 0.45 or newer) | Gives one contribution per feature for each prediction (M4). |
| joblib | Saving and loading trained models | 1.6.0 (needs 1.3 or newer) | Standard way to store scikit-learn and XGBoost models; the bytes are hashed with SHA-256. |
| FastAPI, Pydantic, uvicorn | REST API, strict request models, server | 0.150.0, 2.14.1, 0.54.0 (FastAPI needs 0.110 or newer) | Request models reject unexpected fields and wrong types; interactive documentation at /docs. |
| MongoDB and PyMongo | Database and its Python driver | MongoDB image mongo:7; PyMongo 4.19.0 (needs 4.6 or newer) | Documents hold the nested explanation of a session without joins; validation rules and indexes; GridFS stores the model files. |
| bcrypt and PyJWT | Password hashes and signed 30-minute tokens | 5.0.0 and 2.15.1 (need 4.1 and 2.8 or newer) | Established libraries for these two jobs. |
| httpx | Call to the hosted model | 0.28.1 (needs 0.27 or newer) | Timeout and status handling in one call; failures fall back to the offline answer. |
| pytest and mongomock | Tests with an in-memory database | 9.1.1 and 4.3.0 (need 8.0 and 4.1 or newer) | The tests run without a database server; one extra test uses a real server when it is configured. |
| React and Vite | Dashboard and its build and development server | 18.3.1 and 5.4.21 | Four pages and no state library; Vite proxies /api to the API during development. |
| Node.js | Runs the Vite build | 26.5.0 | Needed for the build. |
| Docker and Docker Compose | Local MongoDB | 29.6.2 and 5.3.1 | Same database setup on every team laptop; a second compose file adds authentication and separate accounts. |

The versions are those installed on the tested laptop on 1 November 2026. Because the requirement files give lower bounds only, the resolved versions should be archived with any reported result (Section 19).

Second environment, 5 November 2026: Python 3.14.5, Docker 29.9.2, MongoDB image mongo:7, npm 10.9.2, Vite 5.4.21. The resolved Python packages of this environment are archived in `backend/requirements.lock.txt`.
<!-- word:end -->
