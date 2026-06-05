# Jyotish Agent Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Построить веб-сервис джйотиша: точные расчеты, функциональная совместимость с Jagannatha Hora, авторитетные ссылки на шастры и труды Шрилы Прабхупады, гаудия-вайшнавская логика рекомендаций.

**Architecture:** Отдельный проект `C:\Projects\jyotish-agent`: Next.js frontend, Django/DRF backend, Postgres + pgvector, Redis/Celery для тяжелых отчетов. База `C:\Projects\vl` используется read-only как авторитетный корпус Прабхупады и вайшнавских текстов; тексты не дублируем без необходимости.

**Tech Stack:** Next.js, TypeScript, Django, DRF, PostgreSQL, pgvector, Redis, Celery, Swiss Ephemeris или другой лицензируемый эфемеридный слой, Playwright, pytest.

---

## 1. Как я понял задачу

Нужен не просто калькулятор гороскопа, а полноценная астрологическая платформа в духе ISKCON/гаудия-вайшнавской парампары.

Основной пользовательский сценарий:

1. Человек вводит дату, точное время и место рождения.
2. Система строит карту: планеты, дома, варги, накшатры, даши, йоги, транзиты и другие разделы уровня Jagannatha Hora.
3. Система дает полный разбор, но каждый важный вывод должен иметь источник: расчет, правило джйотиша, шастра, комментарий, лекция/письмо/книга Шрилы Прабхупады.
4. Если классическая астрология предлагает поклонение полубогу/граха-девате, сервис переводит это в гаудия-вайшнавскую рамку: прибежище Кришны, Харе Кришна маха-мантра, служение, чтение, садхана, пожертвование/пост/поклонение как зависимое от Кришны, без независимого полубожества.
5. Точность расчетов проверяется не словами, а тестами против JHora, эфемерид и эталонных карт.

Ограничение: JHora берем как функциональный эталон и источник сравнительных тестов. Код, закрытые таблицы и данные JHora не копируем и не декомпилируем. Расчеты реализуем сами по открытым алгоритмам, шастрам и лицензируемым эфемеридам.

## 2. Источники, которые уже надо учитывать

Публичные ориентиры:

- Jagannatha Hora: https://vedicastrologer.org/jh/
- Shyamasundara Dasa: https://shyamasundaradasa.com/
- Swiss Ephemeris: https://www.astro.com/swisseph/

Локальные ориентиры:

- `C:\Projects\INFRASTRUCTURE.md` - реестр портов, БД, правил.
- `C:\Projects\vl` - существующий проект с книгами, лекциями, письмами, шастрами, авторизацией и Postgres.
- `C:\Projects\vl\db\migrations` - структура `works`, `text_units`, `texts`, `search_documents`, `persons`, связи источников и ачарьев.

## 3. Ключевые решения

1. Backend: рекомендую Django/DRF, потому что для джйотиша удобнее Python-экосистема: эфемериды, timezone/geocoding, Celery, админка, ingest pipeline. Go можно оставить для отдельных быстрых сервисов позже, но стартовать быстрее на Django.
2. Frontend: Next.js, как в `vl`, чтобы использовать знакомые паттерны и не плодить лишнюю технологию UI.
3. БД: отдельный Postgres проекта `jyotish-agent`, плюс read-only подключение к VL Postgres.
4. Эфемериды: сначала юридический аудит лицензии. Если Swiss Ephemeris подходит по лицензии/покупке, используем ее. Если нет, проектируем адаптер, чтобы заменить на NASA/JPL/SPICE или другой источник.
5. Интерпретации: не генерировать свободно без источников. Сначала rule-based слой с цитатами, потом RAG только как вспомогательный поиск цитат, с обязательным provenance.

## 4. Этап 0 - границы, право, богословская политика

Цель: до кода зафиксировать, что именно можно считать, цитировать и рекомендовать.

Deliverables:

- `docs/product_scope.md` - список модулей: natal, varga, dasha, transit, muhurta, compatibility, prashna, yearly, remedial.
- `docs/source_policy.md` - какие тексты можно хранить, цитировать, показывать публично.
- `docs/vaishnava_interpretation_policy.md` - правила рекомендаций в линии ISKCON.
- `docs/jhora_parity_policy.md` - что значит "как JHora": функциональная совместимость, но без копирования кода.

Done:

- Есть список разрешенных источников.
- Есть запрет на независимое поклонение полубогам в рекомендациях.
- Есть формулировка, что сервис не дает медицинских, финансовых, юридических и фаталистичных гарантий.

## 5. Этап 1 - инвентаризация Jagannatha Hora

Цель: разобрать JHora как эталон функционала.

Работы:

