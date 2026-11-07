# Fix list for Group7_Research_and_Methodology.docx

Each fix changes only the wrong words and keeps your own wording, so the text keeps its human style. Style and small grammar points were left out on purpose.

How to use: in Word, press Cmd+F, search for the text after "Find", and replace it with the text after "Replace with". Work from the top and tick the box when done. Every "Find" text appears exactly once in the current file (checked 6 November 2026).

61 fixes in 3 groups:
1. Wrong facts, numbers or structure: fixes 1 to 34
2. Text that contradicts the figures: fixes 35 to 43
3. Sentences that say something different from what is meant: fixes 44 to 61

## 1. Wrong facts, numbers or structure (fix first)

- [ ] **1. Section 8: heading 8.1 is missing.** Add the line "8.1 Data in use" in the Heading 2 style, right under the heading "8. Data and preprocessing" (above the bullet that starts "The demonstration includes a generator"). Why: Section 10.1 cites Section 8.1.

- [ ] **2. 9.1, the 39 columns.**
  Find: `9 for timing, 9 for general activity, 2 for device, 5 for file, 5 for email, 5 for web, and 2 for same-day context (whole day session starts with weekend days removed), and 1 for recency (days since last contact with user).`
  Replace with: `9 for timing and general activity, 2 for device, 5 for file, 5 for email, 5 for web, 2 for same-day context, 10 for deviations from the user's history, and 1 for recency (time between the user's session starts, with whole weekend days removed).`
  Why: the numbers now add up to 39; before, they added up to 38 and left out the 10 deviations.

- [ ] **3. 12.1, the second run.**
  Find: `The score and flag were the same for every 7,329 session for a second run after retraining.`
  Replace with: `The score and flag were the same for all 7,329 sessions for a second run without retraining.`

- [ ] **4. 12.2, Issue 14 plan.**
  Find: `The idea is to take a session off the baseline only after it has completed`
  Replace with: `The idea is to add a session to the baseline only after it has completed`

- [ ] **5. 8.1, SPEDIA is already published.**
  Find: `and will be published on Zenodo under CC BY 4.0 licence without attempting to identify anyone.`
  Replace with: `and is published on Zenodo under CC BY 4.0 licence; it will be used without attempting to identify anyone.`

- [ ] **6. 11, the statement check.**
  Find: `and the statement is retained if it refers to an evidence id that exists and all the numbers in it are present in the evidence ids`
  Replace with: `and the statement is retained only if it refers to an evidence id that exists and all the numbers in it are present in the cited evidence`

- [ ] **7. 11, when no statement is left.**
  Find: `the answer states that there is no evidence stored.`
  Replace with: `the answer states that the stored evidence does not support an answer.`

- [ ] **8. 11, the evidence and the question.**
  Find: `The evidence is untagged, but the analyst's question is sent to it,`
  Replace with: `The evidence leaves out user and PC names, but the analyst's question is sent with it,`

- [ ] **9. 10.1, experiment C.**
  Find: `C compares the best single model (equal weights and validation-F1 weights)`
  Replace with: `C compares the best single model, equal weights and validation-F1 weights`

- [ ] **10. 10.2, the weights result.**
  Find: `The validation F1 had equal weights and weights both gave 0.95.`
  Replace with: `Equal weights and the validation F1 weights both gave 0.95.`

- [ ] **11. 10.2, the F1 ranking.**
  Find: `as the best result was obtained by XGBoost alone (0.98) followed by Logistic Regression (0.94), Isolation Forest (0.75), and the combined score (0.95).`
  Replace with: `as the best mean F1 over the five data sets was obtained by XGBoost alone (0.98), followed by the combined score (0.95), Logistic Regression (0.94) and Isolation Forest (0.75).`
  Why: the combined score (0.95) is second, not last.

- [ ] **12. 9.2, the flag threshold.**
  Find: `The flag threshold is one threshold among several that is calculated using the validation data with the best F1,`
  Replace with: `The flag threshold is whichever candidate value gives the best F1 on the validation data,`

- [ ] **13. 9.2, the calibration setting.**
  Find: `with a and b optimized with logistic regression on the scores`
  Replace with: `with a and b optimized with logistic regression (C = 10) on the scores`

- [ ] **14. 12.1, the database rebuild.**
  Find: `Rebuilt main database from a backup:`
  Replace with: `Rebuilt main database after a backup:`
  Why: a backup was taken first; nothing was restored from it.

- [ ] **15. 12.1, the date and the build result (two edits).**
  Find: `At commit ac8afa9,`
  Replace with: `On 4 November 2026, at commit ac8afa9,`
  Find: `npm run build returned 41 modules.`
  Replace with: `npm run build passed with 41 modules.`

- [ ] **16. 12.1, the demo scripts.**
  Find: `That demo script was passed onto that database,`
  Replace with: `The demo scripts all passed on that database,`

