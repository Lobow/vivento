import { useEffect, useState } from "react";
import { listEvents } from "../api/events";
import { extractErrorMessage } from "../api/client";
import EventCard from "../components/EventCard";
import { EmptyState, ErrorState, Loader } from "../components/StateBlocks";
import "./EventsListPage.css";

const STATUS_OPTIONS = [
  { value: "", label: "Todos" },
  { value: "future", label: "Em breve" },
  { value: "past", label: "Encerrados" },
  { value: "full", label: "Lotados" },
];

export default function EventsListPage() {
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState("");
  const [date, setDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError("");

    listEvents({ status: status || undefined, date: date || undefined })
      .then((data) => {
        if (!ignore) setEvents(data.items);
      })
      .catch((err) => {
        if (!ignore) setError(extractErrorMessage(err, "Não foi possível carregar os eventos."));
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [status, date]);

  return (
    <div>
      <section className="hero">
        <div className="container hero__inner">
          <h1>Encontre e organize eventos que reúnem pessoas.</h1>
          <p>Crie sua página de inscrição em minutos e acompanhe as vagas em tempo real.</p>
        </div>
      </section>

      <div className="page container">
        <div className="filters">
          <div className="filters__status">
            {STATUS_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                className={`filters__chip ${status === opt.value ? "filters__chip--active" : ""}`}
                onClick={() => setStatus(opt.value)}
              >
                {opt.label}
              </button>
            ))}
          </div>
          <div className="field filters__date">
            <label htmlFor="date-filter">Data específica</label>
            <input id="date-filter" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
        </div>

        {loading && <Loader label="Carregando eventos…" />}
        {!loading && error && <ErrorState message={error} />}
        {!loading && !error && events.length === 0 && (
          <EmptyState
            title="Nenhum evento encontrado"
            description="Tente ajustar os filtros ou crie o primeiro evento da plataforma."
          />
        )}

        {!loading && !error && events.length > 0 && (
          <div className="events-grid">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
