"use client";

export type AppNavKey =
  | "charts"
  | "vargas"
  | "calculations"
  | "yogas"
  | "timeline"
  | "transits"
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

export const appNavItems: AppNavItem[] = [
  { key: "charts", homeHref: "#chart", href: "/", label: "Карта", shortLabel: "К" },
  { key: "vargas", homeHref: "#varga-charts", href: "/#varga-charts", label: "D-карты", shortLabel: "D" },
  { key: "compatibility", homeHref: "/compatibility", href: "/compatibility", label: "Совместимость", shortLabel: "С" },
  { key: "interactions", homeHref: "/interactions", href: "/interactions", label: "Взаимодействия", shortLabel: "В" },
  { key: "calculations", homeHref: "#reports", href: "/?analysis=calculations#reports", label: "Расчёты", shortLabel: "Р" },
  { key: "timeline", homeHref: "#reports", href: "/?analysis=timeline#reports", label: "Даши", shortLabel: "Д" },
  { key: "transits", homeHref: "#reports", href: "/?analysis=transits#reports", label: "Транзиты", shortLabel: "Т" },
  { key: "yogas", homeHref: "#reports", href: "/?analysis=yogas#reports", label: "Йоги", shortLabel: "Й" },
  { key: "reports", homeHref: "/reports", href: "/reports", label: "Отчёты", shortLabel: "О" },
  { key: "sources", homeHref: "#reports", href: "/?analysis=sources#reports", label: "Источники", shortLabel: "И" },
  { key: "accuracy", homeHref: "#reports", href: "/?analysis=accuracy#reports", label: "Точность", shortLabel: "!" },
  { key: "settings", homeHref: "#display-settings", href: "/#display-settings", label: "Настройки", shortLabel: "Н" },
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
  return (
    <a
      aria-current={activeKey === item.key ? "page" : undefined}
      className={activeKey === item.key ? "active" : ""}
      data-short-label={item.shortLabel}
      data-nav-key={item.key}
      href={home ? item.homeHref : item.href}
      onClick={() => onSelect?.(item.key)}
    >
      <span aria-hidden="true" className="app-nav-icon" data-short-label={item.shortLabel} />
      <span className="app-nav-label">{item.label}</span>
    </a>
  );
}