- Скачать текущую версию JHora с официального сайта.
- Зафиксировать версию, дату скачивания, checksum.
- Сделать каталог экранов и функций.
- Составить матрицу функционала:
  - birth data input;
  - timezone/DST/place handling;
  - rashi chart;
  - bhava chart;
  - divisional charts D1-D60;
  - nakshatra/pada;
  - panchanga;
  - yogas;
  - bala;
  - ashtakavarga;
  - vimshottari and other dashas;
  - transits;
  - annual charts;
  - compatibility;
  - muhurta;
  - prashna;
  - reports/export.
- Сделать `docs/jhora_feature_matrix.md`.
- Сделать `docs/jhora_accuracy_test_suite.md`.

Done:

- У каждой функции есть статус: `must_have_mvp`, `phase_2`, `phase_3`, `research_only`.
- У каждой функции есть эталонные скриншоты/выгрузки JHora.
- Есть минимум 100 тестовых карт для сравнения.

## 6. Этап 2 - исследование точности

Цель: "сто раз проверить" превратить в воспроизводимую лабораторию точности.

Наборы тестов:

- 20 современных карт с точными timezone.
- 20 исторических карт до 1900 года.
- 20 карт рядом с DST-переходами.
- 20 карт рядом с границами знаков/накшатр/варг.
- 20 карт из публичных учебных примеров.
- 20 карт, вручную проверенных в JHora.

Метрики:

- долгота планет: допуск в arcseconds;
- lagna: допуск в arcseconds/minutes;
- nakshatra/pada: точное совпадение, boundary cases помечать отдельно;
- varga placements: точное совпадение;
- dasha start/end: допуск по времени, отдельно для разных ayanamsa;
- sunrise/tithi/yoga/karana: допуск по времени.

Артефакты:

- `tests/fixtures/charts/*.json`
- `tests/fixtures/jhora_exports/*.json`
- `backend/apps/calculations/tests/test_ephemeris_accuracy.py`
- `backend/apps/calculations/tests/test_jhora_parity.py`
- `backend/apps/calculations/tests/test_boundary_cases.py`

Done:

- CI показывает процент совпадений с JHora.
- Любое расхождение имеет причину: ayanamsa, house system, timezone, эфемериды, округление, баг.

## 7. Этап 3 - каркас приложения

Структура:

```text
C:\Projects\jyotish-agent\
  backend\
    manage.py
    config\
    apps\
      accounts\
      places\
      calculations\
      charts\
      sources\
      interpretations\
      reports\
      vl_integration\
  frontend\
    src\
      app\
      components\
      lib\
  db\
    migrations\
  docs\
  tests\
  docker-compose.yml
  .env.example
```

Работы:

- Поднять Django + DRF.
- Поднять Next.js frontend.
- Поднять Postgres + Redis через Docker Compose.
- Настроить `.env.example`, реальные ключи держать только в `.env`.
- Настроить pytest, eslint/typecheck, Playwright.
- Настроить health endpoints:
  - `/api/health`;
  - `/api/health/db`;
  - `/api/health/vl`.

Done:

- `docker compose up` поднимает локальную систему.
- Есть регистрация/логин.
- Backend видит свою БД.
- Backend умеет read-only проверить связь с VL DB.

## 8. Этап 4 - модель данных

Основные таблицы:

- `birth_profiles` - дата, время, место, timezone, точность времени, владелец.
- `places` - geoname/osm id, координаты, timezone, история.
- `chart_calculations` - версия алгоритма, ayanamsa, house system, исходные параметры.
- `planet_positions` - graha, longitude, latitude, speed, rashi, nakshatra, pada.
- `house_positions` - cusps, bhavas, lagna.
- `varga_charts` - D1-D60 placements.
- `dasha_periods` - система, levels, start/end.
- `yogas` - найденные йоги, условия, confidence.
- `source_works` - джйотиш-источники.
- `source_passages` - точные места в источниках.
- `interpretation_rules` - правило, условие, приоритет, источник.
- `interpretation_blocks` - готовые блоки отчета.
- `remedy_policies` - вайшнавское преобразование remedial-рекомендаций.
- `vl_citation_links` - ссылки на `C:\Projects\vl` works/text_units/texts.
- `report_jobs` - генерация длинных отчетов.
- `accuracy_runs` - сравнение с JHora/эфемеридами.

Done:

- Миграции применяются с нуля.
- В админке видно карты, источники, правила, отчеты, тестовые прогоны.
- Чувствительные данные рождения защищены правами доступа.

## 9. Этап 5 - расчетное ядро

Минимальный порядок реализации:

