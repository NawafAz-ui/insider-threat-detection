# Evaluation criteria, measurable indicators and test cases

Source text for the Word file (a subsection at the end of Section 17, "Detection evaluation and comparisons"). Written on 1 November 2026. All values come from generated CERT-layout data on one laptop (Apple M4 Pro, 12 cores, 24 GB, macOS 26.6.2, Python 3.14.6). They are not research findings and say nothing about real logs.

How to repeat the numbers:
- Detection: `cd backend && python scripts/run_experiments.py --seeds 5` (about 10 seconds, no database; writes `reports/experiments.json`).
- Batch time and memory: `/usr/bin/time -l python -m itd.engine --data data/cert_synthetic --retrain` against a temporary database (`DB_NAME=...`).
- API time: 200 requests per endpoint (100 for chat) with the FastAPI test client against the same database; median and 95th percentile.
- Tests: `pytest -q`, and with `ITD_TEST_MONGO=mongodb://127.0.0.1:27017` for the real-server test.

<!-- word:start -->
## Evaluation criteria, measurable indicators and test cases

This subsection turns the evaluation plan above into indicators with a definition, a rule for judging the value, a way to measure it and the value measured so far, and lists the test cases with their recorded result. The detection values are the mean over five generated data sets (seeds 7 to 11; 120 users, 90 days, 12 insiders each) with the lowest and highest value in brackets. Each data set has 13 to 16 malicious sessions in its test part, so one session moves precision or recall by several points. Every threshold was chosen on validation data. The data is much easier than real logs, so the values show that the measuring works, not how good the detector is.

<!-- widths 1900,2600,2000,3393 -->
| Indicator | Definition | Rule for judging it | Value on generated data, all 39 features, combined score |
|---|---|---|---|
| Precision | TP / (TP + FP), malicious class as positive | No fixed target; report with the counts | 0.96 (0.80 to 1.00) |
| Recall | TP / (TP + FN) | No fixed target; report with the counts | 0.94 (0.85 to 1.00) |
| F1 | 2PR / (P + R) at the validation threshold | Compare configurations on the same data sets | 0.95 (0.89 to 1.00) |
| Average precision | sklearn average_precision_score; stored under the key pr_auc | Must be far above the no-skill value, which equals the test prevalence (1.2% to 1.5%) | 0.99 (0.93 to 1.00) |
| False positives per 1,000 benign sessions | 1000 × FP / benign sessions of the test part | Judged by analyst workload | 0.7 (0.0 to 3.7) |
| Alerts per 1,000 sessions | 1000 × flagged / sessions of the test part | Judged by analyst workload | 13.3 |
| Recall in the top 20 | Malicious test sessions among the 20 highest scores / all malicious test sessions | Shows the value of a fixed review budget of 20 sessions | 0.98 |
| Brier score | Mean squared difference between risk/100 and the label | Lower is better; compare calibrated with raw scores | 0.0009, against 0.0034 for raw scores |
| Batch run time | Wall time of python -m itd.engine | Report with the data size | 1.2 s of processing and 3.1 s with start-up for 7,329 sessions and 108,635 events |
| Peak memory | Maximum resident set size of the engine process | Report with the data size; not inferred for larger data | 322,846,720 bytes (about 308 MiB) for the same run |
| API response time | Median and 95th percentile of repeated authenticated requests | Under two seconds (NF3) | List 3.7 and 5.4 ms; detail 2.7 and 3.5 ms; user history 5.1 and 6.5 ms; latest run 2.0 and 3.1 ms; offline chat 2.5 and 3.8 ms |
| Page load in a browser | Navigation until the content appears | Under two seconds (NF3) | Not measured |
| Test pass rate | Tests passed / tests run | All pass; skipped tests are named | 42 passed and 1 skipped (the real-server test); 43 passed with a real MongoDB server |

The API times were taken in the same process, without a network and without a browser, so they show that the server work is small, not what an analyst experiences. The memory and time values are for 7,329 sessions only; the full CERT r4.2 data has 32.8 million events and has not been run.

<!-- widths 1900,3000,2000,2993 -->
| Comparison | Configuration | F1, mean (lowest to highest) | Other values (mean) |
|---|---|---|---|
| A single models | Logistic Regression | 0.94 (0.82 to 1.00) | Average precision 0.99; precision 1.00; recall 0.90 |
| A single models | XGBoost | 0.98 (0.96 to 1.00) | Average precision 0.98; precision 0.99; recall 0.97 |
| A single models | Isolation Forest | 0.75 (0.70 to 0.83) | Average precision 0.74; precision 0.93; recall 0.64 |
| B feature groups | 28 session features | 0.92 (0.89 to 1.00) | Precision 0.96; recall 0.90 |
| B feature groups | plus 10 deviations | 0.96 (0.89 to 1.00) | Precision 0.96; recall 0.96 |
| B feature groups | plus recency (all 39) | 0.95 (0.89 to 1.00) | Precision 0.96; recall 0.94 |
| C combination rule | Best single model (Logistic Regression) | 0.94 (0.82 to 1.00) | Brier 0.0006 |
| C combination rule | Equal weights | 0.95 (0.89 to 1.00) | Brier 0.0011 |
| C combination rule | Weights from validation F1 | 0.95 (0.89 to 1.00) | Brier 0.0009 |
| D raw or calibrated | Raw scores | 0.95 (0.92 to 1.00) | Precision 0.98; recall 0.93; Brier 0.0034 |
| D raw or calibrated | Calibrated scores | 0.95 (0.89 to 1.00) | Precision 0.96; recall 0.94; Brier 0.0009 |

