from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SCREENSHOTS_DIR = Path(__file__).resolve().parent / "test-screenshots"


def test_frontend():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        base_url = "http://localhost:3000"

        try:
            page.goto(base_url, timeout=10000)
            page.wait_for_load_state("networkidle")
        except (PlaywrightTimeoutError, Exception) as e:
            print(f"Warning: Could not connect to localhost:3000. Error: {e}")
            base_url = "http://localhost:3001"
            try:
                page.goto(base_url, timeout=10000)
                page.wait_for_load_state("networkidle")
            except Exception as fallback_error:
                print(
                    f"Error: Fallback to localhost:3001 also failed: {fallback_error}"
                )
                browser.close()
                raise

        print(f"Testing at: {base_url}\n")

        tests = [
            ("Homepage", "/"),
            ("Login", "/login"),
            ("Register", "/register"),
            ("Patient Dashboard", "/patient"),
            ("Nurse Dashboard", "/nurse"),
        ]

        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        for name, path in tests:
            try:
                page.goto(f"{base_url}{path}", timeout=10000)
                page.wait_for_load_state("networkidle")

                html = page.content()
                has_rtl = 'dir="rtl"' in html
                has_arabic = 'lang="ar"' in html
                has_cairo = "Cairo" in html or "font-cairo" in html

                h1_count = len(page.locator("h1").all())

                result = {
                    "name": name,
                    "path": path,
                    "rtl": has_rtl,
                    "arabic": has_arabic,
                    "cairo": has_cairo,
                    "h1_count": h1_count,
                    "status": "PASS" if (has_rtl and has_arabic) else "FAIL",
                }
                results.append(result)

                status_icon = "[PASS]" if result["status"] == "PASS" else "[FAIL]"
                print(f"{status_icon} {name} ({path})")
                print(
                    f"   RTL: {has_rtl}, Arabic: {has_arabic}, Cairo: {has_cairo}, H1s: {h1_count}"
                )

                safe_name = path.replace("/", "-").strip("-") or "homepage"
                page.screenshot(
                    path=str(SCREENSHOTS_DIR / f"{safe_name}.png"),
                    full_page=True,
                )

            except Exception as e:
                results.append(
                    {"name": name, "path": path, "status": "ERROR", "error": str(e)}
                )
                print(f"[ERROR] {name} ({path}) - {e}")

        browser.close()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    print(f"Errors: {errors}/{len(results)}")

    if passed == len(results):
        print("\nALL TESTS PASSED!")

    return results


if __name__ == "__main__":
    test_frontend()
