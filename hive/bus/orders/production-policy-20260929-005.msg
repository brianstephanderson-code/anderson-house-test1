MESSAGE_ID=production-policy-20260929-005
CHANNEL=ORDERS
FROM=MANAGEMENT
TO=AWS
TYPE=PRODUCTION_POLICY_PROFILE
PAYLOAD=Use one useful work queue. Free workers take the next suitable parcel. Retry only failed parcels. Avoid duplicate harmful work. After three failures, quarantine.
UTC=2026-09-29T14:24:00Z
