# M4 production HTTPS gate verification — 26 September 2026

The verification workflow revision was `3f335122ee57bb08ae78ae9a1780db1dd4868462`. It invoked the **unchanged** production command `python3 scripts/check_https_health.py` in both modes. This tests gate rejection and failure propagation; it is **not** an ECS outage or a failed ECS deployment. Neither run changed AWS resources.

| Mode | GitHub Actions evidence | Observed result |
| --- | --- | --- |
| Controlled unhealthy | [Run 36280113216](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36280113216), attempt 1, [verify job 108510214322](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36280113216/job/108510214322) | Overall `failure`; fixture step `failure`; healthy step skipped |
| Live healthy recovery | [Run 36280236296](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36280236296), attempt 1, [verify job 108510564190](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36280236296/job/108510564190) | Overall `success`; live gate step `success`; fixture step skipped |

GitHub run metadata and job logs were read on 27 September 2026. The unhealthy job log shows the fixture preflight and all **12** production-script attempts against `https://tm.feras-dev.co.uk/health` failing with `HTTPError: HTTP Error 503: Service Unavailable`; the script then printed `FAIL: HTTPS health gate exhausted its attempts.` The unmasked failing step made the job and run red. The fixture was an HTTPS server bound to runner loopback, with runner-local DNS and certificate trust; it did not alter public DNS, the deployed ECS service or AWS.

The separate healthy job selected `MODE: healthy`; the production script used public DNS and normal TLS trust and printed `PASS: verified HTTPS, HTTP 200 and expected health JSON.` on attempt 1. GitHub reports the overall run conclusion as `success`. The healthy runner did not inherit the unhealthy runner's hosts or trust changes. A separate [post-M4 independent HTTP capture](terraform/2026-09-27-m4-final-http.txt) records HTTP 200, `Content-Type: application/json` and `{"status":"ok"}`. Its response `Date` header is 27 September 2026 00:15:13 GMT. The earlier [M3 HTTP capture](terraform/2026-09-26-m3-final-http.txt) predates M4.
