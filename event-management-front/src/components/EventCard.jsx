import { Link } from "react-router-dom";
import StatusBadge from "./StatusBadge";
import "./EventCard.css";

const MONTHS = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"];

function formatTime(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

export default function EventCard({ event }) {
  const date = new Date(event.date_time);
  const day = date.getDate().toString().padStart(2, "0");
  const month = MONTHS[date.getMonth()];

  return (
    <Link to={`/events/${event.id}`} className="event-card">
      <div className="event-card__day">
        <span className="event-card__day-number">{day}</span>
        <span className="event-card__day-month">{month}</span>
      </div>

      <div className="event-card__body">
        <div className="event-card__top">
          <h3 className="event-card__title">{event.name}</h3>
          <StatusBadge status={event.status} />
        </div>
        <p className="event-card__meta">
          {formatTime(event.date_time)} · {event.location}
        </p>
        {event.description && <p className="event-card__description">{event.description}</p>}
        <p className="event-card__spots">
          {event.status === "full"
            ? "Todas as vagas preenchidas"
            : `${event.spots_left} de ${event.capacity} vagas disponíveis`}
        </p>
      </div>
    </Link>
  );
}
