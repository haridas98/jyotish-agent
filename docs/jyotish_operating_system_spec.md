# Jyotish Agent: операционная система для джйотиша

Этот документ фиксирует продуктовую и техническую архитектуру, чтобы UI больше не превращался ни в свалку блоков, ни в пустой минимализм.

## Главный принцип

Приложение строится как астрологический рабочий стол:

```text
Calculation Layer -> Entity Registry -> UI Layer -> EntityInspector -> Interpretation/AI Layer
```

Разделение обязанностей:

- `Calculation Layer`: только расчеты, без толкований.
- `Entity Registry`: единые сущности джйотиша.
- `UI Layer`: только отображение, layout, переключатели, таблицы.
- `Interpretation/AI Layer`: объяснения, источники, шастрические правила, синтез.

Запрещено писать астрологические толкования прямо внутри React-компонентов.

## EntityId

Любой астрологический объект в UI должен ссылаться на `entityId`.

Обязательные типы:

```text
graha.SU
graha.MO
house.1 ... house.12
rashi.Aries ... rashi.Pisces
nakshatra.Bharani
varga.D1
varga.D9
varga.D10
varga.D12
varga.D60
placement.SU.house.10
placement.MO.house.12
dasha.vimshottari.JU.MO
yoga.*
relationship.father_child
relationship.business_partner
```

Правильно:

```tsx
<EntityLink entityId="varga.D9" />
<EntityLink entityId="graha.SU" />
<InterpretationCard entityId="placement.SU.house.10" />
```

Неправильно:

```tsx
<p>D9 отвечает за брак...</p>
<p>Солнце в 10 доме дает...</p>
```

## Рабочее состояние

Интерфейс должен строиться от единого состояния:

```json
{
  "activeProfileId": "profile.haridev",
  "activeChartId": "chart.birth",
  "activeVarga": "D1",
  "activeReferencePoint": "lagna",
  "activeDisplayLayers": {
    "degrees": true,
    "nakshatras": true,
    "aspects": false,
    "argala": false,
    "specialStatuses": true
  },
  "activeClickMode": "explain",
  "activeEntityId": "placement.SU.house.10"
}
```

## App Shell

Desktop:

```text
TopBar
Left navigation
Main content
Right EntityInspector
```

Mobile:

```text
TopBar
Main content
Bottom navigation
EntityInspector as bottom sheet
```

TopBar:

- логотип;
- поиск / command palette;
- текущий профиль;
- режим: простой / астролог;
- язык терминов;
- стиль карты;
- настройки;
- сохранить / поделиться.

## Страницы

Полная структура:

```text
/                         Главная
/today                    Сегодня / панчанга
/chart/new                Создать карту
/chart/:id                Рабочий стол карты
/chart/:id/edit           Данные и расчетный пресет карты
/profiles                 Профили
/profiles/:id             Карточка профиля
/relations                Связи между профилями
/compare                  Сравнить карты
/compare/:id              Анализ взаимодействия
/ai                       ИИ-анализ
/reports                  Отчеты / экспорт
/library                  Шастры, правила, источники
/settings                 Настройки
/dev                      Debug / raw calculations / Graphify
```

MVP:

```text
/
/chart/new
/chart/:id
/profiles
/relations
/compare
/ai
/settings
```

## Главная `/`

Главная - вход, не рабочий стол.

Показывает:

- быстрый ввод даты, времени, места, пола;
- кнопку расчета;
- переход к профилям;
- переход к сравнению;
- сегодняшнюю панчангу;
- текущую карту неба в компактном виде.

Не показывает:

- все D-карты;
- шадбалу;
- большие таблицы;
- длинные объяснения;
- экспертные настройки.

## `/chart/new`

Wizard, а не огромная форма.

Шаги:

1. Основные данные: имя, пол, дата, время, точность времени.
2. Место рождения: город, координаты, timezone, DST.
3. Расчетный пресет: стандартный или экспертный.
4. Сохранение: личный профиль, родственник, клиент, бизнес-контакт, не сохранять.
5. Итог: открыть карту, сравнить, спросить ИИ.

Если время неизвестно, показывать предупреждение:

```text
Без точного времени лагна, дома, варги и точные периоды могут быть ненадежны.
```

## `/chart/:id`

Главный рабочий стол карты.

Header:

- имя профиля;
- дата, время, место;
- лагна, луна, текущая даша;
- сохранить;
- редактировать;
- сравнить;
- спросить ИИ;
- экспорт.

Центральная область:

- карта;
- `VargaSelector`;
- `ChartToolbar`;
- таблицы выбранной вкладки.

Правая область:

- единый `EntityInspector`.

Нижние / внутренние вкладки:

```text
Overview
Grahas
Bhavas
Vargas
Nakshatra
Panchanga
Dashas
Yogas
Strengths
Ashtakavarga
Transits
Notes
Sources
```

## ChartToolbar

Один общий toolbar для всех карт.

Содержит:

- стиль карты: северный / южный / круговой;
- varga selector: D1, D9, D10, D12, D7, D3, D20, D60;
- точка отсчета: Lagna, Moon, Sun, Arudha, выбранный знак;
- режим клика: объяснить, аспекты, аргала, сделать первым домом, заметка;
- слои отображения.

Слои:

