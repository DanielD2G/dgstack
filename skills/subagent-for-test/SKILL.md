---
name: subagent-for-test
description: Runs backtrack-for-test in a background subagent that follows the user's ongoing changes on the same branch, writing and running tests, fixing small bugs, committing its own work and escalating what breaks, while the main agent keeps working with the user. Use it whenever the user wants tests handled in the background without stopping ("subagent for test", "lanzá el agente de tests", "que un subagente vaya testeando", "testeá en segundo plano", "acompañá los cambios con tests", "dejá la rama testeada"), and when they accept the test-agent offer on entering quick-change mode. Not for writing tests in the foreground yourself; that is backtrack-for-test.
---

# subagent-for-test

You keep working with the user. A background test agent follows behind on the same branch: it reads git, writes and runs the tests, fixes what is small and obvious, commits its own work, and escalates anything that breaks. Your job:

- launch it with a good brief;
- keep it in sync while the user keeps changing things;
- relay what it says to the user.

The testing itself is `backtrack-for-test`'s job. Don't do it in the foreground.

Talk to the user in their language (usually Spanish), briefly.

## 1. Gather the brief

- **Repo and branch:** the absolute repo path, the current branch, `HEAD`, and the base (`git merge-base HEAD <default branch>`).
- **What was done in this conversation:** each change, its files and its **intent**, including deliberate decisions ("removed the button only on this screen, on purpose") and reverts. The agent can read the diffs. Only you know the why.
- **Running servers:** check listening ports (`lsof -nP -iTCP -sTCP:LISTEN`), the process working directory (`lsof -a -p <pid> -d cwd`), and any preview or dev-server list your tools offer. Pass the URL, what it serves and its PID, or "none".
- **Test commands,** if you already know them.
- **Where the skill lives:** `backtrack-for-test` by name, plus the absolute path of `../backtrack-for-test/` next to this skill as a fallback.

## 2. Launch it

- Spawn **one** background subagent per branch. In Claude Code, that is the Agent tool with a general-purpose agent, run in the background, with a `name` such as `test-follower` so you can message it. If this conversation already has one, resume it with a message instead of spawning another.
- If you can't spawn subagents here, say so and offer to run `backtrack-for-test` in the foreground.
- Fill in this brief:

```
You are the background test agent for this branch. Load the skill `backtrack-for-test`
(Skill tool; if it isn't available, read <abs path>/backtrack-for-test/SKILL.md) and
follow it in BACKGROUND MODE, including references/background-mode.md.

Repo: <abs path>
Branch: <branch>   Base: <base>   HEAD at launch: <sha>
Running servers: <url — what it serves — pid, cwd> | none (don't start one; escalate if you need it)
Test commands: <known commands> | unknown

Changes so far (read the diffs yourself; the intent is what matters):
- <what changed> — <files> — <intent / decision>

The user and I keep editing this same checkout while you work. I'll send UPDATE messages
after each change. End each round with a TEST ROUND REPORT, or with an ESCALATION block
when something needs the user's call.
```

- Tell the user in one line, e.g. "Agente de tests corriendo en segundo plano. Sigo con vos."

## 3. Keep it in sync

After **every** change you finish while the agent is alive (in quick-change, right after the report), send it one line with the message tool (in Claude Code, SendMessage to its name):

```
UPDATE: <what changed> — <files> — <intent, especially if behavior changed on purpose>
```

Also send an update when:

- the user reverts something ("UPDATE: reverted the modal; back to the inline form");
- the user changes their mind about intended behavior;
- the user commits.

Don't paste diffs and don't wait for a reply. If the agent already ended its turn, the same message resumes it with its context.

While it's alive:

- Don't edit its test files. If a request needs a test change, say so in the update.
- If the user asks you to commit, commit by path, only your files: `git commit -m "<msg>" -- <paths>`.
- Don't run `git add -A`, `stash`, `reset`, `checkout` or `restore` of files, `rebase`, or switch branches. Any of those pulls the floor out from under it.
- Don't restart or stop a server it's using without telling it.

## 4. Relay what it reports

Its reports arrive when it ends a turn. They are reports, not proof: check `git log` before telling the user something was committed.

**ESCALATION:** this is the first thing in your next message to the user, before anything else:

> 🧪 **El agente de tests encontró algo:** <what breaks, one line>
> **Dónde:** <file / test>
> **Opciones:**
> 1. <option>
> 2. <option>

Then send the user's answer back in their own words, and say who applies any product change it needs: `DECISION: the user says "<their words>" — <you apply it | I apply it>`. Don't paraphrase it into something stronger or weaker. If the fix lands in a file you or the user are still working on, apply it yourself, as a normal change with its own UPDATE.

**TEST ROUND REPORT:** one line to the user, and only when something is worth knowing: tests added, a fix, a commit, or something left undone. For example: "🧪 +3 tests en `cart.test.ts`, todo verde (commit `a1b2c3d`). Arregló un null en el total vacío."

## 5. Close

Close when the user leaves quick-change mode, or says plainly that they're done with this batch and want the branch ready. A red-alert detour out of quick-change for one request is not leaving it, and neither is a "listo" that only closes one change.

1. Send `FINAL`.
2. When the final report arrives, check its commits with `git log`.
3. Give the user the final summary:
   - tests added;
   - what was deliberately not tested and why;
   - fixes made;
   - commits;
   - anything uncommitted (tests waiting for the code they cover to be committed, fixes sitting in files the user still has to commit);
   - anything that wasn't run;
   - the branch state.
4. If tests or fixes are still uncommitted because the user's changes are, ask whether to commit everything together. On a yes, commit the user's changes and those tests together, by path.

Never push.

## Common mistakes

| Mistake | Why it hurts |
|---|---|
| Updates without intent ("edited Cart.tsx") | The agent can't tell a deliberate behavior change from a regression, so it "fixes" the user's change back. |
| A new agent per change | It loses the context it built up and repeats work. Resume the one you have. |
| Holding an escalation until the end | The user wants to hear about breakage while it's still cheap to fix. |
| Sweeping git commands while it works | They move or mix its uncommitted work with the user's. |
| Writing the tests yourself in the foreground | It defeats the point: the user is waiting on you. |
