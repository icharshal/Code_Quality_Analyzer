## 2026-05-20 - [Network Timeout Implementation]
**Learning:** Network calls without explicit timeouts (like `urllib.request.urlopen`) can lead to hanging processes if the remote server is unresponsive, potentially causing a Denial of Service (DoS) vulnerability.
**Action:** Always implement a reasonable timeout (e.g., 30 seconds) in all network operations to ensure the application remains responsive and resilient to network issues.