1. Julian day, timezone, UTC conversion.
2. Геокодинг и timezone по месту.
3. Graha longitudes.
4. Ayanamsa variants.
5. Lagna and houses.
6. Rashi/nakshatra/pada.
7. Panchanga: tithi, vara, nakshatra, yoga, karana.
8. Vargas D1-D60.
9. Vimshottari dasha.
10. Основные yogas.
11. Ashtakavarga.
12. Shadbala.
13. Дополнительные dasha systems.
14. Transit engine.
15. Muhurta/prashna/compatibility.

Техническое правило:

- Все вычисления чистые и версионированные.
- Каждый результат хранит `calculation_version`.
- Любой boundary case получает флаг `near_boundary`.

Done:

- По каждой группе есть unit tests.
- По каждой группе есть comparison tests против JHora.

## 10. Этап 6 - корпус джйотиш-шастр

Кандидаты на корпус:

- Brihat Parashara Hora Shastra.
- Brihat Jataka.
- Saravali.
- Phaladeepika.
- Jataka Parijata.
- Uttara Kalamrita.
- Jaimini Sutras.
- Brihat Samhita.
- Prashna Marga.
- Muhurta Chintamani.
- Книги/курсы/ссылки, которые Shyamasundara Dasa сам указывает на своем сайте.

Важно:

- Сначала проверить права и качество издания.
- Сырые импорты держать скрытыми.
- Каждый passage должен иметь work, chapter, verse/section, language, edition, source_url/source_file, review_status.

Done:

- Есть минимум один проверенный источник для каждого типа интерпретации.
- Непроверенные источники не используются в публичном отчете.

## 11. Этап 7 - интеграция с VL и Прабхупадой

Цель: использовать существующую БД `C:\Projects\vl`, не изобретая заново библиотеку Прабхупады.

Работы:

- Прочитать реальные `.env` только на этапе подключения.
- Сделать read-only DB user для jyotish-agent.
- Сделать слой `vl_integration`:
  - поиск по `works`;
  - поиск по `text_units`;
  - поиск по `texts`;
  - поиск по `search_documents`;
  - сбор URL маршрутов VL.
- Добавить whitelist цитат:
  - Bhagavad-gita;
  - Srimad-Bhagavatam;
  - Caitanya-caritamrita;
  - лекции;
  - письма;
  - беседы.
- Добавить тематические индексы:
  - karma;
  - destiny/free will;
  - demigod worship;
  - surrender to Krishna;
  - chanting;
  - astrology references;
  - auspiciousness;
  - devotional remedies.

Done:

- Отчет может вставить ссылку на конкретное место в VL.
- Если VL недоступна, отчет показывает расчет, но не публикует неподтвержденные цитаты.

## 12. Этап 8 - интерпретатор карты

Принцип: расчет отдельно, интерпретация отдельно.

Pipeline:

1. `ChartFacts` - строгие факты: положения, аспекты, даши.
2. `RuleMatcher` - применяет правила шастр.
3. `CitationResolver` - прикрепляет источник.
4. `VaishnavaPolicyFilter` - корректирует remedial/religious advice.
5. `ReportComposer` - собирает текст.
6. `ReviewGate` - блокирует слабые/непроверенные выводы.

Типы выводов:

- характер/склонности;
- духовная практика;
- здоровье только мягко и без диагноза;
- семья/отношения;
- образование/карьера;
- финансы без инвестиционных советов;
- периоды жизни;
- рекомендации садханы;
- предупреждения о точности времени рождения.

Done:

- Каждый абзац отчета имеет `citations[]` или пометку `calculation_only`.
- Нет независимого поклонения полубогам.
- Нет категоричного фатализма.

## 13. Этап 9 - frontend

Основные экраны:

- регистрация/логин;
- список карт пользователя;
- создание карты;
- интерактивная карта D1;
- переключатель varga charts;
- dasha timeline;
- transit view;
- отчет с цитатами;
- список источников;
- настройки ayanamsa/house system;
- экспорт PDF;
- admin review.

UX:

- пользователь сразу видит карту, а не маркетинговый лендинг;
- понятные статусы точности: exact time, approximate time, unknown time;
- ссылки на источники раскрываются рядом с выводом;
- спорные места помечаются как требующие проверки.

Done:

- Playwright smoke проходит на desktop/mobile.
- Нет перекрытия текста и элементов.
- Генерация отчета работает через background job.

## 14. Этап 10 - admin и review workflow

Нужна админка не только для пользователей, но и для богословской/астрологической проверки.

Разделы:

- источники;
- passages;
- правила;
- remedial mappings;
- JHora comparison runs;
- спорные вычисления;
- отчеты пользователей с обезличиванием;
- аудит цитат;
- версии алгоритмов.

Done:

