# Vision Band — Phone Bridge Gate

The live Termux worker is NOT modified yet.

Reason:
The Vision Band interface must first pass its standalone endpoint replay. Only after that replay is GREEN should the live device-agent/Termux worker receive new vision actions.

Current safe path:
1. simulator + client exist,
2. automated endpoint replay exists,
3. allowlisted replay shell exists,
4. run/review replay,
5. only then add live worker actions:
   - vision_status
   - vision_mode
   - vision_capture

This preserves the Anderson House rule:
REPLAY realistic work before a new function enters production.
