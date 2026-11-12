// Publisher login. Owner: publisher-auth.
import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { usePageTitle } from "@/utils/usePageTitle";
import { useAuth } from "../auth/AuthContext";
import "../auth.css";

export default function LoginPage() {
  usePageTitle("Publisher login");
  const { status, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const destination = location.state?.from || "/publisher";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  if (status === "authenticated") return <Navigate to={destination} replace />;

  async function onSubmit(event) {
    event.preventDefault();
    const found = {};
    if (!username.trim()) found.username = "Enter your username.";
    if (!password) found.password = "Enter your password.";
    setErrors(found);
    setMessage("");
    if (Object.keys(found).length) return;

    setBusy(true);
    try {
      await login(username.trim(), password);
      navigate(destination, { replace: true });
    } catch (error) {
      setErrors(error.fields || {});
      setMessage(error.message);
      setPassword("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth-card" aria-labelledby="login-title">
      <h1 id="login-title">Publisher login</h1>
      <p className="hint">For authorised staff only. Students can read announcements without logging in.</p>
      {message && (
        <p className="flash flash-error" role="alert">
          {message}
        </p>
      )}
      <form onSubmit={onSubmit} noValidate>
        <div className="form-row">
          <label htmlFor="username">Username</label>
          <input id="username" type="text" autoComplete="username" autoFocus value={username} onChange={(e) => setUsername(e.target.value)} aria-invalid={Boolean(errors.username)} aria-describedby={errors.username ? "username-error" : undefined} />
          {errors.username && <p className="field-error" id="username-error">{errors.username}</p>}
        </div>
        <div className="form-row">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} aria-invalid={Boolean(errors.password)} aria-describedby={errors.password ? "password-error" : undefined} />
          {errors.password && <p className="field-error" id="password-error">{errors.password}</p>}
        </div>
        <button type="submit" className="btn btn-primary btn-block" disabled={busy}>
          {busy ? "Logging in..." : "Log in"}
        </button>
      </form>
    </section>
  );
}
