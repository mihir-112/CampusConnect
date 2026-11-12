// Real counts from the database, never placeholders. Owner: core-announcement-engine.
export default function StatsCards({ stats }) {
  const cards = [
    { label: "Total", value: stats.total },
    { label: "Published", value: stats.published },
    { label: "Drafts", value: stats.drafts },
  ];
  return (
    <section aria-label="Announcement statistics">
      <dl className="stats">
        {cards.map((card) => (
          <div key={card.label} className="stat">
            <dt>{card.label}</dt>
            <dd>{card.value}</dd>
          </div>
        ))}
      </dl>
      <p className="stat-categories">
        {Object.entries(stats.by_category).map(([name, count]) => (
          <span key={name}>
            {name}: <strong>{count}</strong>
          </span>
        ))}
      </p>
    </section>
  );
}
