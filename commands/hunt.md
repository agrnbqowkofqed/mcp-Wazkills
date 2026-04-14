Hunt for all activity related to the indicator: $ARGUMENTS

The indicator can be an IP address, hostname, username, file hash, or domain.

Steps:
1. Search IRIS globally with iris_global_search_ioc for the indicator across all cases.
2. Search IRIS notes globally with iris_global_search_notes for any mention of the indicator.
3. Search Graylog for the indicator as srcip and dstip over the last 14 days across all relevant streams. Use graylog_search with query `srcip:"<indicator>" OR dstip:"<indicator>"`.
4. If results found in Graylog, run graylog_terms to get top destination IPs and ports for that host.
5. Apply analyst mindset silently: check threat tier, look for patterns, identify if this is noise or signal.
6. Report:
   - IRIS cases referencing this indicator (case ID, name, status)
   - IRIS notes mentioning it
   - Graylog network activity (top destinations, ports, event count)
   - Risk assessment: Tier 1 (noise) / Tier 2 (watch) / Tier 3 (escalate)
   - Recommended next action
