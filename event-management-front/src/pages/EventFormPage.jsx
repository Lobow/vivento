import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { createEvent, getEvent, updateEvent } from "../api/events";
import { extractErrorMessage } from "../api/client";
import { Loader } from "../components/StateBlocks";

function toDatetimeLocal(isoString) {
  if (!isoString) return "";
  const date = new Date(isoString);
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60000);
  return local.toISOString().slice(0, 16);
}

const emptyForm = { name: "", description: "", date_time: "", location: "", capacity: 50 };

export default function EventFormPage() {
  const { id } = useParams();
  const isEditing = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(isEditing);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isEditing) return;
    getEvent(id)
      .then((event) => {
        setForm({
          name: event.name,
          description: event.description || "",
          date_time: toDatetimeLocal(event.date_time),
          location: event.location,
          capacity: event.capacity,
        });
      })
      .catch((err) => setError(extractErrorMessage(err, "Não foi possível carregar o evento.")))
      .finally(() => setLoading(false));
  }, [id, isEditing]);

  function handleChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    const payload = {
      ...form,
      capacity: Number(form.capacity),
      date_time: new Date(form.date_time).toISOString(),
    };

    try {
      const event = isEditing ? await updateEvent(id, payload) : await createEvent(payload);
      navigate(`/events/${event.id}`);
    } catch (err) {
      setError(extractErrorMessage(err, "Não foi possível salvar o evento."));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Loader label="Carregando evento…" />;

  return (
    <div className="page container" style={{ display: "flex", justifyContent: "center" }}>
      <div className="form-card" style={{ maxWidth: 640 }}>
        <h2 style={{ marginBottom: 6 }}>{isEditing ? "Editar evento" : "Criar novo evento"}</h2>
        <p style={{ color: "var(--color-ink-muted)", marginBottom: 24 }}>
          Preencha os dados abaixo para {isEditing ? "atualizar" : "publicar"} o evento.
        </p>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="name">Nome do evento</label>
            <input
              id="name"
              value={form.name}
              onChange={(e) => handleChange("name", e.target.value)}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="description">Descrição</label>
            <textarea
              id="description"
              rows={4}
              value={form.description}
              onChange={(e) => handleChange("description", e.target.value)}
            />
          </div>

          <div className="field-row">
            <div className="field">
              <label htmlFor="date_time">Data e hora</label>
              <input
                id="date_time"
                type="datetime-local"
                value={form.date_time}
                onChange={(e) => handleChange("date_time", e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="capacity">Capacidade (vagas)</label>
              <input
                id="capacity"
                type="number"
                min="1"
                value={form.capacity}
                onChange={(e) => handleChange("capacity", e.target.value)}
                required
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="location">Local</label>
            <input
              id="location"
              value={form.location}
              onChange={(e) => handleChange("location", e.target.value)}
              required
            />
          </div>

          <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
            {submitting ? "Salvando…" : isEditing ? "Salvar alterações" : "Publicar evento"}
          </button>
        </form>
      </div>
    </div>
  );
}
