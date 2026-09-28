import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("JSEARCH_API_KEY")
URL = "https://api.openwebninja.com/jsearch/search"
HEADERS = {"x-api-key": API_KEY}

QUERIES = [
    "junior software developer in Canada",
    "junior frontend developer in Canada",
    "junior backend developer in Canada",
    "junior full stack developer in Canada",
    "entry level software engineer in Canada",
]

SEEN_FILE = "seen_jobs.json"


def fetch_jobs(query, retries=3):
    params = {
        "query": query,
        "country": "ca",
        "date_posted": "3days",
        "num_pages": 1,
    }
    # res = requests.get(URL, headers=HEADERS, params=params, timeout=30)
    # res.raise_for_status()
    # return res.json().get("data", [])
    for attempt in range(retries):
        try:
            res = requests.get(URL, headers=HEADERS, params=params, timeout=60)
            res.raise_for_status()
            return res.json().get("data", [])
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            print(f"Retry {attempt + 1} for: {query}")
            time.sleep(5)


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen), f, indent=2)

def job_key(job):
    title = (job.get("job_title") or "").lower().strip()
    company = (job.get("employer_name") or "").lower().strip()
    city = (job.get("job_city") or "").lower().strip()
    return f"{title}|{company}|{city}"

def slim(job):
    # keep only what we need
    return {
        # "id": job["job_id"],
        "id": job_key(job),
        "title": job.get("job_title"),
        "company": job.get("employer_name"),
        "city": job.get("job_city"),
        "remote": job.get("job_is_remote"),
        "link": job.get("job_apply_link"),
        "description": job.get("job_description", ""),
    }


def get_new_jobs():
    seen = load_seen()
    new_jobs = []

    for q in QUERIES:
        try:
            jobs = fetch_jobs(q)
        except requests.RequestException as e:
            print(f"Failed: {q} ({e})")
            continue
        
        for job in jobs:
            key = job_key(job)
            if key in seen:
                continue
            seen.add(key)
            new_jobs.append(slim(job))

    return new_jobs, seen


if __name__ == "__main__":
    new_jobs, seen = get_new_jobs()
    print(f"{len(new_jobs)} new jobs")

    with open("new_jobs.json", "w") as f:
        json.dump(new_jobs, f, indent=2)

    save_seen(seen)