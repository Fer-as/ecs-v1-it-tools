import argparse
import datetime
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    parser = argparse.ArgumentParser(description="Verify application HTTPS health.")
    parser.add_argument(
        "--url",
        default="https://tm.feras-dev.co.uk/health",
    )
    parser.add_argument("--attempts", type=int, default=12)
    args = parser.parse_args()

    parsed = urllib.parse.urlsplit(args.url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "tm.feras-dev.co.uk"
        or parsed.netloc not in ("tm.feras-dev.co.uk", "tm.feras-dev.co.uk:443")
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        parser.error("URL must use HTTPS on tm.feras-dev.co.uk, port 443.")

    if not 1 <= args.attempts <= 30:
        parser.error("Attempts must be between 1 and 30.")

    opener = urllib.request.build_opener(RejectRedirects())
    request = urllib.request.Request(
        args.url,
        headers={
            "Accept": "application/json",
            "User-Agent": "ecs-it-tools-health-gate",
        },
    )

    for attempt in range(1, args.attempts + 1):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        print(
            f"{timestamp} attempt={attempt}/{args.attempts} url={args.url}",
            flush=True,
        )

        try:
            with opener.open(request, timeout=10) as response:
                if response.status != 200:
                    raise ValueError(f"Unexpected HTTP status: {response.status}")

                if response.headers.get_content_type() != "application/json":
                    raise ValueError("Expected application/json.")

                body = response.read(4097)
                if len(body) > 4096:
                    raise ValueError("Health response exceeded 4096 bytes.")

                if json.loads(body) != {"status": "ok"}:
                    raise ValueError("Unexpected health JSON.")

            print("PASS: verified HTTPS, HTTP 200 and expected health JSON.")
            return 0

        except (
            urllib.error.URLError,
            OSError,
            ValueError,
        ) as error:
            print(f"Attempt failed: {type(error).__name__}: {error}", flush=True)

        if attempt < args.attempts:
            time.sleep(5)

    print("FAIL: HTTPS health gate exhausted its attempts.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())