# Modular Jyotish Workbench Plan

Цель: строить проект как джйотиш-конструктор внутри одного приложения, не как набор вручную собранных страниц. Это не микросервисы. Это модули с жесткими контрактами.

## Главная формула

```text
Birth data
  -> Calculation Pipeline
  -> Normalized Chart Model
  -> Calculation Registry
  -> Entity Registry
  -> Block Registry
  -> Layout Manifest
  -> EntityInspector
  -> AI Evidence
```

Нельзя начинать с “найти дубли и удалить”. Это симптом. Правильный порядок:

1. Зафиксировать типы и контракты.
2. Создать `Calculation Registry`.
3. Создать `Block Registry`.
4. Создать `Layout Manifests`.
5. Подключить существующие вычисления через adapters.
6. Подключить старые UI-компоненты как legacy blocks.
7. После миграции удалить дубли.

## 5 типов модулей

```text
Calculation Modules      только считают
Entity Modules           описывают сущности
View Blocks              только отображают
Interpretation Modules   дают объяснения и источники
AI Evidence Modules      собирают structured evidence для ИИ
```

## Calculation Registry

Каждый расчет получает контракт:

```ts
export interface CalculationModule<TOutput> {
  id: CalculationId;
  label: string;
  dependsOn: CalculationId[];
  compute: (ctx: CalculationContext, deps: CalculationStore) => TOutput;
  validate?: (output: TOutput) => ValidationResult;
}
```

Примеры:

```text
calc.birthData
calc.geo
calc.ayanamsha
calc.planetPositions
calc.houses
calc.nakshatras
calc.panchanga
calc.varga.D1
calc.varga.D9
calc.varga.D10
calc.varga.D12
calc.varga.D60
calc.vimshottari
calc.shadBala
calc.ashtakavarga
calc.yogas
calc.arudhas
calc.argala
calc.grahaDrishti
calc.rashiDrishti
calc.transits
```

Расчеты зависят друг от друга как DAG:

```text
birth data
  -> geo/timezone
  -> planet positions
  -> signs/houses/nakshatras
  -> vargas/dashas/yogas/strengths
```

## Normalized Chart Model

UI должен читать только нормализованный результат:

```ts
export interface ChartCalculationResult {
  chartId: string;
  birthData: BirthData;
  calculationPreset: CalculationPreset;
  grahas: Record<GrahaId, GrahaPosition>;
  houses: Record<HouseId, HouseData>;
  nakshatras: Record<GrahaId, NakshatraPlacement>;
  vargas: Partial<Record<VargaId, VargaChart>>;
  dashas: Partial<Record<DashaSystemId, DashaTree>>;
  strengths?: StrengthsResult;
  yogas?: YogaResult[];
  ashtakavarga?: AshtakavargaResult;
  panchanga?: PanchangaResult;
  warnings: CalculationWarning[];
}
```

UI не должен тянуть вычисления из разных файлов напрямую.

## Block Registry

Каждый UI-блок получает контракт:

```ts
export interface ViewBlock {
  id: string;
  title: string;
  requires: CalculationId[];
  supportedModes: Array<"simple" | "expert">;
  allowedRegions: Array<"header" | "sidebar" | "main" | "bottom" | "inspector">;
  component: React.ComponentType<ViewBlockProps>;
}
```

Примеры:

```text
block.chart.main
block.chart.vargaSelector
block.chart.toolbar
block.chart.vargaGrid
block.table.grahas
block.table.bhavas
block.table.dashas
block.table.yogas
block.table.strengths
block.panel.currentDasha
block.panel.panchanga
block.panel.entityInspector
block.panel.aiQuestion
block.compare.sideBySideCharts
block.compare.overlay
block.compare.roleFactors
block.compare.dualDashas
block.compare.aiEvidence
```

## Layout Manifests

Страницы собираются из блоков.

Простой режим карты:

```ts
export const chartSimpleLayout = {
  page: "chartWorkbench",
  mode: "simple",
  regions: {
    header: ["block.profileHeader", "block.modeSwitcher"],
    main: ["block.chart.main", "block.panel.simpleSummary", "block.panel.currentDasha"],
    bottom: ["block.table.grahas.simple", "block.table.bhavas.simple"],
    inspector: ["block.panel.entityInspector"]
  }
};
```

Режим астролога:

