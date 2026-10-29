---
name: read-it-quick
description: Reads something long so the user doesn't have to (a Markdown file, a PDF, a book, an EPUB, a Word document, a web page, a folder of docs, a pasted text) and gives back only the main idea and a short menu of the concepts worth digging into, then explains whichever ones the user picks, one level deeper each time. Use it whenever the user hands over something to read and wants the gist rather than a full summary ("read it quick", "lee esto rápido", "léete esto", "¿de qué trata esto?", "dame la idea principal", "resumime este libro", "¿qué dice este documento?", "no tengo tiempo de leer esto", "explicame este paper"), even if they don't say "skill" or "summary". Not for reviewing or editing code, and not for writing a full report or translation of the document.
---

# read-it-quick

The user hands you something to read and wants to know what it is about without reading it. Give them the main idea, then a menu of the concepts inside it, and let them choose where to go deeper. They drive the depth; you do the reading.

The point is a short answer that opens doors, not a long summary that closes them. If the user can read your first answer in under a minute and knows what to ask next, it worked.

Talk to the user in their language (usually Spanish) and their register (tú, vos or usted, as they write), plainly. No emojis anywhere in the output.

## 1. Read the whole thing

Read everything before answering. A main idea pulled from the first pages and the table of contents is a guess, and the user can't tell it from a real reading.

How to get the text, by source:

| Source | How |
|---|---|
| `.md`, `.txt`, code docs | Read the file. Read returns large files in pieces: keep reading with `offset` until the end. |
| `.pdf` | `pdftotext -layout` if installed, otherwise the `pdf` skill or Read with `pages`. Scanned PDFs need OCR (the `pdf` skill covers it). |
| `.epub` | It's a zip of HTML: unzip it into a new empty folder in the scratchpad, read the chapters in the order the `.opf` spine lists them. |
| `.docx`, `.pptx`, `.xlsx` | The matching skill (`docx`, `pptx`, `xlsx`) or `pandoc` to plain text. |
| A URL | WebFetch, or the built-in browser when the page needs JavaScript or a sign-in (in the Claude desktop app, the browser pane). Claude in Chrome only if the user asks for it or there is no built-in browser. Never open the user's own browser (`open <url>`). |
| A folder | List it, read the index or README first, then the rest. |
| Pasted text | It's already here. |

Start with the structure (table of contents, headings, chapter titles): it tells you how the author organized the ideas, and the menu often follows it.

**What counts as the thing.** The source is what the user handed over. Follow local links only when they are parts of the same work (a book split into one file per chapter, a docs folder). Links to external articles and images you can't see are not part of the reading: if the document leans on them (diagrams, solutions kept in other files), say so. Prefaces, translator's notes and appendices count as read, but the main idea is about the main work.

**Long sources (a book, a large PDF, a whole docs folder).** Past roughly 40k words, or whenever the text won't comfortably fit in your context with room left for the follow-ups, split it by chapter or section and send one reader subagent per part, all in the same message so they run in parallel (in Claude Code, the Agent tool; `model: "sonnet"` is enough). Give each one its part's location (file and page or chapter range) and ask it to return:

```
Part: <chapter or section, page or line range>
Main point: <one or two sentences>
Concepts: <each concept introduced or developed here, one line each, with where it appears>
Connections: <ideas this part builds on or sets up for later parts>
Unreadable: <anything in the part that couldn't be read, or "none">
```

Then put the main idea together yourself from those reports: the main idea of a book is rarely the main idea of its first chapter. Keep the reports (in the scratchpad, if they are long) so you can find the right chapter when the user digs in. They are a map, not the text: before explaining a concept in step 3, read its passage yourself. With no subagents available, read the parts yourself one after another and take the same notes.

**If part of it can't be read** (scanned pages without OCR, a paywall, a broken file, pages missing), say exactly which part when you answer. Don't fill the gap from what you know about the topic.

## 2. First answer: the idea and the menu

Use this shape, and keep it short:

```
**<Title of the thing>** (<what it is: book, design doc, paper, RFC... and its length>)

<The main idea in two to four sentences: what it is about, what it argues or
describes, and what it's for or who it's for.>

<Only if something couldn't be read: one line saying exactly what.>

**Para ahondar:**
1. **<Concept>**: <one line: what it is or why it matters here>
2. **<Concept>**: <one line>
...

¿En cuál quieres entrar? Puedes elegir uno, varios o "todos".
```

What makes a good menu:

