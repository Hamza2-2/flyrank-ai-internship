"""Render actual local documents and record evidence; no external UI is imitated."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CONTEXT = ROOT / "work" / "context"
BROWSER = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def main():
    manifest = json.loads((CONTEXT / "fluency_manifest.json").read_text(encoding="utf-8"))
    profile = Path(tempfile.mkdtemp(prefix="flyrank-fluency-render-"))
    outputs = []
    try:
        def render(source, target, screenshot=False, size="1280,1800"):
            cmd = [str(BROWSER), "--headless", "--disable-gpu", "--disable-dev-shm-usage", "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "--no-pdf-header-footer", "--allow-file-access-from-files", f"--user-data-dir={profile}", f"--window-size={size}"]
            cmd.append(("--screenshot=" if screenshot else "--print-to-pdf=") + str(target))
            cmd.append(source.as_uri())
            run = subprocess.run(cmd, capture_output=True, timeout=60)
            if run.returncode != 0 or not target.is_file() or target.stat().st_size < 500:
                raise RuntimeError(f"Browser render did not produce {target.name}: exit {run.returncode}")
            outputs.append({"path": target.relative_to(ROOT).as_posix(), "size_bytes": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "type": "actual local browser screenshot" if screenshot else "browser-printed PDF"})

        for foldername in manifest["folders"]:
            folder = ROOT / foldername
            render(folder / "deliverable.html", folder / "deliverable.pdf")
        map_folder = ROOT / "work" / "assignments" / "Draw_the_Path_Portfolio_Sitemap_and_Toolkit"
        render(map_folder / "sitemap_render.html", map_folder / "sitemap.png", True, "1280,850")
        render(map_folder / "context_evidence.html", map_folder / "context_doc_screenshot.png", True, "1280,2600")
        render(map_folder / "pressure_test.html", map_folder / "pressure_test_screenshot.png", True, "1280,2500")
        render(CONTEXT / "portfolio_maintenance_reminder.html", CONTEXT / "reminder_screenshot.png", True, "1280,1300")
        reminder = CONTEXT / "portfolio_maintenance_reminder.md"
        reminder_evidence = {"evidence_kind": "actual saved local recurring note", "external_calendar_imported": False, "automatic_notification_service": False, "created_date": "2026-10-09", "first_due": "2026-10-16T18:00:00+05:00", "timezone": "Asia/Karachi", "recurrence": "every Friday at 18:00 until case is added", "note": "work/context/portfolio_maintenance_reminder.md", "sha256": hashlib.sha256(reminder.read_bytes()).hexdigest(), "calendar_aid": "work/context/portfolio_maintenance_reminder.ics", "next_case": "Deploy and harden the backend review API", "next_case_intention_status": "explicitly confirmed by Hamza", "next_case_work_status": "planned; production hosting, HTTPS, authentication/rate limits, tests, rollback, and deployment evidence are not done", "next_case_page": "work/site/dist/cases/backend-api-deployment.html", "screenshot_provenance": "headless Chrome screenshot of the actual local reminder HTML; no external calendar UI"}
        for foldername in manifest["folders"]:
            folder = ROOT / foldername
            if "capstones/" in foldername:
                shutil.copy2(CONTEXT / "reminder_screenshot.png", folder / "reminder_screenshot.png")
                shutil.copy2(CONTEXT / "project_context.md", folder / "preserved_build_context.md")
                shutil.copy2(CONTEXT / "portfolio_maintenance_reminder.md", folder / "portfolio_maintenance_reminder.md")
                shutil.copy2(CONTEXT / "portfolio_maintenance_reminder.ics", folder / "portfolio_maintenance_reminder.ics")
                (folder / "reminder_evidence.json").write_text(json.dumps(reminder_evidence, indent=2) + "\n", encoding="utf-8")
            elif folder.name == "Draw_the_Path_Portfolio_Sitemap_and_Toolkit":
                shutil.copy2(CONTEXT / "project_context.md", folder / "saved_project_context.md")
            elif folder.name == "FL-01_AI_Workflow_Audit_and_Tool_Setup":
                shutil.copy2(CONTEXT / "claude_project_instructions.txt", folder / "claude_project_instructions.txt")
        (CONTEXT / "render_evidence.json").write_text(json.dumps({"browser": "Google Chrome headless", "created_date": "2026-10-09", "external_actions": "none", "outputs": outputs}, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"rendered_outputs": len(outputs), "task_folders": len(manifest["folders"]), "external_calendar_imported": False}))
    finally:
        temp_root = Path(tempfile.gettempdir()).resolve()
        resolved_profile = profile.resolve()
        if resolved_profile.is_relative_to(temp_root) and resolved_profile.name.startswith("flyrank-fluency-render-"):
            shutil.rmtree(resolved_profile, ignore_errors=True)


if __name__ == "__main__":
    main()
