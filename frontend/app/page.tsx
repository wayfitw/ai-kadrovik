import { getApiHealth } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const health = await getApiHealth();
  return (
    <main>
      <h1>AI-Кадровик</h1>
      <p>Кабинет кадровика и руководителя. Этап 1 — MVP на ручном вводе.</p>
      <h2>Состояние API</h2>
      {health ? (
        <ul>
          <li>Статус: {health.status}</li>
          <li>Версия: {health.version}</li>
          <li>Среда: {health.env}</li>
          <li>База данных: {health.checks.db}</li>
          <li>Redis: {health.checks.redis}</li>
        </ul>
      ) : (
        <p>API недоступен.</p>
      )}
    </main>
  );
}
