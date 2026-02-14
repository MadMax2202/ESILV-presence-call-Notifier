import json
import re
import time
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from plyer import notification
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

BASE = "https://my.devinci.fr"
SCHEDULE_URL = f"{BASE}/student/presences/"
SESSION_FILE = "session.json"

TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")


@dataclass
class Course:
    name: str
    start_time: datetime
    url: str


def toast(title: str, msg: str):
    notification.notify(title=title, message=msg, timeout=12)


def today_dt(hhmm: str) -> datetime:
    now = datetime.now()
    h, m = map(int, hhmm.split(":"))
    return now.replace(hour=h, minute=m, second=0, microsecond=0)


def fetch_today_courses() -> List[Course]:
    """
    Open /student/presences/ and extract courses + start times + links from #bloc_presences.
    """
    courses: List[Course] = []
    now = datetime.now()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(storage_state=SESSION_FILE)
        page = ctx.new_page()
        page.goto(SCHEDULE_URL, wait_until="networkidle", timeout=60_000)

        bloc = page.locator("#bloc_presences")
        text = bloc.inner_text(timeout=10_000)

        # Collect candidate links in the block
        links = bloc.locator("a[href]").all()

        # Build mapping: link_text -> href
        candidates = []
        for a in links:
            href = a.get_attribute("href") or ""
            label = (a.inner_text() or "").strip()
            if href:
                # normalize relative urls
                if href.startswith("/"):
                    href = BASE + href
                candidates.append((label, href))

        # Heuristic: look for times in the block text, then attach nearest link by label match.
        # If your portal is structured in rows, this will still work reasonably, and you can refine later.
        times = TIME_RE.findall(text)

        if not times:
            browser.close()
            return []

        # If we have explicit rows later, you can replace this with row-wise parsing.
        for t in sorted(set(times)):
            start = today_dt(t)
            if start < now - timedelta(hours=2):
                continue

            # choose a link that contains the time or is likely a "details" link
            chosen_url = None
            chosen_name = f"Course @ {t}"

            for label, href in candidates:
                if t in label:
                    chosen_url = href
                    chosen_name = label
                    break

            if not chosen_url and candidates:
                # fallback: first candidate (you'll refine once you print candidates)
                chosen_name, chosen_url = candidates[0][0] or chosen_name, candidates[0][1]

            if chosen_url:
                courses.append(Course(name=chosen_name, start_time=start, url=chosen_url))

        browser.close()

    # Deduplicate by url+time
    uniq = {}
    for c in courses:
        uniq[(c.url, c.start_time)] = c
    return list(uniq.values())


def presence_open(course_url: str) -> bool:
    """Return True if the course presence page shows a 'validate presence' action."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(storage_state=SESSION_FILE)
        page = ctx.new_page()
        page.goto(course_url, wait_until="networkidle", timeout=60_000)

        # Try a few common French labels (adjust once you see the exact wording)
        selectors = [
            "text=Valider ma présence",
            "text=Valider ma presence",
            "text=Valider présence",
            "text=Je suis présent",
            "text=Présent",
        ]

        for sel in selectors:
            loc = page.locator(sel).first
            try:
                if loc.is_visible(timeout=2000):
                    browser.close()
                    return True
            except Exception:
                pass

        browser.close()
        return False


def poll_course_until_open(course: Course, window_min: int = 20):
    """Poll course page politely until presence opens, then notify once."""
    deadline = course.start_time + timedelta(minutes=window_min)
    base = 300  # 5 minutes

    while datetime.now() < deadline:
        try:
            if presence_open(course.url):
                toast("Presence is open", f"{course.name}\nOpen and validate now: {course.url}")
                return

            # Polite interval + jitter
            time.sleep(base * random.uniform(0.85, 1.15))

        except PWTimeoutError:
            # If portal is slow, back off
            time.sleep(10 * 60)
        except Exception:
            # Any unexpected issue: back off more
            time.sleep(20 * 60)


def refresh_schedule_and_plan(sched: BackgroundScheduler):
    """Run at 08:15: fetch today's courses and schedule polling jobs."""
    courses = fetch_today_courses()

    # Debug print: first time you run, see what it extracts
    print(f"[{datetime.now()}] Found {len(courses)} courses")
    for c in courses:
        print(" -", c.start_time.strftime("%H:%M"), c.name, c.url)

    # Schedule polling for each course start
    for c in courses:
        # small offset so you're not hitting exactly at start time every day
        run_at = c.start_time + timedelta(seconds=random.randint(0, 60))
        if run_at < datetime.now():
            continue

        sched.add_job(
            poll_course_until_open,
            "date",
            run_date=run_at,
            args=[c],
            id=f"poll-{c.start_time.isoformat()}-{hash(c.url)}",
            replace_existing=True,
        )


def main():
    sched = BackgroundScheduler()

    # Weekdays at 08:15
    sched.add_job(lambda: refresh_schedule_and_plan(sched), "cron", day_of_week="mon-fri", hour=8, minute=15)
    refresh_schedule_and_plan(sched)
    sched.start()
    print("Presence notifier running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        sched.shutdown()


if __name__ == "__main__":
    main()
