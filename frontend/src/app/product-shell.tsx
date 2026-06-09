"use client";

import Link from "next/link";
import type { ReactNode } from "react";

type ProductShellProps = {
  active: "charts" | "reports" | "compatibility";
  children: ReactNode;
};

const navItems = [
  { key: "charts", href: "/", label: "Карты" },
  { key: "reports", href: "/reports", label: "Личные обзоры" },
  { key: "compatibility", href: "/compatibility", label: "Совместимость" },
] as const;

export function ProductShell({ active, children }: ProductShellProps) {
  return (
    <main className="product-app">
      <aside className="product-sidebar">
        <div className="mark">Ом</div>
        <div>
          <h1>Jyotish Agent</h1>
          <p>Карты, обзоры, диалоги</p>
        </div>
        <nav aria-label="Основная навигация">
          {navItems.map((item) => (
            <Link href={item.href} key={item.key} className={active === item.key ? "active" : ""}>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="product-sidebar-note">
          <strong>Архитектура</strong>
          <span>Один API истории для web, Telegram и мобильного приложения.</span>
        </div>
      </aside>
      <section className="product-main">{children}</section>
    </main>
  );
}
