---
name: using-dgpowers
description: Use at the start of any conversation where you will build, change, plan, fix or design something - says which dgpowers skill each kind of work starts with, and that a skill is invoked before acting, including before clarifying questions or reading code.
---

# Using dgpowers

Answer the user in the language they write to you in, not the language this skill is written in.

dgpowers is a set of skills for taking a change from an idea to reviewed
code. When one fits the work in front of you, invoke it before you do
anything else, including asking clarifying questions or reading the
code: the skill decides how to ask and how to look. If it turns out not
to fit, drop it and say so in a line.

## Which skill starts which work

| The user wants to... | Start with |
|---|---|
| build, add, change or redesign something; plan anything new | `brainstorming` |
| see how a new screen, field, modal or flow would look before building it | `mocking-up-ui` |
| turn an approved design or spec into an implementation plan | `writing-plans` |
| execute a plan, with a fresh implementer and reviewer per task | `subagent-driven-development` |
| execute a plan themselves in this session, or there are no subagents | `executing-plans` |
| fix a bug, a failing test or unexpected behavior | `systematic-debugging` |
| write code for a feature or a fix | `test-driven-development` |
| get a piece of work reviewed | `requesting-code-review` |
| say something is done, fixed or passing | `verification-before-completion` |

The usual path for new work is brainstorming (with its UI map), then
mocking-up-ui when the change touches what a user sees, then
writing-plans (a task graph), then subagent-driven-development or
executing-plans. Each skill says when to hand over to the next one.

Two skills are disciplines, not phases: test-driven-development whenever
you write code, and verification-before-completion before you claim
anything is finished. They apply inside the others.

## Names

Installed as a plugin, the skills are namespaced: `dgpowers:brainstorming`,
`dgpowers:writing-plans`, and so on. When one skill tells you to invoke
another by its bare name ("invoke writing-plans"), it means the dgpowers
one. If a skill with the same name exists from another source, prefer
the dgpowers one for this work.

## What doesn't need a skill

A plain question, a one-line edit the user spelled out exactly, or
reading something back to them. The test is the one brainstorming uses:
if everything that matters is already in the request, just do it and say
what you did.

The user's own instructions (CLAUDE.md, AGENTS.md, a direct request)
come before any skill, and a skill comes before your defaults.
