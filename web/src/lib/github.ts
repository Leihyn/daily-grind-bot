const GITHUB_TOKEN = process.env.GITHUB_TOKEN!;
const REPO_OWNER = process.env.GITHUB_REPO_OWNER!;
const REPO_NAME = process.env.GITHUB_REPO_NAME!;

interface GitHubFileResponse {
  content: string;
  sha: string;
  encoding: string;
}

async function githubFetch(path: string, options?: RequestInit) {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      ...options?.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`GitHub API error ${res.status}: ${body}`);
  }

  return res.json();
}

export async function getFile(path: string): Promise<{ content: string; sha: string }> {
  const data: GitHubFileResponse = await githubFetch(path);
  const content = Buffer.from(data.content, "base64").toString("utf-8");
  return { content, sha: data.sha };
}

export async function putFile(
  path: string,
  content: string,
  sha: string,
  message: string
): Promise<void> {
  const encoded = Buffer.from(content).toString("base64");
  await githubFetch(path, {
    method: "PUT",
    body: JSON.stringify({
      message,
      content: encoded,
      sha,
    }),
  });
}
