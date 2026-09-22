import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Navbar.css";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header className="navbar">
      <div className="container navbar__inner">
        <Link to="/" className="navbar__brand">
          <span className="navbar__brand-mark">●</span>
          Vivento
        </Link>

        <nav className="navbar__links">
          <Link to="/">Eventos</Link>
          {isAuthenticated && <Link to="/events/new">Criar evento</Link>}
        </nav>

        <div className="navbar__actions">
          {isAuthenticated ? (
            <>
              <span className="navbar__user">Olá, {user.name.split(" ")[0]}</span>
              <button className="btn btn-ghost" onClick={handleLogout}>
                Sair
              </button>
            </>
          ) : (
            <>
              <Link className="btn btn-ghost" to="/login">
                Entrar
              </Link>
              <Link className="btn btn-primary" to="/register">
                Criar conta
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
