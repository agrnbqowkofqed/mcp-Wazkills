"""
blueteam MCP server — DFIR-IRIS + Graylog tools for SOC BlueTeam analysts.

Exposes:
  iris_*     — DFIR-IRIS queries and actions (cases, alerts, IOCs, assets, …)
  graylog_*  — Graylog search and aggregation

Credentials are read from the existing plugin config files:
  ~/.config/claude-dfir-iris-plugin/config.json
  ~/.config/claude-graylog-plugin/config.json
"""

import importlib.util
import logging
import os
import sys
from typing import Optional

from fastmcp import FastMCP

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("blueteam")

# ── Load existing lib modules without sys.path collision ──────────────────────

def _load(name: str, path: str):
    """Load a .py file as a module without touching sys.path."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # register so relative imports inside the module work
    spec.loader.exec_module(mod)
    return mod

_IRIS_LIB = os.path.expanduser("~/claude-dfir-iris-plugin/lib/reader.py")
_GRAYLOG_LIB = os.path.expanduser("~/claude-graylog-plugin/lib/client.py")

_iris = _load("iris_reader", _IRIS_LIB)
_graylog = _load("graylog_client", _GRAYLOG_LIB)

init_reader = _iris.init_reader
init_client = _graylog.init_client
resolve_stream = _graylog.resolve_stream

# ── Lazy-init singletons ──────────────────────────────────────────────────────

_reader = None
_client = None


def get_reader():
    global _reader
    if _reader is None:
        _reader = init_reader()
    return _reader


def get_client():
    global _client
    if _client is None:
        _client = init_client()
    return _client


# ── MCP server ────────────────────────────────────────────────────────────────

mcp = FastMCP("blueteam")


# ═══════════════════════════════════════════════════════════
# IRIS tools
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def iris_test() -> dict:
    """Test connectivity to DFIR-IRIS. Returns {"ok": true} on success."""
    ok = get_reader().test_connection()
    return {"ok": ok}


@mcp.tool()
def iris_list_cases(
    per_page: int = 15,
    page: Optional[int] = None,
    sort_dir: str = "desc",
    start_open_date: Optional[str] = None,
    end_open_date: Optional[str] = None,
    case_customer_id: Optional[int] = None,
    case_state_id: Optional[int] = None,
    case_severity_id: Optional[int] = None,
    case_name: Optional[str] = None,
) -> dict:
    """List DFIR-IRIS cases with optional filters.

    Args:
        per_page: Results per page (default 15).
        page: Explicit page number. Omit to get newest (desc) or oldest (asc) page automatically.
        sort_dir: "desc" = newest first (default), "asc" = oldest first.
        start_open_date: Cases opened on/after this date, format YYYY-MM-DD.
        end_open_date: Cases opened on/before this date, format YYYY-MM-DD.
        case_customer_id: Filter by customer/tenant ID.
        case_state_id: Filter by state (3=Open, 9=Closed). Use iris_ref("case-states") for full list.
        case_severity_id: 1=Unspecified, 2=Info, 3=Low, 4=Medium, 5=High, 6=Critical.
        case_name: Filter by case name substring.
    """
    return get_reader().list_cases(
        per_page=per_page,
        page=page,
        sort_dir=sort_dir,
        start_open_date=start_open_date,
        end_open_date=end_open_date,
        case_customer_id=case_customer_id,
        case_state_id=case_state_id,
        case_severity_id=case_severity_id,
        case_name=case_name,
    )


@mcp.tool()
def iris_get_case(case_id: int) -> dict:
    """Get full details for a single DFIR-IRIS case."""
    return get_reader().get_case(case_id)


@mcp.tool()
def iris_case_summary(case_id: int) -> dict:
    """Get the summary/description text of a case."""
    return get_reader().case_summary(case_id)


@mcp.tool()
def iris_filter_alerts(
    per_page: int = 15,
    page: int = 1,
    alert_title: Optional[str] = None,
    alert_source: Optional[str] = None,
    alert_severity_id: Optional[int] = None,
    alert_status_id: Optional[int] = None,
    alert_start_date: Optional[str] = None,
    alert_end_date: Optional[str] = None,
    case_id: Optional[int] = None,
    sort: str = "desc",
) -> dict:
    """Filter DFIR-IRIS alerts.

    Args:
        per_page: Results per page (default 15).
        page: Page number (default 1).
        alert_title: Filter by title substring.
        alert_source: Filter by source name.
        alert_severity_id: 1=Unspecified, 2=Info, 3=Low, 4=Medium, 5=High, 6=Critical.
        alert_status_id: Use iris_ref("alert-statuses") to get available status IDs.
        alert_start_date: Alerts created on/after this date, format YYYY-MM-DD.
        alert_end_date: Alerts created on/before this date, format YYYY-MM-DD.
        case_id: Only alerts linked to this case.
        sort: "desc" = newest first (default), "asc" = oldest first.
    """
    return get_reader().filter_alerts(
        per_page=per_page,
        page=page,
        alert_title=alert_title,
        alert_source=alert_source,
        alert_severity_id=alert_severity_id,
        alert_status_id=alert_status_id,
        alert_start_date=alert_start_date,
        alert_end_date=alert_end_date,
        case_id=case_id,
        sort=sort,
    )


@mcp.tool()
def iris_get_alert(alert_id: int) -> dict:
    """Get full details for a single IRIS alert."""
    return get_reader().get_alert(alert_id)


@mcp.tool()
def iris_list_assets(case_id: int) -> dict:
    """List all assets for a case."""
    return get_reader().list_assets(case_id)


@mcp.tool()
def iris_list_iocs(case_id: int) -> dict:
    """List all IOCs (Indicators of Compromise) for a case."""
    return get_reader().list_iocs(case_id)


@mcp.tool()
def iris_list_tasks(case_id: int) -> dict:
    """List all tasks for a case."""
    return get_reader().list_tasks(case_id)


@mcp.tool()
def iris_list_timeline(case_id: int) -> dict:
    """List timeline events for a case."""
    return get_reader().list_timeline(case_id)


@mcp.tool()
def iris_list_notes(case_id: int) -> dict:
    """List note directories (and their notes) for a case."""
    return get_reader().list_notes(case_id)


@mcp.tool()
def iris_search_notes(search_term: str, case_id: int) -> dict:
    """Search note content within a specific case.

    Args:
        search_term: Text to search for in notes.
        case_id: Case to search within.
    """
    return get_reader().search_notes(search_term, case_id)


@mcp.tool()
def iris_list_evidence(case_id: int) -> dict:
    """List all evidence items for a case."""
    return get_reader().list_evidence(case_id)


@mcp.tool()
def iris_global_search_ioc(search_term: str) -> dict:
    """Search for an IOC value (IP, hash, domain…) across ALL cases."""
    return get_reader().global_search_ioc(search_term)


@mcp.tool()
def iris_global_search_notes(search_term: str) -> dict:
    """Search note content across ALL cases."""
    return get_reader().global_search_notes(search_term)


@mcp.tool()
def iris_ref(ref_type: str) -> list:
    """Get IRIS reference/lookup data.

    Args:
        ref_type: One of:
            severities, classifications, case-states, customers, users,
            asset-types, ioc-types, alert-statuses, task-statuses,
            tlps, analysis-statuses, event-categories, compromise-statuses
    """
    r = get_reader()
    dispatch = {
        "severities":          r.list_severities,
        "classifications":     r.list_classifications,
        "case-states":         r.list_case_states,
        "customers":           r.list_customers,
        "users":               r.list_users,
        "asset-types":         r.list_asset_types,
        "ioc-types":           r.list_ioc_types,
        "alert-statuses":      r.list_alert_statuses,
        "task-statuses":       r.list_task_statuses,
        "tlps":                r.list_tlps,
        "analysis-statuses":   r.list_analysis_statuses,
        "event-categories":    r.list_event_categories,
        "compromise-statuses": r.list_compromise_statuses,
    }
    fn = dispatch.get(ref_type)
    if fn is None:
        valid = ", ".join(sorted(dispatch.keys()))
        raise ValueError(f"Unknown ref_type '{ref_type}'. Valid values: {valid}")
    return fn()


# ═══════════════════════════════════════════════════════════
# IRIS write tools
# ═══════════════════════════════════════════════════════════

def _get_alert_writer():
    """Return a write-capable Alert instance using the existing reader session."""
    from dfir_iris_client.alert import Alert
    return Alert(session=get_reader()._session)


def _unwrap_write(resp):
    """Unwrap an ApiResponse from a write call."""
    if resp.is_error():
        msg = resp.get_msg() or "Unknown IRIS API error"
        uri = resp.get_uri() or ""
        raise RuntimeError(f"IRIS API error: {msg} (endpoint: {uri})")
    return resp.get_data()


def _resolve_owner_and_status(reader, owner_name: str, status: str):
    """Resolve owner name → user_id and status name → status_id."""
    users = reader.list_users()
    owner_name_lower = owner_name.strip().lower()
    matched = [u for u in users if owner_name_lower in u.get("user_name", "").lower()
               or owner_name_lower in u.get("user_login", "").lower()]
    if not matched:
        raise ValueError(
            f"No user found matching '{owner_name}'. "
            f"Available: {[u.get('user_name') for u in users]}"
        )
    owner_id = matched[0]["user_id"]

    statuses = reader.list_alert_statuses()
    status_lower = status.strip().lower()
    matched_status = [s for s in statuses if status_lower in s.get("status_name", "").lower()]
    if not matched_status:
        raise ValueError(
            f"No alert status matching '{status}'. "
            f"Available: {[s.get('status_name') for s in statuses]}"
        )
    status_id = matched_status[0]["status_id"]
    return owner_id, status_id


@mcp.tool()
def iris_treat_alert(
    alert_id: int,
    owner_name: str,
    note: str,
    status: str = "closed",
) -> dict:
    """Treat and close a single IRIS alert — assign owner, set note, update status.

    Args:
        alert_id: ID of the alert to treat.
        owner_name: Full name of the analyst treating the alert (used to resolve user ID).
        note: Treatment note explaining the action taken and resolution.
        status: Target status name (default "closed"). Use iris_ref("alert-statuses") to see options.

    Returns:
        Updated alert data from IRIS.
    """
    reader = get_reader()
    owner_id, status_id = _resolve_owner_and_status(reader, owner_name, status)

    full_note = f"{note}\n\nResponsável: {owner_name}"
    alert_data = {
        "alert_status_id": status_id,
        "alert_owner_id": owner_id,
        "alert_note": full_note,
    }

    writer = _get_alert_writer()
    resp = writer.update_alert(alert_id, alert_data)
    return _unwrap_write(resp)


@mcp.tool()
def iris_treat_alerts_range(
    alert_id_from: int,
    alert_id_to: int,
    owner_name: str,
    note: str,
    status: str = "closed",
) -> dict:
    """Treat and close a range of IRIS alerts in bulk.

    Args:
        alert_id_from: First alert ID in the range (inclusive).
        alert_id_to: Last alert ID in the range (inclusive).
        owner_name: Full name of the analyst treating the alerts (used to resolve user ID).
        note: Treatment note applied to all alerts in the range.
        status: Target status name (default "closed"). Use iris_ref("alert-statuses") to see options.

    Returns:
        {"ok": [alert_ids], "failed": {alert_id: error_message}}
    """
    reader = get_reader()
    owner_id, status_id = _resolve_owner_and_status(reader, owner_name, status)

    full_note = f"{note}\n\nResponsável: {owner_name}"
    alert_data = {
        "alert_status_id": status_id,
        "alert_owner_id": owner_id,
        "alert_note": full_note,
    }

    writer = _get_alert_writer()
    ok = []
    failed = {}
    for alert_id in range(alert_id_from, alert_id_to + 1):
        try:
            resp = writer.update_alert(alert_id, alert_data)
            _unwrap_write(resp)
            ok.append(alert_id)
        except Exception as e:
            failed[alert_id] = str(e)

    return {"ok": ok, "failed": failed}


# ═══════════════════════════════════════════════════════════
# Graylog tools
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def graylog_test() -> dict:
    """Test connectivity to Graylog. Returns server version on success."""
    client = get_client()
    ok = client.test_connection()
    result: dict = {"ok": ok}
    if ok and hasattr(client, "server_version"):
        result["version"] = client.server_version
    return result


@mcp.tool()
def graylog_list_streams() -> list:
    """List all available Graylog streams (id, title, description)."""
    return get_client().list_streams()


@mcp.tool()
def graylog_search(
    stream: str,
    query: str,
    from_ts: str,
    to_ts: str,
    fields: Optional[list] = None,
    limit: int = 100,
    sort: str = "timestamp:desc",
) -> list:
    """Search events in a Graylog stream.

    Args:
        stream: Stream name (partial match OK, e.g. "firewall") or exact stream ID.
        query: Elasticsearch query string, e.g. "srcip:10.0.0.1 AND event:blocked" or "*".
        from_ts: Start time, UTC ISO 8601, e.g. "2026-04-01T00:00:00.000Z".
        to_ts: End time, UTC ISO 8601, e.g. "2026-04-13T23:59:59.000Z".
        fields: Fields to return, e.g. ["timestamp", "srcip", "dstip", "event"]. Omit for all.
        limit: Max events (default 100).
        sort: Sort field:direction, default "timestamp:desc" (newest first).

    Returns:
        List of event dicts.
    """
    client = get_client()
    stream_id, _ = resolve_stream(client, stream)
    return client.search(query, from_ts, to_ts, stream_id,
                         fields=fields, limit=limit, sort=sort)


@mcp.tool()
def graylog_count(
    stream: str,
    query: str,
    from_ts: str,
    to_ts: str,
) -> int:
    """Count events matching a query in a Graylog stream.

    Args:
        stream: Stream name or ID.
        query: Elasticsearch query string.
        from_ts: Start time UTC ISO 8601.
        to_ts: End time UTC ISO 8601.

    Returns:
        Total event count.
    """
    client = get_client()
    stream_id, _ = resolve_stream(client, stream)
    return client.count(query, from_ts, to_ts, stream_id)


@mcp.tool()
def graylog_terms(
    stream: str,
    query: str,
    from_ts: str,
    to_ts: str,
    field: str,
    size: int = 50,
) -> dict:
    """Top N unique values of a field with their event counts (frequency analysis).

    Args:
        stream: Stream name or ID.
        query: Filter query, e.g. "program:suricata" or "*".
        from_ts: Start time UTC ISO 8601.
        to_ts: End time UTC ISO 8601.
        field: Field to aggregate, e.g. "srcip", "event", "dstport", "alert_signature".
        size: Number of top values to return (default 50).

    Returns:
        {value: count} sorted by count descending.
    """
    client = get_client()
    stream_id, _ = resolve_stream(client, stream)
    return client.terms(query, from_ts, to_ts, field, stream_id, size=size)


@mcp.tool()
def graylog_stats(
    stream: str,
    query: str,
    from_ts: str,
    to_ts: str,
    field: str,
) -> dict:
    """Numeric stats (count, min, max, mean, sum) for a numeric field.

    Args:
        stream: Stream name or ID.
        query: Filter query.
        from_ts: Start time UTC ISO 8601.
        to_ts: End time UTC ISO 8601.
        field: Numeric field to compute stats on.
    """
    client = get_client()
    stream_id, _ = resolve_stream(client, stream)
    return client.stats(query, from_ts, to_ts, field, stream_id)


@mcp.tool()
def graylog_histogram(
    stream: str,
    query: str,
    from_ts: str,
    to_ts: str,
    interval: str = "1h",
) -> dict:
    """Temporal histogram of event counts over a time range.

    Args:
        stream: Stream name or ID.
        query: Filter query.
        from_ts: Start time UTC ISO 8601.
        to_ts: End time UTC ISO 8601.
        interval: Bucket size: "1h", "1d", "30m", "15m", etc. or "auto".

    Returns:
        {"results": {timestamp: count}}
    """
    client = get_client()
    stream_id, _ = resolve_stream(client, stream)
    return client.histogram(query, from_ts, to_ts, stream_id, interval=interval)


@mcp.tool()
def graylog_multi_terms(
    stream: str,
    query: str,
    from_ts: str,
    to_ts: str,
    aggregations: list,
) -> dict:
    """Run multiple field frequency analyses in a single API call.

    Args:
        stream: Stream name or ID.
        query: Filter query.
        from_ts: Start time UTC ISO 8601.
        to_ts: End time UTC ISO 8601.
        aggregations: List of aggregation specs, each a dict with:
            - id (str): Unique identifier for this aggregation in the result.
            - field (str): Field to aggregate.
            - size (int, optional): Top N values, default 50.
          Example: [{"id": "events", "field": "event", "size": 20},
                    {"id": "sources", "field": "srcip", "size": 10}]

    Returns:
        {id: {value: count}} for each aggregation, sorted by count.
    """
    client = get_client()
    stream_id, _ = resolve_stream(client, stream)
    field_sizes = {
        agg["id"]: (agg["field"], agg.get("size", 50))
        for agg in aggregations
    }
    return client.multi_terms(query, from_ts, to_ts, stream_id, field_sizes)


@mcp.tool()
def graylog_discover_fields(
    stream: str,
    query: str,
    from_ts: str,
    to_ts: str,
    sample_size: int = 20,
) -> dict:
    """Discover available fields in a stream by sampling events.

    Useful before building queries to know which fields exist.

    Args:
        stream: Stream name or ID.
        query: Filter query (use "*" to sample all events).
        from_ts: Start time UTC ISO 8601.
        to_ts: End time UTC ISO 8601.
        sample_size: Number of events to sample (default 20).

    Returns:
        {field_name: python_type} for all discovered fields.
    """
    client = get_client()
    stream_id, _ = resolve_stream(client, stream)
    return client.discover_fields(query, from_ts, to_ts, stream_id, sample_size=sample_size)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