- Любое новое правило сначала `draft`.
- Публично используется только `approved`.
- Можно увидеть, кто и когда одобрил правило.

## 15. Этап 11 - безопасность и приватность

Данные рождения чувствительные.

Требования:

- пользователь видит только свои карты;
- admin access отдельно;
- rate limit на API;
- audit log на доступ к чужим картам;
- backup БД;
- экспорт/удаление своих данных;
- опциональное шифрование точного времени/места рождения;
- отчеты не индексируются поисковиками.

Done:

- Есть threat model.
- Есть тесты прав доступа.
- Есть политика хранения данных.

## 16. Этап 12 - MVP

MVP не должен пытаться сразу заменить всю JHora.

MVP scope:

- auth;
- создание карты;
- geocoding/timezone;
- D1;
- nakshatra/pada;
- panchanga;
- D9;
- Vimshottari;
- базовый отчет;
- цитаты из VL;
- вайшнавский фильтр рекомендаций;
- JHora comparison по 20 картам.

Done:

- Пользователь получает полезный отчет.
- Админ видит, какие выводы основаны на каких источниках.
- Расчеты не расходятся с JHora без объяснения.

## 17. Этап 13 - расширение до JHora parity

После MVP:

- D1-D60;
- полный набор dashas;
- yogas catalog;
- shadbala;
- ashtakavarga;
- transits;
- annual charts;
- compatibility;
- muhurta;
- prashna;
- stronger report generator;
- compact JHora-like workspace: multiple vargas visible at once, dense tables, tabbed analytical areas;
- dual calculation view:
  - `primary_calculation`;
  - `jhora_profile_calculation`;
  - `delta`;
  - `settings_diff`;
  - `authority_decision`;
- JHora screenshot inventory for Basics, Strengths, Dasas, Transits, Ashtakavarga, Muhurta/Prashna and settings dialogs;
- API для внешних клиентов.

Done:

- Матрица `docs/jhora_feature_matrix.md` закрыта по приоритетам.
- Есть regression suite на 100+ карт.

## 18. Этап 14 - проверка традиции

Нужна ручная экспертная проверка.

Работы:

- Составить список спорных тем: remedial measures, graha worship, gemstones, mantra recommendations, predictions.
- Для каждой темы найти позиции:
  - классическая джйотиш-шастра;
  - Shyamasundara Dasa или авторитетный ISKCON-источник;
  - Шрила Прабхупада/VL.
- Ввести статусы:
  - `approved_gaudiya`;
  - `allowed_with_krishna_centered_framing`;
  - `admin_only`;
  - `blocked`.

Done:

- Нет автоматического совета, который противоречит сиддханте ISKCON.
- Спорные темы требуют ручного review.

## 19. Риски

1. Лицензия эфемерид. Решить до публичного запуска.
2. Исторические timezone. Нужна отдельная проверка.
3. Разные настройки JHora. Для сравнения фиксировать ayanamsa, house system, true/mean nodes, sunrise method.
4. Авторитетность текстов. Нельзя смешивать неподтвержденные PDF с публичным отчетом.
5. AI hallucinations. Интерпретации должны быть rule/citation-first.
6. Время рождения часто неточное. Сервис обязан показывать uncertainty.

## 20. Порядок исполнения

- [ ] Утвердить backend: Django или Go. Моя рекомендация: Django.
- [ ] Утвердить MVP scope.
- [ ] Создать `docs/product_scope.md`.
- [ ] Создать `docs/vaishnava_interpretation_policy.md`.
- [ ] Создать `docs/jhora_feature_matrix.md`.
- [ ] Поднять каркас backend/frontend/db.
- [ ] Реализовать расчетный MVP.
- [ ] Сделать JHora comparison suite на 20 карт.
- [ ] Подключить VL read-only.
- [ ] Сделать первый отчет с цитатами.
- [ ] Провести review традиции.
- [ ] Расширять функциональность до parity.

## 21. Самопроверка понимания

Я не должен начинать с красивого сайта. Сначала нужны точность расчетов, источники, права, политика интерпретаций и проверяемость.

Я не должен "верить JHora на слово". JHora - сильный практический эталон, но каждое совпадение/расхождение надо объяснять настройками и алгоритмами.

Я не должен заменять гаудия-вайшнавскую традицию общим индуистским remedial-подходом. Если классический текст говорит о propitiation конкретной graha/devata, публичная рекомендация должна быть Кришна-центричной и согласованной с Прабхупадой.

Я должен использовать `C:\Projects\vl` как источник Прабхупады и шастр, а не импортировать все заново.

Первый реальный результат должен быть малым, но правильным: карта + D9 + Vimshottari + цитируемый отчет + тесты против JHora.
