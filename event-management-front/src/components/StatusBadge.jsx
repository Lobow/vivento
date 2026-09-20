const LABELS = {
  future: "Em breve",
  past: "Encerrado",
  full: "Lotado",
};

export default function StatusBadge({ status }) {
  const label = LABELS[status] || status;
  return <span className={`badge badge-${status}`}>{label}</span>;
}
