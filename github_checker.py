"""
Check target repos for new 'good first issue' / 'help wanted' issues.
"""

import logging
from datetime import datetime, timedelta, timezone

import httpx

from config import GITHUB_TOKEN, TARGET_REPOS, ISSUE_LABELS
from state import is_issue_seen, add_seen_issue

logger = logging.getLogger(__name__)


async def check_new_issues() -> list[dict]:
    """
    Check target repos for new issues with relevant labels.
    Returns list of {"repo", "title", "url", "labels"} dicts.
    """
    new_issues = []
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    # Look at issues from the last 24 hours
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    async with httpx.AsyncClient() as client:
        for repo in TARGET_REPOS:
            for label in ISSUE_LABELS:
                url = f"https://api.github.com/repos/{repo}/issues"
                params = {
                    "labels": label,
                    "state": "open",
                    "since": since,
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 5,
                }

                try:
                    resp = await client.get(
                        url, headers=headers, params=params, timeout=15
                    )
                    if resp.status_code != 200:
                        logger.warning(
                            f"GitHub API {resp.status_code} for {repo}: {resp.text[:200]}"
                        )
                        continue

                    issues = resp.json()
                    for issue in issues:
                        issue_url = issue["html_url"]
                        # Skip PRs (GitHub API returns PRs in issues endpoint)
                        if "pull_request" in issue:
                            continue
                        if not is_issue_seen(issue_url):
                            add_seen_issue(issue_url)
                            new_issues.append(
                                {
                                    "repo": repo,
                                    "title": issue["title"],
                                    "url": issue_url,
                                    "labels": [
                                        l["name"] for l in issue.get("labels", [])
                                    ],
                                }
                            )
                except Exception as e:
                    logger.error(f"GitHub check failed for {repo}: {e}")

    return new_issues


def format_issue_alerts(issues: list[dict]) -> str:
    """Format new issues into a notification message."""
    if not issues:
        return ""

    lines = ["*New issues on target repos:*\n"]
    for issue in issues:
        labels = ", ".join(issue["labels"][:3])
        lines.append(f"[{issue['repo']}] {issue['title']}")
        lines.append(f"  Labels: {labels}")
        lines.append(f"  {issue['url']}\n")

    return "\n".join(lines)
