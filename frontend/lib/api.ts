export interface Citation {
  title: string;
  url: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  context: Record<string, unknown>;
}

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function streamQuery(query: string, onToken: (token: string) => void) {
  const response = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, stream: true }),
  });

  if (!response.ok || !response.body) {
    throw new Error("Failed to start stream");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";
    for (const part of parts) {
      const line = part.replace(/^data: /, "").trim();
      if (!line) continue;
      const payload = JSON.parse(line);
      if (payload.text) {
        onToken(payload.text as string);
      }
      if (payload.done) {
        return payload as { done: true; citations: Citation[]; context: Record<string, unknown> };
      }
    }
  }
  return { done: true, citations: [], context: {} };
}
