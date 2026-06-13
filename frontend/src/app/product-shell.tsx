"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { AppNavigation, type AppNavKey } from "@/app/app-navigation";
import { InterfaceModeSwitch, INTERFACE_MODE_STORAGE_KEY, type InterfaceMode } from "@/app/interface-mode-switch";
import { fetchCurrentUser, loginUser, logoutUser, registerUser, type User } from "@/lib/api";

type ProductShellProps = {
  active: "charts" | "reports" | "compatibility" | "interactions";
  children: ReactNode;
};

export function ProductShell({ active, children }: ProductShellProps) {
  const [interfaceMode, setInterfaceMode] = useState<InterfaceMode>("pro");
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [authUsername, setAuthUsername] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authBirthDate, setAuthBirthDate] = useState("");
  const [authBirthTime, setAuthBirthTime] = useState("");
  const [authPlaceName, setAuthPlaceName] = useState("");
  const [authStatus, setAuthStatus] = useState("Проверяю вход...");

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(INTERFACE_MODE_STORAGE_KEY);
      if (saved === "pro" || saved === "beginner") {
        setInterfaceMode(saved);
      }
      setCollapsed(window.localStorage.getItem("jyotish-sidebar-collapsed") === "1");
    } catch {
      // Keep in-memory state when localStorage is unavailable.
    }

    fetchCurrentUser()
      .then((currentUser) => {
        setUser(currentUser);
        setAuthStatus(currentUser ? `Вошли как ${currentUser.username}` : "Войдите, чтобы видеть личные отчёты");
      })
      .catch((error) => setAuthStatus(error instanceof Error ? error.message : "Не удалось проверить вход"));
  }, []);

  const selectInterfaceMode = useCallback((value: InterfaceMode) => {
    setInterfaceMode(value);
    try {
      window.localStorage.setItem(INTERFACE_MODE_STORAGE_KEY, value);
    } catch {
      // Keep the selected mode for this render.
    }
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
      const registrationOptions =
        authBirthDate.trim() && authPlaceName.trim()
          ? {
              display_name: "Моя карта",
              birth_date: authBirthDate.trim(),
              birth_time: authBirthTime.trim(),
              birth_time_accuracy: authBirthTime.trim() ? "exact" : "unknown",
              place_name: authPlaceName.trim(),
            }
          : {};
      const currentUser =
        mode === "login"
          ? await loginUser(authUsername, authPassword)
          : (await registerUser(authUsername, authPassword, registrationOptions)).user;
      setUser(currentUser);
      setAuthPassword("");
      setAuthOpen(false);
      window.dispatchEvent(new Event("jyotish-auth-changed"));
      setAuthStatus(`Вошли как ${currentUser.username}`);
    } catch (error) {
      setAuthStatus(error instanceof Error ? error.message : "Ошибка авторизации");
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
      setAuthStatus(error instanceof Error ? error.message : "Ошибка выхода");
    }
  }

  return (
    <main className={`product-app ${interfaceMode === "beginner" ? "beginner-mode" : "pro-mode"}${collapsed ? " sidebar-collapsed" : ""}`}>
      <aside className="product-sidebar">
        <div className="sidebar-brand-row">
          <div className="mark">Ом</div>
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
          <h1>Jyotish Agent</h1>
          <p>Карты, обзоры, диалоги</p>
        </div>

        <AppNavigation activeKey={active as AppNavKey} />

        <div className="product-sidebar-footer">
          <InterfaceModeSwitch value={interfaceMode} onChange={selectInterfaceMode} />
        </div>
      </aside>

      <div className="product-account-dock" aria-label="Аккаунт">
        {user ? (
          <>
            <span className="product-account-name">{user.username}</span>
            <button type="button" className="product-account-button secondary" onClick={handleLogout}>
              Выйти
            </button>
          </>
        ) : (
          <button type="button" className="product-account-button" onClick={() => setAuthOpen(true)}>
            Войти
          </button>
        )}
      </div>

      {authOpen && !user ? (
        <div className="product-auth-popover-backdrop" role="presentation" onMouseDown={() => setAuthOpen(false)}>
          <section className="product-auth-popover" aria-label="Вход и регистрация" onMouseDown={(event) => event.stopPropagation()}>
            <div className="product-auth-popover-head">
              <div>
                <strong>Вход</strong>
                <span>Регистрация может сразу создать вашу карту. Время рождения необязательно.</span>
              </div>
              <button type="button" onClick={() => setAuthOpen(false)} aria-label="Закрыть">
                ×
              </button>
            </div>
            <div className="product-auth-popover-grid">
              <input placeholder="Логин" value={authUsername} onChange={(event) => setAuthUsername(event.target.value)} />
              <input placeholder="Пароль" type="password" value={authPassword} onChange={(event) => setAuthPassword(event.target.value)} />
              <label>
                Дата рождения
                <input type="date" value={authBirthDate} onChange={(event) => setAuthBirthDate(event.target.value)} />
              </label>
              <label>
                Время
                <input type="time" value={authBirthTime} onChange={(event) => setAuthBirthTime(event.target.value)} />
              </label>
              <label>
                Город рождения
                <input value={authPlaceName} onChange={(event) => setAuthPlaceName(event.target.value)} />
              </label>
            </div>
            <div className="product-auth-popover-actions">
              <button type="button" className="primary-button" onClick={() => handleAuth("login")}>
                Войти
              </button>
              <button type="button" className="secondary-button" onClick={() => handleAuth("register")}>
                Регистрация
              </button>
            </div>
            <span className="product-auth-popover-status">{authStatus}</span>
          </section>
        </div>
      ) : null}

      <section className="product-main">{children}</section>
    </main>
  );
}
