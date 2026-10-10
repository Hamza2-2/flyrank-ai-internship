"""Exercise the actual pages, downloads, ranking interaction and local backend."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "work/site/qa"
QA.mkdir(parents=True, exist_ok=True)
browser_path = next((p for p in [Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")] if p.exists()), None)
if browser_path is None:
    raise RuntimeError("An installed Edge or Chrome browser is required for this local QA script.")
flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
processes = [subprocess.Popen([sys.executable,"-m","http.server","8000","--directory",str(ROOT / "work/site/dist")],
    cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags),
    subprocess.Popen([sys.executable,str(ROOT / "work/backend_api/server.py")], cwd=ROOT,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)]
receipt = {"pages": [], "browser_errors": [], "download_checks": 0, "api_demo": None}
try:
    for url in ["http://127.0.0.1:8000/", "http://127.0.0.1:8787/health"]:
        for attempt in range(50):
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    assert response.status == 200
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError("Local QA service failed to start")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(browser_path), headless=True)
        for width, height, device in [(1440,1000,"desktop"),(390,844,"mobile")]:
            page = browser.new_page(viewport={"width":width,"height":height}, device_scale_factor=1)
            page.on("pageerror", lambda error: receipt["browser_errors"].append(str(error)))
            for name in ["index", "portfolio"]:
                assert page.goto(f"http://127.0.0.1:8000/{name}.html").status == 200
                page.wait_for_load_state("networkidle")
                assert page.locator("h1").count() == 1
                overflow = page.evaluate("document.documentElement.scrollWidth - innerWidth")
                assert overflow <= 0, (name, device, overflow, page.evaluate("[...document.querySelectorAll('*')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).map(e=>[e.tagName,e.className,e.getBoundingClientRect().width]).slice(0,10)"))
                assert page.locator("img").evaluate_all("images => images.every(i => i.complete && i.naturalWidth > 0)")
                receipt["pages"].append({"page":name,"viewport":device,"no_horizontal_overflow":True,"images_loaded":True})
                if name == "index":
                    page.locator("#budget").select_option("100")
                    assert "Precision@100" in page.locator("#comparison-caption").inner_text()
                    page.locator("#budget").select_option("50")
                    assert page.locator("#model-value").inner_text() == "80%"
                    page.locator("#ranking-explorer details").first.locator("summary").click()
                    assert page.locator("#ranking-explorer details").first.get_attribute("open") is not None
                    assert page.locator("#ranking-explorer details").count() == 20
                if name == "portfolio" and device == "desktop":
                    assert page.locator('.api-evidence a').count() == 3
                    assert 'invalid_signal' in page.locator('#bad-input-response').inner_text()
                    assert page.locator('#bad-input-proof + p a').get_attribute('href').startswith('https://github.com/Hamza2-2/flyrank-ai-internship/issues/new?')
                    page.locator("#api-run").click()
                    page.wait_for_function("document.getElementById('api-output').textContent.includes('HTTP 200')")
                    result = page.locator("#api-output").inner_text()
                    assert '"review_score": 9.24' in result
                    assert 'transparent_fixed_rule_v1' in result
                    receipt["api_demo"] = {"actual_http_status":200,"example_score":9.24,"method":"transparent_fixed_rule_v1"}
                    bad_input = json.loads((ROOT / 'work/backend_api/bad_input_example.json').read_text(encoding='utf-8'))
                    page.locator("#api-payload").fill(json.dumps(bad_input['request']))
                    page.locator("#api-run").click()
                    page.wait_for_function("document.getElementById('api-output').textContent.includes('HTTP 422')")
                    actual_error = json.loads(page.locator('#api-output').inner_text().split('\n', 1)[1])
                    assert actual_error == bad_input['response']
                    receipt["api_validation_error"] = 422
                    receipt["evidence_strip"] = {"direct_links": 3, "recorded_error_matches_live_response": True, "adjacent_interview_link": True}
                    page.locator("#api-payload").fill('{"pages":[{"page_id":"page_demo_001","impressions_90d":1200,"ctr_pct":0.4,"avg_position":8,"days_since_last_update":220,"word_count":850}]}')
                    page.locator("#api-run").click()
                    page.wait_for_function("document.getElementById('api-output').textContent.includes('HTTP 200')")
                page.screenshot(path=str(QA/f"{name}-{device}.png"), full_page=True)
                for link in page.locator("a[href]").evaluate_all("links => links.map(a => a.getAttribute('href'))"):
                    if link.startswith(("http:","https:","#","mailto:")):
                        continue
                    with urllib.request.urlopen("http://127.0.0.1:8000/"+link,timeout=5) as response:
                        assert response.status == 200, link
                        receipt["download_checks"] += 1
            page.close()
        browser.close()
    assert not receipt["browser_errors"], receipt["browser_errors"]
    (QA / "verification.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    print(json.dumps(receipt,indent=2))
finally:
    for process in processes:
        process.terminate()
        process.wait(timeout=10)