```text
planets
degrees
houses
signs
nakshatras
padas
dignities
retrograde
combustion
special statuses
aspects
argala
arudhas
upagrahas
outer planets
```

## EntityInspector

Один инспектор на все приложение.

Открывается по клику на:

- граху;
- дом;
- знак;
- накшатру;
- варгу;
- йогу;
- дашу;
- значение в таблице.

Вкладки:

```text
General
In this chart
Calculation
Sources
Related
Actions
```

Пример для `placement.SU.house.10`:

- что такое Сурья;
- что такое 10 дом;
- что значит Сурья в 10 доме в этой карте;
- знак, градус, накшатра, статус;
- расчетные основания;
- источники;
- действия: показать в D10, подсветить аспекты, спросить ИИ, добавить заметку.

## Режимы

### Простой режим

Показывает:

- D1;
- ключевые планеты;
- текущий период;
- простые объяснения;
- сферы жизни;
- предупреждения о неточном времени;
- кнопку ИИ.

Скрывает:

- Shad Bala;
- Vimshopaka Bala;
- Upagrahas;
- Sphutas;
- D60 без предупреждения;
- сложные даши;
- raw JSON;
- спорные техники.

### Режим астролога

Показывает:

- все вкладки;
- varga selector;
- dasha selector;
- силы;
- йоги;
- аштакаваргу;
- аргала;
- арудхи;
- специальные лагны;
- технические предупреждения;
- sourceId / ruleId.

### Плотность

Отдельная настройка:

```text
Комфортная
Обычная
Плотная
```

## Настройки

Настройки разделяются строго.

### `/settings`

Глобальные настройки:

- язык интерфейса;
- язык терминов;
- стиль карты по умолчанию;
- айанамша;
- true/mean nodes;
- система домов;
- режим по умолчанию;
- приватность;
- AI settings.

### `/chart/:id/edit`

Настройки конкретной карты:

- исходные данные рождения;
- точность времени;
- координаты;
- timezone / DST;
- расчетный пресет карты.

### ChartToolbar

Временные настройки отображения:

- градусы;
- накшатры;
- аспекты;
- аргала;
- стиль карты;
- точка отсчета.

Они не меняют расчет.

## Сравнение и связи

Сравнение - не только брак.

Типы связей:

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

Каждый тип связи должен определять:

- важные дома;
- караки;
- варги;
- правила сравнения;
- что показывать в AI-контексте.

Экран сравнения:

- профиль A;
- профиль B;
- тип связи;
- side-by-side charts;
- overlay A -> B;
- overlay B -> A;
- даши обоих;
- транзиты обоих;
- role-specific houses;
- AI-анализ с evidence.

## Library

Библиотека хранит:

- шастры;
- правила;
- сущности;
- толкования;
- йоги;
- даши;
- варги;
- накшатры.

ИИ должен ссылаться на:

```text
sourceId + ruleId + entityId + calculation evidence
```

## Dev

Только для разработчика:

- raw chart JSON;
- calculation trace;
- entity IDs;
- rule IDs;
- source IDs;
- Graphify dependency map;
- duplicate interpretation detector;
- hardcoded interpretation detector.

## Reusable components

```text
AppShell
TopBar
Sidebar
InspectorShell
ChartCanvas
NorthChart
SouthChart
VargaSelector
ChartToolbar
ChartCell
PlanetGlyph
AspectOverlay
ArgalaOverlay
EntityLink
EntityCard
EntityInspector
EntityTooltip
EntityBreadcrumbs
GrahaTable
BhavaTable
VargaTable
DashaTable
YogaTable
StrengthTable
AshtakavargaTable
ProfileCard
RelationshipEditor
AiPanel
AiEvidenceBlock
AiSourceBlock
```

## Запреты

- Не создавать новые описания D9, D60, graha, house, rashi внутри UI.
- Не добавлять новую вкладку, если такая тема уже есть.
- Не дублировать `VargaSelector`.
- Не смешивать настройки расчета и настройки отображения.
- Не делать AI-анализ на основе текста UI.
- Не удалять старый блок ради минимализма без миграции в правильную вкладку.

## Definition of Done

1. D9 description exists in one registry entry.
2. D60 description exists in one registry entry.
3. Every chart object is clickable.
4. EntityInspector is reused everywhere.
5. Simple mode hides advanced details.
6. Astrologer mode shows expert tables.
7. Calculation settings and display settings are separated.
8. AI receives structured calculation context, not UI text.
9. No copyrighted third-party interpretation text is copied.
10. Existing calculations are moved into correct tabs, not deleted.

## Порядок работ

Не начинать с удаления дублей. Сначала создать модульные контракты, потом мигрировать старые блоки.

1. Зафиксировать `Calculation Registry`.
2. Зафиксировать `Block Registry`.
3. Зафиксировать `Layout Manifests`.
4. Создать `Entity Registry`.
5. Создать `Interpretation Registry`.
6. Создать единый `EntityInspector`.
7. Обернуть существующие вычисления в `CalculationModule` adapters.
8. Подключить старые UI-компоненты как временные `ViewBlock`.
9. Собрать `Chart Workbench` через manifest.
10. Переносить старые блоки по одному.
11. После стабилизации одной карты делать сравнение и связи.

Подробный план модульного конструктора: `docs/jyotish_modular_workbench_plan.md`.
