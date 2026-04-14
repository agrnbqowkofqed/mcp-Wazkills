# mcp-Wazkills

MCP server for SOC BlueTeam analysts — wraps **DFIR-IRIS** and **Graylog** into a single FastMCP server with analyst-ready slash commands for alert triage, case analysis, and threat hunting.

Built for university SOC BlueTeam operations.

---

## What it does

Exposes two sets of tools through the [Model Context Protocol](https://modelcontextprotocol.io):

- **`iris_*`** — query and act on DFIR-IRIS cases, alerts, IOCs, assets, timeline, notes, and evidence
- **`graylog_*`** — search, aggregate, and analyse events from Graylog streams

Comes with Claude Code slash commands for common SOC workflows:

| Command | Description |
|---|---|
| `/treat <owner> <id_from> to <id_to>` | Treat and close a range of IRIS alerts in bulk |
| `/hunt <ip\|host\|hash>` | Cross-search an indicator across IRIS and Graylog |
| `/analyse-case <id>` | Full deep-dive on an IRIS case |
| `/triage-av` | Triage the weekly Kaspersky AV alert sheet |
| `/triage-network` | Triage the weekly Graylog network alert sheet |
| `/correlate-week` | Cross-correlate AV + network alerts, find escalation candidates |

---

## Requirements

- Python 3.10+
- Access to a DFIR-IRIS instance
- Access to a Graylog instance
- [Claude Code](https://claude.ai/code) CLI

---

## Installation

**1. Clone the repo**

```bash
git clone https://github.com/agrnbqowkofqed/mcp-Wazkills.git
cd mcp-Wazkills
```

**2. Run setup**

```bash
chmod +x setup.sh
./setup.sh
```

This creates a `.venv/` and installs all dependencies.

**3. Configure credentials**

IRIS — create `~/.config/claude-dfir-iris-plugin/config.json`:

```json
{
    "url": "https://your-iris-instance.com",
    "token": "YOUR_IRIS_API_KEY",
    "verify_ssl": true,
    "timeout": 120
}
```

Graylog — create `~/.config/claude-graylog-plugin/config.json`:

```json
{
    "url": "https://your-graylog-instance.com",
    "token": "YOUR_GRAYLOG_API_KEY"
}
```

> Config files must be `chmod 600` — world-readable files are rejected.

**4. Register the MCP server in Claude Code**

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "blueteam": {
      "command": "/path/to/mcp-Wazkills/.venv/bin/python3",
      "args": ["/path/to/mcp-Wazkills/server.py"]
    }
  }
}
```

**5. Install slash commands**

```bash
mkdir -p ~/.claude/commands
cp commands/*.md ~/.claude/commands/
```

Restart Claude Code — the tools and commands will be available immediately.

---

## Tools reference

### IRIS tools

| Tool | Description |
|---|---|
| `iris_test` | Test connectivity to DFIR-IRIS |
| `iris_list_cases` | List cases with filters (date, state, severity, customer) |
| `iris_get_case` | Full details for a single case |
| `iris_case_summary` | Case summary/description text |
| `iris_filter_alerts` | Filter alerts by title, source, severity, status, date |
| `iris_get_alert` | Full details for a single alert |
| `iris_list_assets` | List assets for a case |
| `iris_list_iocs` | List IOCs for a case |
| `iris_list_tasks` | List tasks for a case |
| `iris_list_timeline` | List timeline events for a case |
| `iris_list_notes` | List notes for a case |
| `iris_search_notes` | Search note content within a case |
| `iris_list_evidence` | List evidence for a case |
| `iris_global_search_ioc` | Search an IOC across ALL cases |
| `iris_global_search_notes` | Search note content across ALL cases |
| `iris_ref` | Get reference/lookup data (severities, statuses, users, etc.) |
| `iris_treat_alert` | Treat and close a single alert, assign owner |
| `iris_treat_alerts_range` | Treat and close a range of alerts in bulk |

### Graylog tools

| Tool | Description |
|---|---|
| `graylog_test` | Test connectivity to Graylog |
| `graylog_list_streams` | List available streams |
| `graylog_search` | Search events in a stream |
| `graylog_count` | Count events matching a query |
| `graylog_terms` | Top N unique values of a field (frequency analysis) |
| `graylog_stats` | Numeric stats for a field (min, max, mean, sum) |
| `graylog_histogram` | Event count over time |
| `graylog_multi_terms` | Multiple field aggregations in one call |
| `graylog_discover_fields` | Discover available fields by sampling events |

---

## Usage examples

**Treat alerts 1234 to 1239:**
```
/treat john doe 1234 to 1239
```

**Hunt for a suspicious IP:**
```
/hunt 192.168.1.100
```

**Deep-dive on case 42:**
```
/analyse-case 42
```

**Triage this week's AV alerts:**
```
/triage-av
```

---

## Dependencies

- [fastmcp](https://github.com/jlowin/fastmcp) >= 2.0
- [dfir-iris-client](https://github.com/dfir-iris/dfir-iris-client) >= 2.0
- requests
- openpyxl
- pyyaml
- python-dotenv

---

## Security notes

- Credentials are never stored in this repo — they live in `~/.config/` outside version control
- Config files with loose permissions (`chmod 077`) are rejected at startup
- HTTPS is enforced by default; plain HTTP requires explicit opt-in
