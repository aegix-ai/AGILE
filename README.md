## GAC — Governed Autonomous Cognition

**GAC (Governed Autonomous Cognition)** describes a system that doesn’t just generate text, but repeatedly **decides and acts** in an environment while being held inside **explicit constraints, permissions, and verification gates**.

Scientifically, you can model GAC as decision-making under partial information (a **POMDP**). At each step *t*, the system receives an observation *oₜ* (tool outputs, logs, sensor data, web state), maintains an internal belief/state summary *bₜ* (memory + state estimation), chooses an action *aₜ* (often a **tool call**, not a token), and then receives outcomes and feedback *(oₜ₊₁, rₜ)*.

The core object is a policy:

<div align="center">
  <img
    src="https://latex.codecogs.com/svg.image?\dpi{260}\bg{white}\color{black}{\displaystyle\pi(a_t\mid%20b_t)}"
    alt="pi(a_t | b_t)"
    height="90"
  />
</div>

Meaning: “given what I think is going on, what should I do next?”

---

### What makes it more than an LLM agent

GAC is built as a **stack of distinct roles** rather than one monolithic prompt-following loop:

- **Cognition (LLM / MoE):** generates hypotheses, plans, decompositions, and candidate actions.  
  With **MoE**, a router activates a subset of specialized experts per context to increase capability efficiently.

- **Control (RL / classical controllers):** selects and refines actions based on outcomes, especially when success depends on multi-step behavior and delayed feedback.

- **Perception (CV / NLP / signal processing):** converts raw inputs (images, audio, documents) into features/representations that update the belief/state *bₜ*.

- **Memory / World Model:** stores history and optionally predicts consequences of actions (a learned dynamics model or simulators), enabling planning instead of pure reaction.

- **Tools (action interface):** defines the *real* action space: API calls, file ops, system commands, browser steps, DB queries, robotic commands, etc.

---

### The “Governed” part (the key difference)

Action selection is not “whatever the model suggests.” Proposed actions are passed through explicit constraints:

<div align="center">
  <img
    src="https://latex.codecogs.com/svg.image?\dpi{260}\bg{white}\color{black}{\displaystyle a_t=\mathrm{Guard}(\mathrm{Propose}(b_t))}"
    alt="a_t = Guard(Propose(b_t))"
    height="90"
  />
</div>

Where **Guard** can enforce:
- permissions / allowlists (what tools can be used)
- rate limits, budgets, timeouts
- sandboxing (run untrusted actions safely)
- audit logging and reproducibility
- mandatory verification (tests, validators, policy checks)
- safe fallbacks and abort conditions

This is the layer that prevents reward-hacking, unsafe tool use, and “high-confidence wrong actions” from turning capability into failure.

---

### One-line definition

**GAC is a constrained, hierarchical decision system in which tool use is the action space, cognition proposes options, control optimizes behavior over time, perception updates state, memory supplies context, and governance enforces invariants.**