- **The concepts the document actually develops,** not every term it mentions. A concept earns a place if the author spends real space on it or the rest depends on it.
- **Usually 4 to 8 items.** If there are more, group them ("Patrones de mensajería: cola, pub/sub, event sourcing") and let the user open the group.
- **In the order that makes sense to learn them,** foundations first, which is usually but not always the author's order.
- **Each line says something.** "Microservicios: dividir el sistema en servicios que se despliegan por separado" beats "Microservicios: un tipo de arquitectura".
- **The terms in the document's own words,** so the user can find them in it. If the document is in another language than the user's, translate the term and keep the original next to it when that helps searching: "Capacidad y fortuna (*ability*, *fortune*)".

Give the length in a unit the user can picture: pages if it has them, otherwise chapters or sections, or an approximate word count.

Example, for a document about software architectures:

```
**Software Architecture Patterns** (guía, ~60 páginas)

Compara cinco formas de organizar una aplicación grande y cuándo conviene
cada una. La tesis es que no hay una mejor: cada arquitectura cambia
facilidad de desarrollo por escalabilidad, despliegue o rendimiento, y hay
que elegir según qué necesita el sistema.

**Para ahondar:**
1. **Capas (layered)**: separar presentación, negocio y datos; la opción por defecto.
2. **Orientada a eventos**: componentes que reaccionan a eventos en vez de llamarse entre sí.
3. **Microkernel**: un núcleo mínimo y funcionalidades como plugins.
4. **Microservicios**: servicios pequeños que se despliegan y escalan por separado.
5. **Basada en espacios (space-based)**: quitar la base de datos del camino crítico para escalar mucho.
6. **Cómo elegir**: la tabla con la que el autor compara las cinco.

¿En cuál quieres entrar? Puedes elegir uno, varios o "todos".
```

Don't add a full summary, a list of chapters, quotes or your opinion of the document to this first answer, unless the user asked for them. The menu is the invitation; the depth comes when they pick.

## 3. Going deeper

When the user picks a concept (by number, name, or anything close), go back to its passage in the source and read it again: your first reading, or a reader subagent's report, gives you where it is, not the detail to explain it well. Then explain it from the document:

- **What it is,** in plain words.
- **What it's for:** the problem it solves, and when the document says to use it or avoid it.
- **How it works,** with the example or diagram the document gives, retold briefly.
- **How it connects** to the other concepts in the menu.
- **Where it is** in the source (chapter, section, page), so the user can go read it.

When the document's diagram is an image you couldn't see, use its text examples instead; the first answer already said the diagrams weren't read.

Then offer the next level the same way: a numbered list of a few sub-concepts the document develops inside this one, or the related items from the first menu, and close with the same question. Stop offering when there is nothing more in the document to open.

**When the pick is a group** (a menu item that bundles several concepts, or a long section such as "Bases de datos"), don't explain every member at once. Say in two or three sentences what ties them together, list the members with one line each, and let the user open one. That answer is a smaller menu, not a chapter.

Keep each answer about the size of one concept: around 150 to 300 words before the next-level menu. The five points above are what to cover, not five headings to fill; merge them when that reads better, and keep the one or two examples that show the idea best rather than every one the document gives. When the concept is spread across the document, explain it from its main passage and list the other places in one line. If they choose several or "todos", go through them in menu order with the same short structure each, and ask before continuing if the answer is getting long.

**The document first, your knowledge second.** Explain what the document says. When adding something it doesn't say (a more current view, a counterexample, a term it gets wrong), mark it plainly ("Esto no está en el documento, pero...") so the user knows which is which. If the user asks something the document doesn't cover, say so before answering from general knowledge. The same goes for a translator's or editor's introduction and footnotes: they are part of what you read, but say whose view it is when it differs from the author's.

## Other things the user may ask

- **"Dame un resumen completo"**: then write a proper summary, section by section. The skill's default is short, not the only option.
- **A question about the content** ("¿qué dice sobre X?"): answer it from the text, with where it is.
- **Another document**: start over from step 1. If it relates to the first one, say how.

## Common mistakes

| Mistake | Why it hurts |
|---|---|
| Answering after reading the first pages or the table of contents | The main idea is often stated or changed later. The user trusts that you read it all. |
| A long summary in the first answer | The user asked for the gist. They pick the depth. |
| A menu of every term in the document | Ten weak items hide the three that matter. |
| Generic one-liners in the menu | "X: un concepto importante" gives no reason to pick it. |
| Explaining a concept from the reader reports or memory of the first pass | Detail and nuance get lost in the summary. Re-read the passage before explaining it. |
| Explaining a whole group in one answer | It becomes the long summary the user didn't ask for. Show the group as a smaller menu. |
| Explaining from general knowledge as if it were the document | The user wanted to know what this text says, and may act on it. |
| Not saying which parts couldn't be read | A confident summary of half a book is worse than an honest one. |