- [ ] **17. 12.1, the fixed issues.**
  Find: `day counts end at current session,`
  Replace with: `day counts end at current session, re-runs rebuild the baseline, offline answer and SHAP heading corrected,`
  Why: issues 5 to 7 are called fixed, but their fixes were missing from the list.

- [ ] **18. 12.2, the Issue 14 test.**
  Find: `(the later session should not be the one that has been opened, and the first session should be the one that has been flagged), a long test on later sessions`
  Replace with: `(the later session's baseline should not include the session that is still open), an extended test on later sessions`
  Why: the "flagged" condition is not part of the plan.

- [ ] **19. 12.2, the Issue 13 fallback order.**
  Find: `then the alternative is to remove the old records at the end and replace them with the new run id one by one.`
  Replace with: `then the alternative is to write the records one by one under the new run id and remove the old ones at the end.`

- [ ] **20. 12.2, the Issue 13 staging collections.**
  Find: `staging collections, which are the same as the old ones, and the counts will be done,`
  Replace with: `staging collections, which follow the same rules as the old ones, and the counts will be checked,`

- [ ] **21. 9.1, overlapping sessions.**
  Find: `and the totals from the first may be recorded on a baseline that is already filled, but the user scores have not yet been completed`
  Replace with: `and the later one may then be compared with a baseline that already includes the first one's totals, even though that session has not finished yet`

- [ ] **22. 8.2, the run-link check.**
  Find: `so a check will be done for the run link separately.`
  Replace with: `so a separate test checks the run link.`
  Why: the test already exists.

- [ ] **23. 4, the status definitions (two edits).**
  Find: `a run over generated evidence`
  Replace with: `a run over generated data`
  Find: `Met on generated data means that the software behaves as expected, a result`
  Replace with: `Met on generated data only means that the software behaves as expected; a result`

- [ ] **24. 10.2, the data set size.**
  Find: `12 insiders respectively)`
  Replace with: `12 insiders each)`

- [ ] **25. 10.2, what the laptop measured.**
  Find: `The measurements were performed on one laptop`
  Replace with: `The time and memory measurements were performed on one laptop`

- [ ] **26. 1, all results are from generated data.**
  Find: `Any of the results reported here`
  Replace with: `All of the results reported here`

- [ ] **27. 8.1, the seed.**
  Find: `120 users, 90 days (default values) and 12 insiders,`
  Replace with: `120 users, 90 days and 12 insiders (default values, seed 7),`

- [ ] **28. 8.1, overclaim.**
  Find: `It's enough to prove that method is technically sound,`
  Replace with: `It's enough to show the method is technically sound,`

- [ ] **29. 3, the four design options.**
  Find: `detect on the session, instead of oversampling, use class weights, and use a personal baseline (with thresholds set on validation data; see Section 9.3`
  Replace with: `detect on the session, use class weights instead of oversampling, split the data by time with thresholds set on validation data, and use a personal baseline (see Section 9.3`
  Why: the options were mixed up and the split by time was missing.

- [ ] **30. 3, the proposal's claim.**
  Find: `The proposed attributes, which are stronger than the evidence, are not included in any selected study.`
  Replace with: `The proposal claims that none of the selected studies has all of these attributes, which is stronger than the evidence.`

- [ ] **31. 9.2, the noisy calibration.**
  Find: `and there are a few malicious sessions, which results in a noisy fitted curve;`
  Replace with: `and there are few malicious sessions in it, so the fitted curve may be noisy;`

- [ ] **32. 9.2, the missing conclusion.**
  Find: `but calibration and weighting do require labels.`
  Replace with: `but calibration and weighting do require labels, so the combined score still depends on labels.`

- [ ] **33. 12.2, overclaim.**
  Find: `will prove that it works when it is tested`
  Replace with: `will show that it works when it is tested`

- [ ] **34. 10.2, the deviation result.**
  Find: `do not constitute an improvement;`
  Replace with: `do not prove an improvement;`

## 2. Text that contradicts the figures

- [ ] **35. 5.2, Figure 2 has four parties.**
  Find: `with two sets of parties: the log sources and the administrator, the security analyst,`
  Replace with: `with four parties: the log sources, the administrator, the security analyst,`

- [ ] **36. 6, who uses the dashboard.**
  Find: `Only the security analyst can access the dashboard and view the stored results,`
  Replace with: `The security analyst only uses the dashboard and can view the stored results,`
  Why: an admin account can also use the dashboard.

- [ ] **37. 6, the administrator's tasks.**
  Find: `operates from the command line, initiates the batch run, creates user accounts,`
  Replace with: `operates from the command line, places the log files, initiates the batch run, manages analyst accounts,`

- [ ] **38. 6, the hosted model is optional.**
  Find: `The hosted language model is an external service`
  Replace with: `The hosted language model is an optional external service`

- [ ] **39. 5.1, tiers.**
  Find: `The prototype is of three levels (Figure 1).`
  Replace with: `The prototype is of three tiers (Figure 1).`

- [ ] **40. 7, stages.**
  Find: `It has ten steps as shown in Figure 5`
  Replace with: `It has ten stages as shown in Figure 5`

