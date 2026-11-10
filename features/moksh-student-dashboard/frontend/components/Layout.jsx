// Header, navigation, footer. Owner: Moksh.
import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "@features/publisher-auth/frontend/auth/AuthContext";
import NotificationBell from "@features/search-notifications/frontend/components/NotificationBell";

export default function Layout() {
  const { status, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const close = () => setMenuOpen(false);

  async function onLogout() {
    close();
    await logout();
    navigate("/");
  }

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <div className="container header-row">
          <Link className="brand" to="/" onClick={close}>
            <span className="brand-name">CampusConnect</span>
            <span className="brand-tag">Your campus. One place.</span>
          </Link>
          <button type="button" className="nav-toggle" aria-expanded={menuOpen} aria-controls="site-nav" onClick={() => setMenuOpen((v) => !v)}>
            <span className="visually-hidden">Menu</span>
            <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
          <nav id="site-nav" className={`site-nav ${menuOpen ? "open" : ""}`} aria-label="Main">
            <NavLink to="/" end onClick={close}>
              Announcements
            </NavLink>
            {status === "authenticated" ? (
              <>
                <NavLink to="/publisher" onClick={close}>
                  Manage
                </NavLink>
                <button type="button" className="nav-button" onClick={onLogout}>
                  Log out
                </button>
              </>
            ) : (
              <NavLink to="/publisher/login" onClick={close}>
                Publisher login
              </NavLink>
            )}
            <NotificationBell />
          </nav>
        </div>
      </header>
      <main id="main" className="container main">
        <Outlet />
      </main>
      <footer className="site-footer">
        <div className="container">CampusConnect &middot; Announcements from across campus, in one place.</div>
      </footer>
    </>
  );
}
