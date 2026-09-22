import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { deleteEvent, getEvent } from "../api/events";
import { listParticipants } from "../api/participants";
import { extractErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";
import StatusBadge from "../components/StatusBadge";
import ParticipantsPanel from "../components/ParticipantsPanel";
import { ErrorState, Loader } from "../components/StateBlocks";
import "./EventDetailPage.css";

function formatDateTime(isoString) {
  return new Date(isoString).toLocaleString("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function EventDetailPage() {
  const { id } = useParams();
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [event, setEvent] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(async () => {
    try {
      const [eventData, participantsData] = await Promise.all([
        getEvent(id),
        isAuthenticated && listParticipants(id),
      ]);
      setEvent(eventData);
      isAuthenticated && setParticipants(participantsData);
    } catch (err) {
      setError(extractErrorMessage(err, "Não foi possível carregar o evento."));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleDelete() {
    if (!confirm("Tem certeza que deseja excluir este evento? Essa ação não pode ser desfeita.")) return;
    setDeleting(true);
    try {
      await deleteEvent(id);
      navigate("/");
    } catch (err) {
      alert(extractErrorMessage(err, "Não foi possível excluir o evento."));
      setDeleting(false);
    }
  }

  if (loading) return <Loader label="Carregando evento…" />;
  if (error) return <div className="page container"><ErrorState message={error} /></div>;
  if (!event) return null;

  const isOwner = isAuthenticated && user?.id === event.organizer_id;

  return (
    <div className="page container">
      <Link to="/" className="event-detail__back">
        ← Voltar para eventos
      </Link>

      <div className="event-detail__header">
        <div>
          <StatusBadge status={event.status} />
          <h1 className="event-detail__title">{event.name}</h1>
          <p className="event-detail__meta">
            {formatDateTime(event.date_time)} · {event.location}
          </p>
        </div>

        {isOwner && (
          <div className="event-detail__owner-actions">
            <Link className="btn btn-secondary" to={`/events/${event.id}/edit`}>
              Editar
            </Link>
            <button className="btn btn-danger" onClick={handleDelete} disabled={deleting}>
              {deleting ? "Excluindo…" : "Excluir"}
            </button>
          </div>
        )}
      </div>

      {event.description && <p className="event-detail__description">{event.description}</p>}

      <div className="event-detail__stats">
        <div>
          <strong>{event.participants_count}</strong>
          <span>inscritos</span>
        </div>
        <div>
          <strong>{event.spots_left}</strong>
          <span>vagas restantes</span>
        </div>
        <div>
          <strong>{event.capacity}</strong>
          <span>capacidade total</span>
        </div>
      </div>

      {isAuthenticated && <ParticipantsPanel
        event={event}
        participants={participants}
        onChanged={load}
        isOwner={isOwner}
      />}
    </div>
  );
}
