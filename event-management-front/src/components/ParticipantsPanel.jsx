import { useState } from "react";
import { extractErrorMessage } from "../api/client";
import { registerParticipant, removeParticipant } from "../api/participants";
import { useAuth } from "../context/AuthContext";
import "./ParticipantsPanel.css";

export default function ParticipantsPanel({ event, participants, onChanged, isOwner }) {
  const { isAuthenticated } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const isFull = event.status === "full";

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);
    try {
      await registerParticipant(event.id, { name, email });
      setSuccess("Inscrição confirmada! Nos vemos no evento.");
      setName("");
      setEmail("");
      onChanged();
    } catch (err) {
      setError(extractErrorMessage(err, "Não foi possível concluir a inscrição."));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRemove(participantId) {
    if (!confirm("Remover esta inscrição?")) return;
    try {
      await removeParticipant(event.id, participantId);
      onChanged();
    } catch (err) {
      alert(extractErrorMessage(err, "Não foi possível remover o participante."));
    }
  }

  return (
    <div className="participants-panel">
       {isOwner && ( <div className="participants-panel__list-card">
        <h3>Participantes inscritos ({participants.length})</h3>
        {participants.length === 0 ? (
          <p className="participants-panel__empty">Ainda não há inscrições para este evento.</p>
        ) : (
          <ul className="participants-panel__list">
            {participants.map((p) => (
              <li key={p.id}>
                <div>
                  <strong>{p.name}</strong>
                  <span>{p.email}</span>
                </div>
              
                  <button className="btn btn-danger" onClick={() => handleRemove(p.id)}>
                    Remover
                  </button>
               
              </li>
            ))}
          </ul>
        )}
      </div> 
    )}
      <div className="participants-panel__form-card form-card">
        <h3>Inscreva-se</h3>

        {isFull && (
          <div className="alert alert-danger">
            Este evento está lotado. Não há mais vagas disponíveis.
          </div>
        )}
        {error && <div className="alert alert-danger">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="participant-name">Nome completo</label>
            <input
              id="participant-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={isFull}
            />
          </div>
          <div className="field">
            <label htmlFor="participant-email">E-mail</label>
            <input
              id="participant-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isFull}
            />
          </div>
          <button className="btn btn-primary btn-block" type="submit" disabled={isFull || submitting}>
            {submitting ? "Enviando…" : "Confirmar inscrição"}
          </button>
        </form>
        {!isAuthenticated && (
          <p className="participants-panel__hint">
            Não é necessário criar conta para se inscrever em um evento.
          </p>
        )}
      </div>
    </div>
  );
}
