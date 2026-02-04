import { NextResponse } from "next/server";
import { getFile } from "@/lib/github";

export async function GET() {
  try {
    const { content } = await getFile("state.json");
    const data = JSON.parse(content);
    return NextResponse.json(data);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
