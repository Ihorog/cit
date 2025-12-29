# Secure Access to CIT

This document describes how to securely access the CIT server running on an Android/Termux device using Tailscale, a WireGuard-based VPN mesh network.

## Recommended method: Tailscale

Tailscale is chosen as the preferred solution because it is easy to set up on Android, automatically establishes secure connections between devices, and avoids the need for manual port forwarding. Devices joined to a Tailscale network can reach each other over private IP addresses.

## Installing Tailscale on Android

1. Open the Google Play Store on the device running CIT and install the Tailscale app (or download it from Tailscale’s download page).
2. Launch the Tailscale app and choose **Get Started**.
3. Accept the prompts to install the VPN configuration and allow notifications.
4. Sign in with a supported identity provider (Google, GitHub, Microsoft, etc.).
5. Once signed in, the device will obtain a `100.x.x.x` Tailscale IP address. Note this address for connecting to CIT.

## Accessing CIT through Tailscale

1. Ensure the CIT server is running on the Android device. It listens on port `8790` and binds to all network interfaces by default.
2. Install and log in to Tailscale on any other device that needs to access CIT (for example, your laptop).
3. On the other device, open a browser and navigate to `http://<tailscale-ip-of-android>:8790/health` to verify the server is reachable. You should see a JSON response indicating `ok: true`.
4. Send chat requests to `http://<tailscale-ip-of-android>:8790/chat` as you normally would.

## Security notes

- Use Tailscale’s ACL features if you need to restrict access or share the CIT service with specific users.
- Do not expose the CIT port directly to the public internet. Tailscale encrypts traffic end‑to‑end and limits access to authenticated devices.
