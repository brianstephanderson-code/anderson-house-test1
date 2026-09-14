# Anderson House — Communication Parcel 002

Parcel ID: AH-COMMS-002
Created: 2026-09-14

## ROUTING SLIP
FROM: Moto G / Controller
FROM DONE: Communication test parcel prepared
TO: S20 / Worker
TO STATE: Communication test parcel received and ready

## AIKIDO PRE-CHECK
- Parcel ID must be AH-COMMS-002.
- Destination must be S20 / Worker.
- This instruction section must be present.

## TRANSFORM
S20 receives this parcel and creates `AH-RECEIPT-002.txt` containing:

Parcel ID: AH-COMMS-002
DELIVERY VERIFIED

## AIKIDO RECEIPT CHECK
Delivery is not DONE merely because the parcel was sent.
Confirm that the S20 received the correct parcel and that the required contents are intact.

## DANNY DONE
The communication handoff is DONE when S20 proves receipt by producing `AH-RECEIPT-002.txt` with the correct Parcel ID and `DELIVERY VERIFIED`.
