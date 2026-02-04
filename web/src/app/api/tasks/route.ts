import { NextRequest, NextResponse } from "next/server";
import { getFile, putFile } from "@/lib/github";

export async function GET() {
  try {
    const { content, sha } = await getFile("tasks.json");
    const data = JSON.parse(content);
    return NextResponse.json({ ...data, _sha: sha });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { _sha, ...data } = body;

    if (!_sha) {
      return NextResponse.json({ error: "Missing _sha field" }, { status: 400 });
    }

    const content = JSON.stringify(data, null, 2) + "\n";
    await putFile("tasks.json", content, _sha, "Update tasks via web dashboard");

    return NextResponse.json({ ok: true });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
