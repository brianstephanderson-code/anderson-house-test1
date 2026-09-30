MESSAGE_ID=SH-001-01-PROBE-20260930
CHANNEL=ORDERS
FROM=TOMO-COORDINATOR
TO=SEARCH-WORKER
TYPE=SEARCH_RESEARCH_PROBE
PAYLOAD={"batch_id":"sleepy-hollow-research-001","job_id":"SH-001-01","correlation_id":"sleepy-hollow-research-001:SH-001-01","function_class":"named_reference","term":"CASTLE OF INDOLENCE","local_context":"The opening epigraph ends with CASTLE OF INDOLENCE.","question":"Identify the quoted work/author and explain what the epigraph is doing here.","search_doors":["local-context","bibliographic-source","literary-reference","annotated-edition"],"purpose":"PROBE backlog-to-live-bus admission joint. Preserve ACK, UPLINK, verification and warehouse closure evidence. If unsupported by this worker, return BLOCKED with exact missing function; do not fabricate a result."}
