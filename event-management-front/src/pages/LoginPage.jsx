import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { extractErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      const redirectTo = location.state?.from?.pathname || "/";
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(extractErrorMessage(err, "E-mail ou senha incorretos."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page container" style={{ display: "flex", justifyContent: "center" }}>
      <div className="form-card">
        <h2 style={{ marginBottom: 6 }}>Entrar</h2>
        <p style={{ color: "var(--color-ink-muted)", marginBottom: 24 }}>
          Acesse sua conta de organizador para gerenciar eventos.
        </p>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit}>
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
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
            {submitting ? "Entrando…" : "Entrar"}
          </button>
        </form>

        <p style={{ marginTop: 18, fontSize: "0.88rem", color: "var(--color-ink-muted)" }}>
          Ainda não tem conta? <Link to="/register" style={{ color: "var(--color-primary)" }}>Criar conta</Link>
        </p>
      </div>
    </div>
  );
}
