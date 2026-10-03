# Prime Video Native Title Open — Proven Android Function

## Status
PROVEN on moto g power (2021), Android 11, Prime Video package:
`com.amazon.avod.thirdpartyclient`

## Purpose
Open a specific Prime Video title directly in the installed Prime Video app, bypassing the browser.

## Working route
Use an Android VIEW intent and explicitly target Prime Video's detail-page activity:

- Package: `com.amazon.avod.thirdpartyclient`
- Activity: `com.amazon.avod.detailpage.ui.core.DetailPageActivity`
- Data URL: `https://www.primevideo.com/detail/<TITLE_ID>`

## Proven example
Plain Sight title ID:
`0NLO0TU5CRDWWOQ4WYX9D7YOFK`

Working command pattern:
```sh
~/bin/rish -c 'am start -a android.intent.action.VIEW -d "https://www.primevideo.com/detail/0NLO0TU5CRDWWOQ4WYX9D7YOFK" -n com.amazon.avod.thirdpartyclient/com.amazon.avod.detailpage.ui.core.DetailPageActivity'
```

## Important finding
The app-native URI:
`aiv://app.primevideo.com/detail/<TITLE_ID>`
resolved to Prime Video but produced an in-app "Problem occurred" error for Plain Sight.

The explicit HTTPS detail route targeted directly at `DetailPageActivity` opened the title successfully.

## Safety/default behavior
- Open title detail page only.
- Do not start playback automatically.
- Do not purchase/rent anything.
- Do not tap or navigate further unless explicitly requested.

## Three Amigos flow
Tomo → GitHub → V2 push bridge → Codex exec → rish/Shizuku → Android → Prime Video detail page
