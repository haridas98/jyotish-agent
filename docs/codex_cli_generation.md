# Codex CLI Generation

Codex CLI установлен локально:

```powershell
C:\Users\Admin\AppData\Local\OpenAI\Codex\bin\codex.exe
```

Его можно использовать как отдельный генератор draft-разбора без прямого вызова OpenAI API из backend.

## Натальный разбор

1. Сформировать packet и prompt:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py build_analysis_packet `
  --birth-date 1998-04-30 `
  --birth-time 13:45 `
  --place-name "Ishimbay" `
  --timezone Asia/Yekaterinburg `
  --latitude 53.4546 `
  --longitude 56.0439 `
  --output ..\.tmp\analysis-packet.json `
  --prompt-output ..\.tmp\analysis-prompt.md `
  --citation-requests-output ..\.tmp\citation-requests.json
```

2. Запустить Codex CLI:

```powershell
cd C:\Projects\jyotish-agent
Get-Content .\.tmp\analysis-prompt.md -Raw |
  codex exec --cd C:\Projects\jyotish-agent --sandbox read-only --output-last-message .\.tmp\analysis-draft.json -
```

3. Проверить результат вручную перед публикацией.

## Правила

- Ответ Codex CLI всегда считается `draft`.
- Использовать только citations из packet.
- Не выдумывать стихи, главы, ссылки и названия источников.
- Не давать самостоятельное поклонение полубогам как remedy.
- Рекомендации формулировать через прибежище у Кришны, садхану, служение вайшнавам и наставления Шрилы Прабхупады.

## Когда лучше CLI

- Для ручной редакторской работы астролога.
- Для разборов, где нужно посмотреть prompt и итоговый текст.
- Для пакетной генерации с сохранением файлов.

## Когда лучше backend API

- Для пользовательской кнопки в UI.
- Для сохранения draft в БД.
- Для будущего review workflow в админке.
