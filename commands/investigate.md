Investigate an IP address using the MCP tools. Arguments: $ARGUMENTS

Expected format: `<ip> [last <N> days]`
Examples:
  `/investigate 192.168.1.100`
  `/investigate 192.168.1.100 last 7 days`

Default time window: last 14 days if not specified.

Steps — call all tools, then report:

1. Parse the IP and time window. Convert to UTC ISO 8601 from_ts and to_ts.

2. Run these MCP tool calls in parallel:
   - graylog_count  stream="firewall"  query=`srcip:"<ip>"`  → outbound event count
   - graylog_count  stream="firewall"  query=`dstip:"<ip>"`  → inbound event count
   - iris_global_search_ioc  search_term="<ip>"              → existing IRIS cases

3. Run these in parallel:
   - graylog_multi_terms  stream="firewall"  query=`srcip:"<ip>"`
       aggregations: dstip (top 20), dport (top 20), action (top 10), srcuser (top 10)
   - graylog_multi_terms  stream="firewall"  query=`dstip:"<ip>"`
       aggregations: srcip (top 20), action (top 10)
   - graylog_histogram  stream="firewall"  query=`srcip:"<ip>"`  interval="1h"

4. graylog_search  stream="firewall"  query=`srcip:"<ip>" OR dstip:"<ip>"`
   fields=["timestamp","srcip","dstip","dport","action","srcuser","srcip_rede"]
   limit=10  sort="timestamp:desc"
   → most recent raw events

5. Apply analyst mindset silently to all results:
   - Ports 3333/4444/5555/14444 → crypto mining C2
   - High repetitive count to single external IP → C2 beaconing
   - Mostly blocked actions → firewall stopping it, check if persistent
   - Many inbound sources → may be a server or targeted host
   - Identify network segment from srcip_rede field

6. Report:

   **IP:** `<ip>` | **Period:** from → to | **Network:** <campus network>

   **Outbound** (as source) — N total events
   | Destination IP | Count |
   | Top Port | Count |
   | Action | Count |
   | User | Count |

   **Inbound** (as destination) — N total events
   | Source IP | Count |
   | Action | Count |

   **Activity over time** — summarise histogram (peak hours, sustained vs spike)

   **Recent events** — last 10 raw events table

   **IRIS** — list any cases referencing this IP

   **Assessment**
   - Risk tier: Tier 1 / Tier 2 / Tier 3
   - Behaviour: what this IP appears to be doing
   - Recommended action
