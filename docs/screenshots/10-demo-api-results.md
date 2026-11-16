# API demo results

Real output of `python scripts/demo_api.py --user alice --password ********` on a copy of the main database (SPEDIA), 16 November 2026.

```
1. Login with a wrong password (expect 401)
   -> HTTP 401
   {
  "detail": "Wrong username or password"
}

2. Session list without a token (expect 401)
   -> HTTP 401
   {
  "detail": "Login required"
}

3. Login with an injection attempt (expect 422)
   -> HTTP 422
   {
  "detail": [
    {
      "type": "string_type",
      "loc": [
        "body",
        "username"
      ],
      "msg": "Input should be a valid string",
      "input": {
        "$ne": ""
      }
    },
    {
      "type": "string_type",
      "loc": [
        "body",
        "password"
      ],
      "msg": "Input should be a valid string",
      "input": {
        "$ne": ""
      }
    }
  ]
}

4. Login with the right password (expect 200 and a token)
   -> HTTP 200
   {
  "username": "alice",
  "expires_minutes": 30
}

5. Flagged sessions, highest risk first (limit 3)
   -> HTTP 200
   {
  "threshold": 35.5,
  "total": 111,
  "scored": 246,
  "high": 101,
  "sessions": [
    {
      "session_id": "S0000130",
      "user": "irene",
      "pc": "public-host_3e100f80a765d58cccb17ac23f57d42d14742813",
      "start": "2025-03-23T20:19:18",
      "end": "2025-03-24T08:19:18",
      "risk_score": 95.8
    },
    {
      "session_id": "S0000222",
      "user": "irene",
      "pc": "public-host_ebae3dba5531378dd1976b870f2462ea37133233",
      "start": "2025-03-30T08:56:42",
      "end": "2025-03-30T14:07:06",
      "risk_score": 95.3
    },
    {
      "session_id": "S0000223",
      "user": "irene",
      "pc": "public-host_2afe5f272bfdd1eedec37b148a1b8fe62b160e75",
      "start":

6. Session detail for S0000130
   -> HTTP 200
   {
  "session_id": "S0000130",
  "risk_score": 95.8,
  "threshold": 35.5,
  "model_scores": {
    "lr": 0.9873,
    "xgb": 0.9755,
    "iforest": 0.8797
  },
  "top_shap": [
    {
      "feature": "events_per_hour",
      "value": 212.583,
      "shap": 4.6227,
      "strength": "strong",
      "text": "Activity rate was 212.6 events per hour."
    },
    {
      "feature": "logon_hour",
      "value": 20.317,
      "shap": 0.516,
      "strength": "minor",
      "text": "Logged on at 20.3h (usual 11.7h)."
    },
    {
      "feature": "n_distinct_pcs_day",
      "value": 4.0,
      "shap": 0.381,
      "strength": "minor",
      "text": "Used 4 different PCs that day, up to this session."
  

7. User history for irene (workflow 2)
   -> HTTP 200
   {
  "user": "irene",
  "summary": {
    "sessions": 97,
    "flagged": 39,
    "highest_risk": 95.8,
    "shown": 97
  },
  "baseline": [
    {
      "metric": "logon_hour",
      "label": "Usual logon hour",
      "mean": 12.45,
      "std": 5.01
    },
    {
      "metric": "duration_min",
      "label": "Usual session length (minutes)",
      "mean": 181.93,
      "std": 165.45
    },
    {
      "metric": "n_device_connect",
      "label": "Removable devices per session",
      "mean": 12.91,
      "std": 35.68
    },
    {
      "metric": "n_distinct_urls",
      "label": "Web pages per session",
      "mean": 59.71,
      "std": 89.79
    },
    {
      "metric": "n_file_events",
     

8. Latest batch run
   -> HTTP 200
   {
  "at": "2026-11-16T14:10:42.805003+00:00",
  "seconds": 0.4,
  "sessions": 246,
  "flagged": 111,
  "threshold": 35.5,
  "weights": {
    "lr": 0.38937023226627665,
    "xgb": 0.38456915939242076,
    "iforest": 0.22606060834130257
  }
}

9. Ask the assistant
   -> HTTP 200
   {
  "answer": "The session scored 96 out of 100, which is above the flag threshold. Main reasons: Activity rate was 212.6 events per hour. Compared with this user's normal: Connected 102 removable device(s) (usual 3.2), which is 10 or more standard deviations above this user's normal. (Offline summary of the stored evidence; no language model was used.)",
  "fields_used": [
    "R",
    "B1",
    "S1"
  ],
  "mode": "template"
}

10. User id with a bad format (expect 422)
   -> HTTP 422
   {
  "detail": "Invalid user id"
}

11. Session id with a bad format (expect 422)
   -> HTTP 422
   {
  "detail": "Invalid session id"
}

12. Session that does not exist (expect 404)
   -> HTTP 404
   {
  "detail": "Session not found"
}

13. Question over 300 characters (expect 422)
   -> HTTP 422
   {
  "detail": [
    {
      "type": "string_too_long",
      "loc": [
        "body",
        "question"
      ],
      "msg": "String should have at most 300 characters",
      "input": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "ctx": {
        "max_length": 300
      }
    }
  ]
}

Done. Check the access_log collection for the login, view and question entries.
```
