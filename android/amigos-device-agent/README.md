# Three Amigos Device Agent

Purpose: replace Shizuku as the **24/7 foundation** for ordinary phone automation.

## Foundation
- Android `AccessibilityService` for user-enabled UI observation/actions.
- Android `NotificationListenerService` for incoming notification events.
- Shizuku becomes optional, only for rare ADB-level operations.

## Privacy rule
The agent must **not publish message text, screenshots, photos, or other private phone data to the public GitHub repository**. Any future remote transport must use a private authenticated/encrypted channel.

## First-run setup
Install the APK, open **Three Amigos Device Agent**, then:
1. Enable **Three Amigos Accessibility**.
2. Enable **Three Amigos Notifications**.
3. Set the app battery mode to **Unrestricted** on devices that aggressively restrict background apps.

Android manages both bound services after the user enables them.

## Current milestone
This first version provides the Android-native service foundation and UI-action primitives. Remote command transport and private return transport are intentionally separate modules and are the next gate.
