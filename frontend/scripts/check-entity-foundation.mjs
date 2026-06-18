import { readFileSync } from "node:fs";

const files = {
  core: "src/astrology/entities/core.ts",
  chip: "src/ui/components/EntityChip.tsx",
  inspector: "src/ui/components/EntityInspector.tsx",
  chartDetail: "src/app/charts/[id]/page.tsx",
  sources: "src/app/sources/page.tsx",
};

const source = Object.fromEntries(
  Object.entries(files).map(([key, path]) => [key, readFileSync(path, "utf8")]),
);

const failures = [];

function assert(condition, message) {
  if (!condition) failures.push(message);
}

for (const id of ["varga.D1", "varga.D9", "varga.D10", "varga.D60"]) {
  assert(source.core.includes(`["${id}"`), `Core registry missing ${id}`);
}

for (const [name, content] of Object.entries(source)) {
  for (const forbidden of ["source.pending", "not registered", "Block is not registered yet"]) {
    assert(!content.includes(forbidden), `${name} contains forbidden marker: ${forbidden}`);
  }
}

assert(source.chip.includes("getEntity(entityId)"), "EntityChip must read label from registry");
assert(!source.chip.includes("D9 отвечает") && !source.chip.includes("карта брака"), "EntityChip must not hardcode D9 interpretation text");
assert(source.chip.includes("onSelect(entityId)"), "EntityChip click must call the shared entity selection handler");
assert(source.chip.includes("aria-label"), "EntityChip must expose an aria-label");
assert(source.chip.includes("<button") && source.chip.includes('type="button"'), "Clickable EntityChip must use button semantics");

assert(source.inspector.includes("registerCoreEntities()"), "EntityInspector must use the shared registry");
assert(source.inspector.includes("entityId: EntityId | null"), "EntityInspector must support empty state");
assert(source.inspector.includes("devMode") && source.inspector.includes("showSources"), "EntityInspector must hide internal sources unless devMode=true");
assert(source.inspector.includes("onClose"), "EntityInspector must support closing and clearing active entity");
assert(source.core.includes("При неточном времени рождения D60"), "D60 warning must be available through registry");

assert(source.chartDetail.includes("useState<EntityId | null>"), "Chart detail must keep one activeEntityId state");
assert(source.chartDetail.includes("onSelect={setActiveEntityId}"), "Chart detail EntityChip must open the shared inspector");
assert(source.chartDetail.includes("<EntityInspector") && source.chartDetail.includes("onClose={() => setActiveEntityId(null)}"), "Chart detail must render one closable EntityInspector");

assert(!source.sources.includes("redirect("), "/sources must not redirect to a legacy hash route");
assert(source.sources.includes('<ProductShell active="sources"'), "/sources must use the current product shell");

if (failures.length) {
  console.error("Entity foundation check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Entity foundation check passed.");