- [ ] **41. 7, the batch flow.**
  Find: `The result is a batch flow that the administrator runs,`
  Replace with: `First is a batch flow that the administrator runs,`
  Why: Figure 5 has two flows; stages 1 to 7 are the batch flow.

- [ ] **42. 7, the assistant.**
  Find: `and the assistant interacts with the data (10)`
  Replace with: `and the assistant answers from one session's evidence (10)`

- [ ] **43. 5.1, the four pages.**
  Find: `four pages are provided, sign-in, flagged list, last run panel, session page and assistant, and user page with risk timeline.`
  Replace with: `four pages are provided: sign-in, flagged list with last run panel, session page with assistant, and user page with risk timeline.`

## 3. Sentences that say something different from what is meant

- [ ] **44. 1, the opening sentence.**
  Find: `The insider activity is already legitimate in the logs, so there is no point in them reading it one by one, and there are too many events for anyone to have legitimate access to.`
  Replace with: `Insider activity looks legitimate in the logs because insiders already have access, and there are far too many events for anyone to read them one by one.`

- [ ] **45. 5.1, the batch flow.**
  Find: `you can start the engine, which will read the CSV logs and write the scored session, user base line and run record`
  Replace with: `the administrator can start the engine, which will read the CSV logs and write the scored sessions, user baselines and run record`

- [ ] **46. 5.1, the analyst flow.**
  Find: `The analyst flow is a view of the dashboard that calls the REST API,`
  Replace with: `The analyst flow is the dashboard calling the REST API,`

- [ ] **47. 5.1, which evidence.**
  Find: `pass a copy of this evidence`
  Replace with: `pass a copy of the session's evidence`

- [ ] **48. 5.2, what the hosted model gets.**
  Find: `The hosted model is fed evidence from one stored session, not the raw logs, and the analyst's question.`
  Replace with: `The hosted model is fed evidence from one stored session and the analyst's question, not the raw logs.`

- [ ] **49. 5.3, tense.**
  Find: `None of the API modules will be imported into the engine.`
  Replace with: `None of the API modules are imported into the engine.`

- [ ] **50. 8.2, the outputs sentence (two edits).**
  Find: `This is because each run will produce`
  Replace with: `Each run will produce`
  Find: `while a run training will also produce`
  Replace with: `while a training run will also produce`

- [ ] **51. 9.1, the column order.**
  Find: `so the order of the columns will be preserved with the models.`
  Replace with: `and the order of the columns is preserved with the models.`

- [ ] **52. 9.2, the test part.**
  Find: `The test part is not used with any threshold, weight or model choice; it is merely reported to provide results.`
  Replace with: `The test part is not used for any threshold, weight or model choice; it is only used to report results.`

- [ ] **53. 11, pseudonymous data.**
  Find: `The code does not mandate pseudonymous data, and it is not the same as anonymity,`
  Replace with: `The code does not mandate pseudonymous data, and pseudonymous data is not the same as anonymity,`

- [ ] **54. 11, what the check cannot do.**
  Find: `cannot distinguish between possibly correct sentences and sensible sentences,`
  Replace with: `cannot tell whether a sentence that looks right actually makes sense,`

- [ ] **55. 12.1, the first sentence.**
  Find: `The prototype is tested with the generated data of CERT-layout.`
  Replace with: `The prototype works from start to finish with the generated data of CERT-layout.`

- [ ] **56. 12.2, neither fix is done.**
  Find: `Both are not in place at this time.`
  Replace with: `Neither is in place at this time.`

- [ ] **57. 12.2, Issue 14 today.**
  Find: `The baseline loop will score a session and immediately append the total of the session to the user's baseline, allowing a user to be scored against a baseline that contains the total of another session at the same time they are scoring the session.`
  Replace with: `The baseline loop scores a session and immediately appends the total of the session to the user's baseline, allowing a user's session to be compared with a baseline that already contains the total of another session running at the same time.`

- [ ] **58. 13, gap G1.**
  Find: `The gaps identified in the literature review are covered by G1 (alerts are not explained to the analyst) which is addressed with the SHAP and baseline reasons in plain words, but have not been tested`
  Replace with: `Of the gaps identified in the literature review, G1 (alerts are not explained to the analyst) is addressed with the SHAP and baseline reasons in plain words, but these have not been tested`

- [ ] **59. 13, gap G2.**
  Find: `cover most of the requirements for G2`
  Replace with: `cover most of G2`

- [ ] **60. 3, the evaluation and the assistant.**
  Find: `when assessed in a clear and orderly manner in which the assistant is explicitly limited in what she can say.`
  Replace with: `when assessed in a clear, time-ordered manner in which the assistant is explicitly limited in what it can say.`

- [ ] **61. 3, publication years.**
  Find: `20 studies were retained between the years 2021 and 2026,`
  Replace with: `20 studies published between the years 2021 and 2026 were retained,`

Not checked: your AI detector's score (re-run it after fixing) and the real Word page layout.
