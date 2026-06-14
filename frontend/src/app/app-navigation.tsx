"use client";

export type AppNavKey =
  | "charts"
  | "people"
  | "vargas"
  | "calculations"
  | "yogas"
  | "timeline"
  | "transits"
  | "muhurta"
  | "compatibility"
  | "interactions"
  | "reports"
  | "guidance"
  | "sources"
  | "accuracy"
  | "settings";

type AppNavItem = {
  homeHref: string;
  href: string;
  key: AppNavKey;
  label: string;
  shortLabel: string;
};

const navIconPaths: Record<AppNavKey, string[]> = {
  charts: ["M4 5.5h16v13H4z", "M4 12h16", "M12 5.5v13", "M4 5.5l8 6.5 8-6.5", "M4 18.5l8-6.5 8 6.5"],
  people: ["M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M16 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M3.5 20a4.5 4.5 0 0 1 9 0", "M11.5 20a4.5 4.5 0 0 1 9 0"],
  vargas: ["M5 4h14v14H5z", "M9 4v14", "M15 4v14", "M5 9h14", "M5 15h14"],
  calculations: ["M6 4h12v16H6z", "M9 8h6", "M9 12h6", "M9 16h3"],
  yogas: ["M12 3v18", "M3 12h18", "M5.6 5.6l12.8 12.8", "M18.4 5.6 5.6 18.4"],
  timeline: ["M5 5h14v14H5z", "M8 3v4", "M16 3v4", "M5 10h14", "M9 14h2", "M13 14h2"],
  transits: ["M12 4a8 8 0 1 0 8 8", "M20 4v6h-6", "M12 8v4l3 2"],
  muhurta: ["M5 5h14v14H5z", "M8 3v4", "M16 3v4", "M5 10h14", "M12 13v4", "M10 15h4"],
  compatibility: ["M8.5 5.5a4 4 0 0 1 3.5 2.1 4 4 0 0 1 7 2.7c0 4.2-7 8.2-7 8.2s-7-4-7-8.2a4 4 0 0 1 3.5-4.8z"],
  interactions: ["M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M16 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M3.5 20a4.5 4.5 0 0 1 9 0", "M11.5 20a4.5 4.5 0 0 1 9 0"],
  reports: ["M7 3h8l4 4v14H7z", "M15 3v5h5", "M10 12h6", "M10 16h6"],
  guidance: ["M12 3a7 7 0 0 0-4 12.75V19h8v-3.25A7 7 0 0 0 12 3z", "M9 22h6"],
  sources: ["M5 4h10a3 3 0 0 1 3 3v13H8a3 3 0 0 0-3 3z", "M5 4v19", "M9 8h5", "M9 12h5"],
  accuracy: ["M12 3l8 4v5c0 5-3.4 8-8 9-4.6-1-8-4-8-9V7z", "M8.5 12l2.3 2.3 4.7-5"],
  settings: ["M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z", "M12 3v3", "M12 18v3", "M3 12h3", "M18 12h3", "M5.6 5.6l2.1 2.1", "M16.3 16.3l2.1 2.1", "M18.4 5.6l-2.1 2.1", "M7.7 16.3l-2.1 2.1"],
};

export const appNavItems: AppNavItem[] = [
  { key: "charts", homeHref: "#chart", href: "/", label: "Карта", shortLabel: "К" },
  { key: "people", homeHref: "/people", href: "/people", label: "Люди", shortLabel: "Л" },
  { key: "vargas", homeHref: "/vargas", href: "/vargas", label: "D-карты", shortLabel: "D" },
  { key: "compatibility", homeHref: "/compatibility", href: "/compatibility", label: "Совместимость", shortLabel: "С" },
  { key: "interactions", homeHref: "/interactions", href: "/interactions", label: "Взаимодействия", shortLabel: "В" },
  { key: "calculations", homeHref: "/calculations", href: "/calculations", label: "Расчёты", shortLabel: "Р" },
  { key: "timeline", homeHref: "/dashas", href: "/dashas", label: "Даши", shortLabel: "Д" },
  { key: "transits", homeHref: "/transits", href: "/transits", label: "Транзиты", shortLabel: "Т" },
  { key: "muhurta", homeHref: "/muhurta", href: "/muhurta", label: "Мухурта", shortLabel: "М" },
  { key: "yogas", homeHref: "/yogas", href: "/yogas", label: "Йоги", shortLabel: "Й" },
  { key: "guidance", homeHref: "/guidance", href: "/guidance", label: "AI-разбор", shortLabel: "AI" },
  { key: "reports", homeHref: "/reports", href: "/reports", label: "Отчёты", shortLabel: "О" },
  { key: "sources", homeHref: "/sources", href: "/sources", label: "Источники", shortLabel: "И" },
  { key: "accuracy", homeHref: "/accuracy", href: "/accuracy", label: "Точность", shortLabel: "!" },
  { key: "settings", homeHref: "/settings", href: "/settings", label: "Настройки", shortLabel: "Н" },
];

type AppNavigationProps = {
  activeKey: AppNavKey;
  home?: boolean;
  onSelect?: (key: AppNavKey) => void;
};

export function AppNavigation({ activeKey, home = false, onSelect }: AppNavigationProps) {
  return (
    <nav aria-label="Основная навигация" className="app-nav">
      {appNavItems.map((item) => (
        <AppNavLink activeKey={activeKey} home={home} item={item} key={item.key} onSelect={onSelect} />
      ))}
    </nav>
  );
}

function AppNavLink({
  activeKey,
  home,
  item,
  onSelect,
}: {
  activeKey: AppNavKey;
  home: boolean;
  item: AppNavItem;
  onSelect?: (key: AppNavKey) => void;
}) {
  const href = home ? item.homeHref : item.href;
  const isLocalAnchor = href.startsWith("#");

  return (
    <a
      aria-current={activeKey === item.key ? "page" : undefined}
      className={activeKey === item.key ? "active" : ""}
      data-short-label={item.shortLabel}
      data-nav-key={item.key}
      href={href}
      onClick={() => {
        if (isLocalAnchor) onSelect?.(item.key);
      }}
    >
      <span aria-hidden="true" className="app-nav-icon" data-short-label={item.shortLabel}>
        <svg viewBox="0 0 24 24" focusable="false">
          {navIconPaths[item.key].map((path) => (
            <path d={path} key={path} />
          ))}
        </svg>
      </span>
      <span className="app-nav-label">{item.label}</span>
    </a>
  );
}
