import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const failures = [];
function assert(condition, message) {
  if (!condition) failures.push(message);
}

const page = read("src/app/transits/page.tsx");
const api = read("src/lib/api.ts");
const nav = read("src/app/app-navigation.tsx");

assert(page.includes('<ProductShell active="transits"'), "/transits must use shared ProductShell with active transits");
assert(!page.includes("PrivateHistoryPage"), "/transits must not be the old history page");
assert(page.includes("listChartProfiles"), "/transits must load saved charts");
assert(page.includes("fetchTransitWorkbench"), "/transits must load the transit workbench API");
assert(page.includes("D1ChartWorkbench"), "/transits must reuse existing D1/Chart Workbench renderer");
assert(!page.includes("TransitNorthChart") && !page.includes("TransitSouthChart"), "/transits must not define transit-specific chart renderers");
assert(page.includes("Натальная карта") && page.includes("Дата") && page.includes("Время") && page.includes("Часовой пояс") && page.includes("Место"), "/transits must expose moment controls");
assert(page.includes("Сейчас") && page.includes("Применить") && page.includes("Вернуться к текущему моменту"), "/transits must expose now/apply/current actions");
assert(page.includes("Стиль: Северный / Южный") && page.includes("Режим: Новичок / Астролог"), "/transits must expose chart style and mode affordances");
assert(page.includes("Термины: RU / EN / SA / Кратко"), "/transits must expose terminology modes");
assert(page.includes("Транзитная карта D1: факты без прогнозов и AI; аспекты выключены по умолчанию."), "/transits must state factual-only scope");
assert(page.includes("Только транзиты") && page.includes("Натал + транзиты") && page.includes("Две карты рядом"), "/transits must expose overlay view modes");
assert(page.includes("Легенда:") && page.includes("один EntityInspector"), "/transits must expose overlay legend and single inspector contract");
assert(page.includes("Граха-дришти") && page.includes("Показать аспекты"), "/transits must expose an astrologer-only graha drishti toggle");
assert(page.includes("aspectLayer") && page.includes("sampleRefs"), "/transits must render aspect list from safe backend refs");
assert(page.includes("enabledByDefault") && page.includes("availableInModes"), "/transits must keep aspect layer off by default and astrologer-only");
assert(page.includes("rashiAspectLayer") && page.includes("showRashiDrishti"), "/transits must expose an astrologer-only rashi drishti toggle");
assert(page.includes("aspect.rashi_drishti.parashara.v1"), "/transits must keep Rashi Drishti separate from Graha Drishti");
assert(page.includes('type DisplayMode = "novice" | "astrologer"'), "/transits must define a real display mode type");
assert(page.includes('useState<DisplayMode>("novice")'), "/transits must default display mode to novice");
assert(page.includes('canShowGrahaDrishti'), "Graha Drishti must be gated by astrologer display mode");
assert(page.includes('canShowRashiDrishti'), "Rashi Drishti must be gated by astrologer display mode");
assert(page.includes('displayMode === "astrologer" && Boolean(aspectLayer?.availableInModes?.includes("astrologer"))'), "Graha Drishti gate must require current astrologer mode");
assert(page.includes('displayMode === "astrologer" && Boolean(rashiAspectLayer?.availableInModes?.includes("astrologer"))'), "Rashi Drishti gate must require current astrologer mode");
assert(page.includes("{canShowGrahaDrishti && aspectLayer ? ("), "Graha Drishti render condition must use the mode gate");
assert(page.includes("{canShowRashiDrishti && rashiAspectLayer ? ("), "Rashi Drishti render condition must use the mode gate");
assert(page.includes('aria-label="Режим отображения"'), "/transits mode switch must expose a readable UTF-8 aria label");
assert(!page.includes("Р РµР¶РёРј РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ"), "/transits mode switch must not contain mojibake");
assert(page.includes('onClick={() => switchDisplayMode("novice")}') && page.includes('onClick={() => switchDisplayMode("astrologer")}'), "/transits must expose novice/astrologer mode controls through switchDisplayMode");
assert(!page.includes("sourceRuleIds.map") && !page.includes("sourceRuleIds.join"), "/transits normal UI must not render raw Rashi Drishti source IDs");
assert(page.includes("displayAspectRef(item.sourceEntityRef)") && page.includes("displayAspectRef(item.targetEntityRef)") && page.includes("displayAspectKind(item.aspectKind)"), "/transits must render Rashi Drishti refs and kinds as human-readable labels");
assert(!page.includes("{item.aspectKind}") || page.indexOf("{item.aspectKind}") < page.indexOf("Rashi Drishti aspect layer"), "/transits normal Rashi Drishti UI must not render raw aspectKind IDs");
assert(api.includes("fetchTransitWorkbench") && api.includes("/api/charts/${profileId}/transit-workbench"), "API client must expose chart-scoped transit workbench fetch");
assert(nav.includes("/transits"), "shared nav must include transits route");
for (const forbidden of ["Спросить AI", "Сгенерировать", "source.pending", "rawEvidence", "eligibleItems", "Missing calculations"]) {
  assert(!page.includes(forbidden), `/transits leaks forbidden marker: ${forbidden}`);
}

if (failures.length) {
  console.error("Transit workbench check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Transit workbench check passed.");
