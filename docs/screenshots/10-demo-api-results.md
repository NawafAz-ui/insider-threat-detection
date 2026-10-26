# Insider Threat Detection --- API Demo Results

**Command**

``` powershell
python scripts\demo_api.py --user alice --password $pw
```

**Result:** Completed successfully. All 13 API tests returned the
expected HTTP status codes.

## Test results

    \# Test                                             Expected   Actual Result
  ---- ---------------------------------------------- ---------- -------- --------
     1 Login with a wrong password                           401      401 PASS
     2 Session list without a token                          401      401 PASS
     3 Login with an injection attempt                       422      422 PASS
     4 Login with the correct password                       200      200 PASS
     5 List flagged sessions, highest risk first             200      200 PASS
     6 View session details for `S0003029`                   200      200 PASS
     7 View user history for `U0027`                         200      200 PASS
     8 View latest batch run                                 200      200 PASS
     9 Ask the assistant about a session                     200      200 PASS
    10 Invalid user ID format                                422      422 PASS
    11 Invalid session ID format                             422      422 PASS
    12 Request a session that does not exist                 404      404 PASS
    13 Submit a question longer than 300 characters          422      422 PASS

## Key results

-   Database connection check: passed.
-   Sessions stored: **7,329**.
-   Flagged sessions: **66**.
-   Risk threshold: **19.3**.
-   Highest-risk example: session `S0003029`, with a risk score of
    **100.0**.
-   The assistant returned an explanation based on stored evidence using
    template mode; no language model was used for this response.
-   The demo finished with:
    `Done. Check the access_log collection for the login, view and question entries.`

## Security checks demonstrated

-   Invalid credentials are rejected with HTTP `401`.
-   Requests without authentication are rejected with HTTP `401`.
-   Injection-shaped input and malformed identifiers are rejected with
    HTTP `422`.
-   Requests for nonexistent sessions return HTTP `404`.
-   Overlong questions are rejected with HTTP `422`.

## Screenshot evidence

Save the terminal screenshots in `docs/screenshots/`:

-   `01-connection-check.png` --- successful database, API, and
    dashboard connection checks.
-   `10-demo-api-part1.png` --- API demo calls 1--6.
-   `10-demo-api-part2.png` --- API demo calls 7--13.
