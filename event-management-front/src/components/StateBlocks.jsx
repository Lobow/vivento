export function Loader({ label = "Carregando…" }) {
  return (
    <div className="state-block" role="status">
      <p>{label}</p>
    </div>
  );
}

export function EmptyState({ title, description }) {
  return (
    <div className="state-block">
      <h3>{title}</h3>
      {description && <p>{description}</p>}
    </div>
  );
}

export function ErrorState({ message }) {
  return <div className="alert alert-danger">{message}</div>;
}
