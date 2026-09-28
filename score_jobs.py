import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()  # reads ANTHROPIC_API_KEY from .env
MODEL = "claude-haiku-4-5-20251001"  # cheap + fast, good enough for this

with open("profile.txt") as f:
    PROFILE = f.read()

SYSTEM = f"""You score job postings for this candidate:

{PROFILE}

Rules:
- Only judge on what the posting actually says. Don't guess requirements that aren't written.
- Location is never a red flag. A job in a preferred area (or remote) can get +1. Anywhere else in Canada is fine, no penalty. On-site/hybrid/remote doesn't matter.
- If French is required, flag it.
- 0-2 years experience required is OK. 3+ years is a dealbreaker.
- A Bachelor's degree requirement is a small gap, not a dealbreaker (he has a 2-year diploma plus practicum work).
- Keep the reason under 20 words.

Reply with ONLY a JSON object, no other text:
{{"score": <1-10>, "reason": "<one short sentence>", "red_flags": ["<max 3 flags, under 10 words each>"]}}

Scoring guide:
9-10: great fit, apply today
7-8: good fit, worth applying
5-6: maybe, some gaps
1-4: poor fit or a dealbreaker"""


def score_job(job):
    job_text = (
        f"Title: {job['title']}\n"
        f"Company: {job['company']}\n"
        f"Location: {job['city']} (remote: {job['remote']})\n\n"
        f"{job['description'][:4000]}"
    )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM,
        messages=[{"role": "user", "content": job_text}],
    )
    text = msg.content[0].text
    # grab just the JSON part in case Claude adds extra text
    start, end = text.find("{"), text.rfind("}") + 1
    return json.loads(text[start:end])


def score_all(jobs):
    scored = []
    for job in jobs:
        try:
            result = score_job(job)
        except Exception as e:
            print(f"Couldn't score {job['title']} ({e})")
            continue
        job.update(result)
        scored.append(job)
        print(f"[{result['score']}] {job['title']} - {job['company']}")
        print(f"    {result['reason']} {result['red_flags']}\n")
    scored.sort(key=lambda j: j["score"], reverse=True)
    return scored


if __name__ == "__main__":
    with open("new_jobs.json") as f:
        jobs = json.load(f)

    scored = score_all(jobs)

    with open("scored_jobs.json", "w") as f:
        json.dump(scored, f, indent=2)