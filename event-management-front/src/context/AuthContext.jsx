import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { fetchMe, login as loginRequest, registerUser } from "../api/auth";
import { clearToken, getToken, setToken } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await fetchMe();
      setUser(me);
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  async function login(email, password) {
    const { access_token: token } = await loginRequest({ email, password });
    setToken(token);
    const me = await fetchMe();
    setUser(me);
    return me;
  }

  async function register(name, email, password) {
    await registerUser({ name, email, password });
    await login(email, password);
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  const value = { user, loading, login, register, logout, isAuthenticated: Boolean(user) };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  return ctx;
}
