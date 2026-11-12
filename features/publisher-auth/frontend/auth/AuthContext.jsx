// Who is logged in. Owner: publisher-auth.
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { UNAUTHORIZED_EVENT } from "@/api/client";
import * as authApi from "./authApi";
import { clearToken, getToken, setToken } from "./tokenStorage";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // "loading" only lasts while a saved token is being checked with the server.
  const [state, setState] = useState({ status: getToken() ? "loading" : "anonymous", publisher: null });

  useEffect(() => {
    if (!getToken()) return undefined;
    let cancelled = false;
    authApi
      .fetchCurrentPublisher()
      .then((publisher) => !cancelled && setState({ status: "authenticated", publisher }))
      .catch(() => {
        clearToken();
        if (!cancelled) setState({ status: "anonymous", publisher: null });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const onExpired = () => setState({ status: "anonymous", publisher: null });
    window.addEventListener(UNAUTHORIZED_EVENT, onExpired);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onExpired);
  }, []);

  const login = useCallback(async (username, password) => {
    const result = await authApi.login(username, password);
    setToken(result.access_token);
    setState({ status: "authenticated", publisher: result.publisher });
    return result.publisher;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      /* the token may already be invalid; either way we are done */
    }
    clearToken();
    setState({ status: "anonymous", publisher: null });
  }, []);

  const value = useMemo(() => ({ ...state, login, logout }), [state, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside <AuthProvider>");
  return context;
}
