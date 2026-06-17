"use client";

export type AppNavKey =
  | "charts"
  | "workbenchV2"
  | "aiV2"
  | "compareV2"
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

const icon = {
  chart: ["M4 5.5h16v13H4z", "M4 12h16", "M12 5.5v13", "M4 5.5l8 6.5 8-6.5", "M4 18.5l8-6.5 8 6.5"],
  people: ["M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M16 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M3.5 20a4.5 4.5 0 0 1 9 0", "M11.5 20a4.5 4.5 0 0 1 9 0"],
  table: ["M5 4h14v14H5z", "M9 4v14", "M15 4v14", "M5 9h14", "M5 15h14"],
  report: ["M7 3h8l4 4v14H7z", "M15 3v5h5", "M10 12h6", "M10 16h6"],
  heart: ["M8.5 5.5a4 4 0 0 1 3.5 2.1 4 4 0 0 1 7 2.7c0 4.2-7 8.2-7 8.2s-7-4-7-8.2a4 4 0 0 1 3.5-4.8z"],
  clock: ["M12 4a8 8 0 1 0 8 8", "M20 4v6h-6", "M12 8v4l3 2"],
  book: ["M5 4h10a3 3 0 0 1 3 3v13H8a3 3 0 0 0-3 3z", "M5 4v19", "M9 8h5", "M9 12h5"],
  settings: ["M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z", "M12 3v3", "M12 18v3", "M3 12h3", "M18 12h3", "M5.6 5.6l2.1 2.1", "M16.3 16.3l2.1 2.1", "M18.4 5.6l-2.1 2.1", "M7.7 16.3l-2.1 2.1"],
};

const navIconPaths: Record<AppNavKey, string[]> = {
  charts: icon.chart,
  workbenchV2: icon.chart,
  aiV2: icon.report,
  compareV2: icon.table,
  people: icon.people,
  vargas: icon.table,
  calculations: icon.report,
  yogas: icon.clock,
  timeline: icon.clock,
  transits: icon.clock,
  muhurta: icon.clock,
  compatibility: icon.heart,
  interactions: icon.people,
  reports: icon.report,
  guidance: icon.report,
  sources: icon.book,
  accuracy: icon.report,
  settings: icon.settings,
};

export const appNavItems: AppNavItem[] = [
  { key: "charts", homeHref: "#chart", href: "/charts", label: "РљР°СЂС‚С‹", shortLabel: "РљР°СЂС‚С‹" },
  { key: "workbenchV2", homeHref: "/workbench-v2", href: "/workbench-v2", label: "Workbench v2", shortLabel: "WB2" },
  { key: "aiV2", homeHref: "/ai-v2", href: "/ai-v2", label: "AI v2", shortLabel: "AI2" },
  { key: "compareV2", homeHref: "/compare-v2", href: "/compare-v2", label: "Compare v2", shortLabel: "CMP" },
  { key: "people", homeHref: "/people", href: "/people", label: "Р›СЋРґРё", shortLabel: "Р›СЋРґРё" },
  { key: "reports", homeHref: "/reports", href: "/reports", label: "РћР±Р·РѕСЂС‹", shortLabel: "РћР±Р·." },
  { key: "compatibility", homeHref: "/compatibility", href: "/compatibility", label: "РЎРѕРІРјРµСЃС‚РёРјРѕСЃС‚СЊ", shortLabel: "РЎРѕРІРј." },
  { key: "interactions", homeHref: "/interactions", href: "/interactions", label: "Р’Р·Р°РёРјРѕРґРµР№СЃС‚РІРёСЏ", shortLabel: "РЎРІСЏР·Рё" },
  { key: "transits", homeHref: "/transits", href: "/transits", label: "РўСЂР°РЅР·РёС‚С‹", shortLabel: "РўСЂР°РЅР·." },
  { key: "sources", homeHref: "/sources", href: "/sources", label: "РСЃС‚РѕС‡РЅРёРєРё", shortLabel: "РСЃС‚." },
  { key: "settings", homeHref: "/settings", href: "/settings", label: "РќР°СЃС‚СЂРѕР№РєРё", shortLabel: "РќР°СЃС‚СЂ." },
];

type AppNavigationProps = {
  activeKey: AppNavKey;
  home?: boolean;
  onSelect?: (key: AppNavKey) => void;
};

export function AppNavigation({ activeKey, home = false, onSelect }: AppNavigationProps) {
  return (
    <nav aria-label="РћСЃРЅРѕРІРЅР°СЏ РЅР°РІРёРіР°С†РёСЏ" className="app-nav">
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
      <span className="app-nav-label" data-short-label={item.shortLabel}>
        {item.label}
      </span>
    </a>
  );
}
