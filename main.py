from fetch_jobs import get_new_jobs, save_seen
from score_jobs import score_all
from send_email import send_digest


def main():
    new_jobs, seen = get_new_jobs()
    print(f"{len(new_jobs)} new jobs")

    scored = score_all(new_jobs) if new_jobs else []

    send_digest(scored)
    save_seen(seen)  # only after the email goes out
    print("Done")


if __name__ == "__main__":
    main()