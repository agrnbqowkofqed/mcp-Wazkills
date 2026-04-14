Treat and close a range of IRIS alerts. Arguments: $ARGUMENTS

Expected format: `<owner full name> <alert_id_from> to <alert_id_to>`
Example: `/treat john doe 1234 to 1239`

Steps:
1. Parse the arguments: everything before the first number is the owner name, the two numbers around "to" are the alert ID range.
2. Fetch the first and last alert with iris_get_alert to confirm both exist and show a brief summary (title, source, current status).
3. Ask for a short treatment note if one was not provided — one sentence describing the action taken (e.g. "KMSAuto detected and blocked, low risk pirated activator").
4. Call iris_treat_alerts_range with alert_id_from, alert_id_to, owner_name, note, and status="closed".
5. Report results: how many alerts were closed successfully, and list any that failed with the reason.
