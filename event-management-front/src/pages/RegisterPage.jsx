import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { extractErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(name, email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(extractErrorMessage(err, "Não foi possível criar sua conta."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page container" style={{ display: "flex", justifyContent: "center" }}>
      <div className="form-card">
        <h2 style={{ marginBottom: 6 }}>Criar conta de organizador</h2>
        <p style={{ color: "var(--color-ink-muted)", marginBottom: 24 }}>
          Crie e gerencie seus próprios eventos na plataforma.
        </p>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="name">Nome</label>
            <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="email">E-mail</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Senha</label>
            <input
              id="password"
              type="password"
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
            {submitting ? "Criando conta…" : "Criar conta"}
          </button>
        </form>

        <p style={{ marginTop: 18, fontSize: "0.88rem", color: "var(--color-ink-muted)" }}>
          Já tem conta? <Link to="/login" style={{ color: "var(--color-primary)" }}>Entrar</Link>
        </p>
      </div>
    </div>
  );
}
