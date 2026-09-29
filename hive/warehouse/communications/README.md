# Completed communication warehouse

One manifest per closed MESSAGE_ID.

Path:
`hive/warehouse/communications/<MESSAGE_ID>.manifest`

A manifest records:
- original source message
- required successful return(s)
- correlation identity
- CLOSED status
- closure time

The matching active-loop retirement receipt is:
`hive/bus/closed/<MESSAGE_ID>.closed`

The bus keeps evidence; the CLOSED receipt retires the loop.
