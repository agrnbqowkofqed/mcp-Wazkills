Triage the AV alerts from the weekly BlueTeam spreadsheet.

Steps:
1. Extract and read the AV sheet (Sheet 1 — "Kaspersky" or first sheet) from the weekly spreadsheet at ~/Downloads/BlueTeam.zip using:
   `python3 -c "import zipfile, openpyxl, json; z=zipfile.ZipFile('Downloads/BlueTeam.zip'); wb=openpyxl.load_workbook(z.open([n for n in z.namelist() if n.endswith('.xlsx')][0])); ws=wb.worksheets[0]; rows=[{ws.cell(1,c).value: ws.cell(r,c).value for c in range(1,ws.max_column+1)} for r in range(2,ws.max_row+1) if any(ws.cell(r,c).value for c in range(1,ws.max_column+1))]; print(json.dumps(rows, default=str))"`
2. Apply analyst mindset triage silently to each alert:
   - Tier 1 (noise): KMS tools, AdWare → fast classify
   - Tier 2 (watch): Stealers, Droppers, Script.Miner, Strelec ISO → investigate
   - Tier 3 (escalate): PWDump, confirmed stealers with network activity → open/update IRIS case
3. Detect patterns: same threat on 3+ hosts, same user on multiple alerts, same subnet cluster.
4. For Tier 2+ alerts, check IRIS with iris_global_search_ioc for the host or threat hash.
5. Output a triage table with columns: host | user | threat | tier | suggested status | reason | escalate?
6. After the table, list any detected patterns and escalation flags separately.
