"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { AppNavigation, appNavItems, type AppNavKey } from "@/app/app-navigation";
import { INTERFACE_MODE_STORAGE_KEY, type InterfaceMode } from "@/app/interface-mode-switch";
import { fetchCurrentUser, loginUser, logoutUser, registerUser, type User } from "@/lib/api";

type ProductShellProps = {
  active: AppNavKey;
  children: ReactNode;
};

function friendlyStatus(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}

export function ProductShell({ active, children }: ProductShellProps) {
  const [interfaceMode, setInterfaceMode] = useState<InterfaceMode>("pro");
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authUsername, setAuthUsername] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authStatus, setAuthStatus] = useState("Проверяю вход...");

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(INTERFACE_MODE_STORAGE_KEY);
      if (saved === "pro" || saved === "beginner") setInterfaceMode(saved);
      setCollapsed(window.localStorage.getItem("jyotish-sidebar-collapsed") === "1");
    } catch {
      // Keep in-memory state when localStorage is unavailable.
    }

    fetchCurrentUser()
      .then((currentUser) => {
        setUser(currentUser);
        setAuthStatus(currentUser ? `Вошли как ${currentUser.username}` : "Войдите, чтобы открыть личное пространство");
      })
      .catch((error) => setAuthStatus(friendlyStatus(error, "Не удалось проверить вход")));
  }, []);

  const toggleCollapsed = useCallback(() => {
    setCollapsed((current) => {
      const next = !current;
      try {
        window.localStorage.setItem("jyotish-sidebar-collapsed", next ? "1" : "0");
      } catch {
        // Collapsed state can stay in memory for this tab.
      }
      return next;
    });
  }, []);

  async function handleAuth(mode: "login" | "register") {
    try {
      setAuthStatus(mode === "login" ? "Вхожу..." : "Регистрирую...");
      const currentUser =
        mode === "login"
          ? await loginUser(authUsername, authPassword)
          : (await registerUser(authUsername, authPassword)).user;
      setUser(currentUser);
      setAuthPassword("");
      setAuthOpen(false);
      window.dispatchEvent(new Event("jyotish-auth-changed"));
      setAuthStatus(`Вошли как ${currentUser.username}`);
      window.location.assign("/charts");
    } catch (error) {
      setAuthStatus(friendlyStatus(error, "Ошибка авторизации"));
    }
  }

  async function handleLogout() {
    try {
      await logoutUser();
      setUser(null);
      setAuthOpen(false);
      window.dispatchEvent(new Event("jyotish-auth-changed"));
      setAuthStatus("Вы вышли из аккаунта");
    } catch (error) {
      setAuthStatus(friendlyStatus(error, "Ошибка выхода"));
    }
  }

  const activeItem = appNavItems.find((item) => item.key === active);

  return (
    <main className={`product-app ${interfaceMode === "beginner" ? "beginner-mode" : "pro-mode"}${collapsed ? " sidebar-collapsed" : ""}`}>
      <aside className="product-sidebar">
        <div className="sidebar-brand-row">
          <div className="mark jyotish-mark" aria-hidden="true">
            <svg viewBox="0 0 48 48" focusable="false">
              <circle cx="24" cy="24" r="7.5" />
              <circle cx="24" cy="24" r="14.5" />
              <path d="M24 3v7M24 38v7M3 24h7M38 24h7" />
              <path d="M9.15 9.15l4.95 4.95M33.9 33.9l4.95 4.95M38.85 9.15l-4.95 4.95M14.1 33.9l-4.95 4.95" />
              <path d="M24 10.5l3 7.3 7.7.7-5.85 5.1 1.75 7.6L24 27.15l-6.6 4.05 1.75-7.6-5.85-5.1 7.7-.7z" />
            </svg>
          </div>
          <button
            type="button"
            className="sidebar-collapse-button"
            onClick={toggleCollapsed}
            aria-label={collapsed ? "Развернуть меню" : "Свернуть меню"}
            title={collapsed ? "Развернуть меню" : "Свернуть меню"}
          >
            {collapsed ? "›" : "‹"}
          </button>
        </div>

        <div className="sidebar-title">
          <h1>Веда Джйотиш</h1>
        </div>

        <AppNavigation activeKey={active} />
      </aside>

      <section className="product-workspace">
        <header className="product-shell-topbar" aria-label="Панель аккаунта">
          <div className="product-shell-context">
            <strong>{activeItem?.label ?? "Веда Джйотиш"}</strong>
            {user ? <span>{user.username}</span> : null}
          </div>
          <div className="product-account-dock" aria-label="Аккаунт">
            {user ? (
              <>
                <span className="product-account-name">{user.username}</span>
                <button type="button" className="product-account-button secondary" onClick={handleLogout}>
                  Выйти
                </button>
              </>
            ) : (
              <button
                type="button"
                className="product-account-button"
                onClick={() => {
                  setAuthMode("login");
                  setAuthOpen(true);
                }}
              >
                Войти
              </button>
            )}
          </div>
        </header>

        <section className="product-main">{children}</section>
      </section>

      {authOpen && !user ? (
        <div className="product-auth-popover-backdrop" role="presentation" onMouseDown={() => setAuthOpen(false)}>
          <section className="product-auth-popover" aria-label="Вход и регистрация" onMouseDown={(event) => event.stopPropagation()}>
            <div className="product-auth-popover-head">
              <div>
                <strong>{authMode === "login" ? "Вход" : "Регистрация"}</strong>
                {authMode === "register" ? <span>Данные рождения вводятся отдельно в форме создания карты.</span> : null}
              </div>
              <button type="button" onClick={() => setAuthOpen(false)} aria-label="Закрыть">
                ×
              </button>
            </div>
            <div className="product-auth-mode-switch" role="tablist" aria-label="Режим авторизации">
              <button type="button" className={authMode === "login" ? "active" : ""} onClick={() => setAuthMode("login")}>
                Вход
              </button>
              <button type="button" className={authMode === "register" ? "active" : ""} onClick={() => setAuthMode("register")}>
                Регистрация
              </button>
            </div>
            <div className="product-auth-popover-grid">
              <input placeholder="Логин" value={authUsername} onChange={(event) => setAuthUsername(event.target.value)} />
              <input placeholder="Пароль" type="password" value={authPassword} onChange={(event) => setAuthPassword(event.target.value)} />
            </div>
            <div className="product-auth-popover-actions">
              <button type="button" className="primary-button" onClick={() => handleAuth(authMode)}>
                {authMode === "login" ? "Войти" : "Зарегистрироваться"}
              </button>
            </div>
            <span className="product-auth-popover-status">{authStatus}</span>
          </section>
        </div>
      ) : null}
    </main>
  );
}