```ts
export const chartExpertLayout = {
  page: "chartWorkbench",
  mode: "expert",
  regions: {
    header: ["block.profileHeader", "block.chartToolbar", "block.calculationPresetBadge"],
    sidebar: ["nav.overview", "nav.grahas", "nav.bhavas", "nav.vargas", "nav.dashas", "nav.yogas", "nav.strengths", "nav.transits"],
    main: ["block.chart.main", "block.chart.vargaSelector", "block.chart.displayLayerToggles"],
    bottom: ["block.table.grahas", "block.table.bhavas", "block.table.dashas"],
    inspector: ["block.panel.entityInspector"]
  }
};
```

## D9/D60 правило

Неправильно:

```text
D9 на странице брака
D9 на странице семьи
D9 на странице духовности
разные тексты в разных местах
```

Правильно:

```text
calc.varga.D9              расчет
entity.varga.D9            сущность
block.varga.chart          отображение
EntityInspector(D9)        объяснение
AiEvidence(varga.D9)       основание для ИИ
```

Контекст добавляется отдельно:

```text
entity.varga.D9 + context.relationship.spouse
entity.varga.D9 + context.planetStrength
entity.varga.D9 + context.dharma
```

Одна сущность, разные контексты.

## Relationship Recipes

Сравнение карт тоже собирается через рецепты, а не через отдельные страницы под каждый случай.

```ts
export interface RelationshipRecipe {
  id: RelationshipType;
  label: string;
  profileAFactors: RelationshipFactorDefinition[];
  profileBFactors: RelationshipFactorDefinition[];
  sharedFactors: RelationshipFactorDefinition[];
  requiredVargas: VargaId[];
  requiredDashas: DashaSystemId[];
  defaultBlocks: string[];
}
```

Пример типов:

```text
father_child
mother_child
siblings
spouse
business_partner
boss_subordinate
colleague
guru_student
custom
```

## AI Evidence Pack

ИИ получает structured evidence, а не текст интерфейса.

```ts
export interface AiEvidencePack {
  subject: "single_chart" | "relationship" | "period" | "event";
  profiles: string[];
  question: string;
  calculationPreset: CalculationPreset;
  factors: AiFactor[];
  warnings: CalculationWarning[];
  sourceRules: SourceRuleRef[];
}
```

Фактор:

```ts
export interface AiFactor {
  entityId: string;
  calcId: CalculationId;
  value: unknown;
  relevance: "primary" | "secondary" | "supporting" | "contradicting";
  reason: string;
  sourceRuleIds?: string[];
}
```

## Миграция без разрушения

1. Заморозить формулы.
2. Сделать golden snapshot для карты:

```text
30.04.1998
13:45
Sterlitamak
UTC +06:00
```

3. Сохранить эталон:

```text
fixtures/haridev.chart.snapshot.json
```

4. Сделать тест: если D1/D9/D60/дашии изменились без причины, тест падает.
5. Обернуть существующие расчеты в `CalculationModule` adapters.
6. Подключить старые UI-компоненты как временные `ViewBlock`.
7. Собрать новую страницу за feature flag:

```text
/chart/:id?layout=v2
```

8. Переносить по одному:

```text
Header
Main chart
Varga selector
Graha table
Bhava table
Dasha panel
EntityInspector
Vargas tab
Yogas tab
Compare module
```

## Файловая структура

```text
src/
  astrology/
    calculations/
      registry.ts
      pipeline.ts
      modules/
    entities/
      registry.ts
      grahas.ts
      rashis.ts
      houses.ts
      nakshatras.ts
      vargas.ts
      dashas.ts
      yogas.ts
      relationships.ts
    interpretations/
      registry.ts
    ai/
      evidence/
      prompts/
      schemas.ts
  ui/
    blocks/
      registry.ts
    layouts/
      chart.simple.ts
      chart.expert.ts
      compare.fatherChild.ts
      compare.businessPartner.ts
    components/
      EntityLink.tsx
      EntityInspector.tsx
      EntityCard.tsx
      ChartRenderer.tsx
```

## Definition of Done

- D9 считается через `calc.varga.D9`.
- D9 отображается через view blocks.
- D9 объясняется через `entity.varga.D9`.
- D9 не имеет текстовых описаний внутри React-компонентов.
- То же правило действует для D60, D10, D12, grahas, houses, nakshatras, dashas и yogas.
- Страницы собираются через layout manifests.
- Старые блоки мигрируются, а не удаляются вслепую.
- Расчеты защищены snapshot-тестами.

