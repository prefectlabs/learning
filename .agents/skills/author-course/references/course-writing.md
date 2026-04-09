# Writing Reference for Courses

Use this reference for learner-facing copy in `assignment.md`, notes, hints, quiz explanations, and script output. Keep it in step with `content-design.md` for challenge shape and `file-formats.md` for structure and schema.

## Principles

- **Shift understanding**; explain the work in a way that changes how the learner thinks about it.
- **Start with the mess they know**; describe the friction first, then introduce the fix.
- **Work at the smallest useful system level**; show how commands, settings, and scripts behave together without extra moving parts.
- **Keep code examples tiny**; choose the smallest code block that still proves the point. This does not apply to prose — trim the code, not the explanation around it.
- **Stay concrete**; real paths, commands, outputs, and examples build credibility.
- **Explain before the code fence**; every step needs 1-3 sentences that say what the command does, why the learner is running it, and what to expect. The prose is the teaching; the code block is the practice.
- **Be hopeful without glossing over reality**; encourage progress while still naming trade-offs and failure points.
- **Teach, don’t pitch**; the guide should still be useful even if the reader only cares about the skill itself.
- **Let ideas connect**; each paragraph should flow into the next, and examples should demonstrate a repeatable pattern rather than act as decoration.

## Voice and flow

- **Anchor in the learner’s reality**; open from a situation they recognize instead of abstract motivation.
- **Write a fuller opening**; give the learner a short orientation paragraph or two before the first step so they know what is happening and why it matters.
- **Sound sure, not inflated**; make clear claims and back them with something observable.
- **Use current terms plainly**; stay accurate without hiding behind jargon.
- **Link each task to the workflow**; explain why the step matters in the wider system.
- **Put the point up front**; say what is happening and why it matters before the reader has to search for it.
- **Vary the rhythm**; mix sentence length and punctuation so the prose feels intentional rather than mechanical.
- **Keep transitions natural**; skip stock openings and tired scaffolding.
- **Show your evidence**; use commands, outputs, screenshots, diagrams, or comparisons when you make a claim.
- **Meet objections where they appear**; note trade-offs at the moment a careful reader would wonder about them.
- **Use numbers when they help**; include them only when they clarify scale, effort, or outcome.
- **Pick the right form**; use bullets for structure and prose for flow, not out of habit.
- **Keep feedback usable**; if the learner can stumble, tell them what to inspect and how to recover.
- **Leave space for judgment**; do not script every choice when the exercise should teach decision-making.
- **Match the tone to the piece**; tutorials should stay practical, while broader pieces can reach higher without losing precision.
- **Trim the code first**; if the same point can be shown with less code or fewer steps, choose the smaller code version. But keep the explanation around it — a smaller example often needs the same amount of prose to land.

## Course rules

- **Know the audience**; tune the pace and depth for beginner, intermediate, or advanced learners.
- **Use beginner-sized code examples by default**; only scale up the code complexity when the learner needs it. Beginner-sized does not mean less explanation — it often means more, because the learner has less context to fill in gaps.
- **Reveal the lesson gradually**; give more support early and less as context builds.
- **Verify fast-moving details**; check current terminology, APIs, and workflows against primary sources.
- **Retire stale language**; avoid deprecated terms and refresh examples when the ecosystem changes.
- **State prerequisites first**; call out required knowledge, access, tools, and setup before the opening task.
- **Separate must-haves from nice-to-haves**; do not bury dependencies in the first exercise.
- **Keep prose and checks aligned**; every instruction should point toward a state the check script can verify.
- **Show the finish line**; make the successful state visible before the learner clicks Check.
- **Keep solve scripts aligned**; the automated path should reach the same end state the text promises.
- **Teach one outcome at a time**; keep each challenge focused and split work that tries to do too much.
- **Use notes for background and the body for guided action**; put conceptual framing in notes and let the assignment text drive the work. But the body still needs its own opening paragraph and per-step explanations — "action-oriented" does not mean "unexplained." Notes should read like a short orientation: say what is changing, why it matters, and what the learner should notice.
- **Use hints and examples with intent**; hints should unblock, and examples should feel believable in the environment.
- **Validate results, not procedure**; check scripts should confirm the end state, not the exact commands used.

## Review

- **Would it still matter to an informed reader?**; if the learner already knows the topic, the piece should still reward their time.
- **Does it point forward?**; the text should tell the learner what to do next without wandering.
- **Are the prerequisites obvious?**; the learner should know what they need before they begin.
- **Do the checks match the promise?**; validation should cover the same result the prose describes.
- **Does it reveal something real about the workflow?**; the lesson should leave the reader with a non-obvious takeaway.
- **Could a thoughtful reader disagree?**; the idea should be specific enough to defend or challenge honestly.
- **Watch for familiar failures**; generic prose, vague claims, hidden setup, mismatched instructions and checks, invented anecdotes, overselling, or cramming too much into one challenge.
- **Could the code example be simpler?**; use the smallest code block that still teaches the pattern. But do not trim the prose that explains it — if a step has no explanation before its code fence, add one.
- **Would the task scope feel oversized to the learner?**; trim extra services, infrastructure, and syntax from the code example. But a step that explains what is happening in 2-3 sentences is not oversized — that is normal teaching.
- **Keep the takeaway simple**; clear, specific writing helps the learner finish the task and carry the idea into real work.
