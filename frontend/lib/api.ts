export type HealthResponse = {
  status: "ok" | "degraded";
  version: string;
  env: string;
  checks: { db: "ok" | "error"; redis: "ok" | "error" };
};

// Server components run inside the container: prefer the internal URL.
const API_URL =
  process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getApiHealth(): Promise<HealthResponse | null> {
  try {
    const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as HealthResponse;
  } catch {
    return null;
  }
}