What the comparisons show, and what they do not. XGBoost is the strongest single model, as S1 reports for its own data, and Isolation Forest the weakest. Adding the ten deviation features raised the mean F1 from 0.92 to 0.96, but the ranges overlap, so five data sets do not establish an improvement. Equal weights and weights from validation F1 give the same F1, so the weighting rule did not matter here, and the best single model is as good as the combination. Calibration lowered the Brier score from 0.0034 to 0.0009 and did not change F1. Experiment E, the transfer to SPEDIA, was not run because the real file has not been mapped.

<!-- widths 700,1100,5400,2693 -->
| ID | Requirement | What the test does | Result |
|---|---|---|---|
| TC1 | FR1 | test_missing_log_file_and_wrong_date_format_stop_the_run: a folder without logon.csv gives the “Missing in” message; a date in another format stops the run. | Passed |
| TC2 | FR2 | test_sessionization_rules: normal session, missing logoff closed by the next logon, 12-hour cap, session across midnight. | Passed |
| TC3 | FR1, FR3 | test_aggregator_counts_per_session: device, email, file and web counts per session. | Passed |
| TC4 | FR3 | test_feature_count (39 features); test_day_counts_use_only_the_sessions_up_to_the_current_one (dropping later sessions changes no earlier value). | Passed |
| TC5 | FR3 | test_baseline_uses_only_past_sessions; test_working_gap_ignores_weekend. | Passed |
| TC6 | FR3, FR4 | test_running_the_same_data_again_does_not_count_it_twice; test_a_later_batch_continues_the_saved_baseline_and_recency. | Passed |
| TC7 | FR4 | test_model_tamper_is_detected: a changed saved model is refused. | Passed |
| TC8 | FR5 | test_risk_engine_weights_and_threshold; test_calibration_keeps_the_order_and_is_fitted_on_validation_scores; test_evaluate_model_uses_the_given_threshold_not_the_test_labels; test_stored_models_keep_calibrators_and_validation_thresholds. | Passed |
| TC9 | FR6 | test_top_shap_is_positive_and_at_most_three; test_list_sorted_and_detail. | Passed |
| TC10 | FR7 | test_login_and_auth; test_unknown_role_and_expired_token; test_injection_rejected; test_login_throttle_last. | Passed |
| TC11 | FR7 | test_list_sorted_and_detail: list sorted by risk, detail within 0 to 100 with at most 3 reasons. | Passed |
| TC12 | FR8 | test_chat_names_fields_and_is_logged; test_assistant_gets_no_identifiers; test_llm_answer_is_validated; test_hosted_statements_are_checked_one_by_one; test_hosted_answer_says_so_when_no_statement_is_supported; test_hosted_reply_in_the_old_format_uses_the_offline_answer; three offline answer tests. | Passed, with fake hosted replies only |
| TC13 | FR9 | The access log gets an entry for each assistant question and each user view (test_chat_names_fields_and_is_logged, test_user_history_endpoint). Login and session-view entries are not asserted by a test. | Passed for the two actions tested |
| TC14 | FR10 | test_user_history_endpoint; test_user_history_rejects_bad_input. | Passed |
| TC15 | FR11 | test_latest_run_endpoint. | Passed |
| TC16 | FR12 | test_health_endpoint; test_database_down_gives_a_clear_503; test_unexpected_error_hides_internal_details. | Passed |
| TC17 | FR13 | test_stored_documents_follow_the_schema; test_results_are_linked_to_their_run; test_schema_rejects_bad_documents; test_real_mongo_enforces_the_schema. | Passed; the last one needs a real MongoDB server |
| TC18 | RQ1 | test_both_workflows_end_to_end: list, detail, chat, user history and back to another session. | Passed (API side) |
| TC19 | NF3 | test_list_is_fast: the session list answers in under two seconds. | Passed |
| TC20 | NF4 | test_https_required_when_enabled: plain HTTP is refused with 426. | Passed; real TLS not tested |
| TC21 | RQ5 | test_spedia_adapter_and_cross_eval: conversion and cross-dataset run on a stand-in file. | Passed; no real SPEDIA data |

Not covered by an automated test: duplicate and boundary events (FR2), unique event ids (FR1), the dashboard (there are no frontend tests; the new results table and CSV download were checked by building the app and by rendering them with sample data, not in a browser), real TLS and trusted certificates, the hosted model with a real key, page timing in a browser and encrypted storage. The demonstration scripts on the main database (Section 21) add manual checks of the database rules and of 13 API calls.
<!-- word:end -->
