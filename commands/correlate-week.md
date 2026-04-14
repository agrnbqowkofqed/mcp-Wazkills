Cross-correlate AV and network alerts from the weekly spreadsheet to find escalation candidates.

Steps:
1. Read both sheets from ~/Downloads/BlueTeam.zip:
   - Sheet 1 (AV): extract dst_host and srcuser columns
   - Sheet 2 (Network): extract srcip and srcuser columns
   Use the same python3 one-liner pattern as /triage-av and /triage-network.
2. Find hosts/users that appear in BOTH sheets — these are the highest priority escalation candidates.
3. For each overlapping host/user:
   a. Retrieve all their AV alerts (threat names, dates)
   b. Retrieve all their network alerts (dstip, dport, count)
   c. Check IRIS with iris_global_search_ioc — is there already an open case?
4. Apply escalation logic silently:
   - AV Tier 3 + any network alert → immediate escalation
   - AV Tier 2 + mining/C2 ports in network sheet → escalate
   - AV Tier 1 + network alert → watch, no case needed unless repeated
5. Report:
   - **Overlapping hosts** table: host | AV threats | network activity | existing IRIS case | action
   - **Escalation candidates**: hosts requiring an IRIS case to be opened or updated
   - **Clean hosts**: hosts in only one sheet with no escalation needed
