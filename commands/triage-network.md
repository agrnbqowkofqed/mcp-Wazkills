Triage the network alerts from the weekly BlueTeam spreadsheet (Graylog/Firewall sheet).

Steps:
1. Extract and read the network sheet (Sheet 2) from ~/Downloads/BlueTeam.zip using:
   `python3 -c "import zipfile, openpyxl, json; z=zipfile.ZipFile('Downloads/BlueTeam.zip'); wb=openpyxl.load_workbook(z.open([n for n in z.namelist() if n.endswith('.xlsx')][0])); ws=wb.worksheets[1]; rows=[{ws.cell(1,c).value: ws.cell(r,c).value for c in range(1,ws.max_column+1)} for r in range(2,ws.max_row+1) if any(ws.cell(r,c).value for c in range(1,ws.max_column+1))]; print(json.dumps(rows, default=str))"`
2. For each unique srcip, check IRIS with iris_global_search_ioc to see if it appears in any case.
3. Apply analyst mindset silently:
   - Ports 3333/4444/5555/14444 → likely mining traffic, check for XMRig rule 85886
   - Multiple srcips on same subnet with same dstip → network-level incident
   - High count() on a single src→dst pair → sustained connection, investigate
4. Detect patterns: subnet clusters, repeated dstip across multiple sources, high-frequency single IPs.
5. Output triage table: srcip | network | dstip | dport | count | risk | reason | in IRIS?
6. After the table, list subnet clusters and escalation candidates separately.
