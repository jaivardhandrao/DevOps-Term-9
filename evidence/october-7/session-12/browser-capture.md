# Genuine current HTTP browser capture — 7 October 2026

This is a provenance summary of observed tool results, not a recreated terminal transcript.

- The [GET-only relay](../serve-session12-view.py) started at **2026-10-07T18:12:30.943689Z** with the isolated `devops-oct7` context and its explicit kubeconfig.
- Its own Ingress-controller forward was `127.0.0.1:64296`; the browser relay was `127.0.0.1:64297`.
- Each allowed GET (`/` or `/api/health`) was forwarded to the actual controller with `Host: devops.test`. Response body bytes were unchanged. No browser cookies or credentials were forwarded.
- The browser showed **Hello from DevOps session 12 frontend** and the screenshot worker saved [session-12-live-frontend.jpg](../screenshots/session-12-live-frontend.jpg). The image was inspected afterward and contains that response.
- Chrome reported `net::ERR_BLOCKED_BY_CLIENT` for `/api/health`; no API screenshot was saved. A subsequent ordinary HTTP header check at **18:17:03 GMT** returned `200 OK`, `Content-Type: application/json`, `Content-Length: 125`, and no `Content-Disposition` header. This shows a responding API, not successful browser display.
- The proposed new browser fault/recovery drill was **not started** because the API display was blocked. No Ingress object was patched, no URL/content-type workaround was attempted, and no browser protection was bypassed.
- The owning session received Ctrl+C and confirmed **Own session-12 relay and Ingress forward stopped.** No other forward or application resource was stopped.

The screenshot proves the current frontend HTTP Ingress response through the documented
local relay. It does not prove TLS, the API response, or a before/after fault transition.
The earlier [complete lab transcript](20261007T102115Z.txt) remains the evidence for the
actual broken route's 503 and restored API response; its corresponding screenshots remain missing.

![Actual current frontend HTTP response](../screenshots/session-12-live-frontend.jpg)
