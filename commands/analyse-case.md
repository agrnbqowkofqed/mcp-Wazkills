Deep-dive analysis of IRIS case: $ARGUMENTS

Steps:
1. Fetch full case details with iris_get_case and iris_case_summary.
2. In parallel, fetch: iris_list_assets, iris_list_iocs, iris_list_tasks, iris_list_timeline, iris_list_notes, iris_list_evidence.
3. For each IOC found, run iris_global_search_ioc to check if it appears in other cases — flag cross-case links.
4. Apply analyst mindset silently: check for patterns, assess severity, identify gaps in investigation.
5. Report in this structure:
   - **Case overview**: ID, title, status, severity, owner, opened date
   - **Summary**: what happened (from case summary + timeline)
   - **Affected assets**: list with type and compromise status
   - **IOCs**: list with type, value, TLP — flag any that appear in other cases
   - **Timeline**: key events in chronological order
   - **Open tasks**: what is still pending
   - **Gaps**: what is missing or unclear in the investigation
   - **Recommended next steps**: concrete actions to advance or close the case
