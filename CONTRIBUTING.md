# Contributing — Applications and Integrations

Corrections, clearer explanations, better figures, better test data and new worked examples are welcome. Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## How to contribute

- **Found an error?** Open an [Erratum](../../issues/new?template=erratum.yml) issue with the section number (e.g. §22.4), what the book says and what it should say, with a calculation, a simulation, a measurement or a datasheet reference.
- **A figure is wrong or unclear?** Open a [Figure](../../issues/new?template=figure.yml) issue, or fix `figures/scripts/chNN.py` and send a pull request.
- **Build, figure-script or MCP-server problem?** Open a [Tooling bug](../../issues/new?template=tooling-bug.yml).
- **Bigger change** (a new section, a rewrite, a new project variant)? Open a [Proposal](../../issues/new?template=proposal.yml) first so the scope can be agreed.

## Pull requests

1. One topic per pull request: a fix, a figure, a section.
2. Follow the house style below; every number you add must be checked (e.g. with Python), and every code listing must compile or run as shown.
3. Run the checks locally before pushing (CI runs the same ones):

```bash
npm ci
```

```bash
npm run check
```

```bash
python scripts/build-figures.py ch22
```

4. Changed a figure? Commit the script and the regenerated PNG together. Added a figure marker? Draw it, run `node scripts/insert-figures.mjs` and `npm run figures:plan`.
5. Leave `pdf/` alone; the PDF is rebuilt and attached to each release by the release workflow.

By contributing you agree that your contribution is licensed under the repository's [MIT License](LICENSE).

---

# House Style

The master outline is [`TOC.md`](TOC.md). It is fixed: 9 parts, 40 chapters. Do not skip, merge or rename listed topics; every bullet in the TOC must be covered by a section or subsection of its chapter.

## What kind of book this is

This is the integration book of the EEE series. It is **project-oriented**: it must not become another theoretical textbook. Every chapter is about a real engineering system and follows it through

**requirements → architecture → design calculations → component selection → implementation → verification → failure analysis.**

Theory appears only as a one-line result with a link to the book that owns it, followed immediately by its use: a number, a choice of part, a test limit. The pages go to what the theory books do not have: design procedures, trade-offs, budgets (power, energy, timing, error, link, thermal, cost), real parts and ratings, interface details, firmware and tool code, test plans with pass/fail limits, measured-looking results with uncertainty, failure modes and what was changed because of them.

## Files

- Each part is a folder `part-N-<slug>/`. Its `README.md` is the part opener; `NN-<slug>.md` (NN two digits, global chapter number) is a chapter. The exact file names are listed in the TOC.
- Markdown only. Math is GitHub-style LaTeX: `$...$` inline, `$$...$$` display (display math on its own lines). Never `\(...\)` or `\[...\]`.
- In tables, never put a raw `|` inside math; use `\lvert ... \rvert` or `\Vert`. Outside math, write the logical OR of code as `||` only inside code spans or fenced blocks, never in a table cell.
- A literal dollar sign in prose (prices, costs) is written `\$` — e.g. `\$4.20` — so it is not read as math. Avoid `$` inside code spans.
- Use `\mathrm{}` for units in math, e.g. `$I_{q}=12\ \mathrm{\mu A}$`, `$E=48\ \mathrm{kWh}$`. Prefer plain text units outside math.
- Use $j=\sqrt{-1}$ (engineering convention).
- **No exercises, problems, quizzes or answer sections.** Worked examples and design walk-throughs inside the text are welcome.

## Chapter layout

```
# Chapter N — Title

*Part X · Part title*

Opening paragraph that starts from a real system and a real failure or decision (a data logger whose readings drift 2 °C after the enclosure is closed, a line follower that oscillates above 0.6 m/s, a PV string that trips its inverter on a cold morning, a PLC panel that fails its E-stop validation, an IoT node whose battery lasts 3 weeks instead of 2 years).

> **Question 1?**
> **Question 2?**

| Concept | Engineering destination |
|---|---|
| ... | ... |

**Roadmap.** Short arrow-chain through the sections (N.1 → N.2–N.3 → ...).

---

## N.1 Section title
...
---
## N.2 ...
...
## What remains open

| Open question | Where it is answered |
|---|---|

**Next:** one sentence pointing to the next chapter.
```

Use `### ` subsections freely inside sections. Separate `## ` sections with `---`.

### The reference system

Every chapter in Parts II–VIII carries **one running reference system** from start to finish (named in the opening paragraph: e.g. a 16-channel thermocouple logger for a battery test lab, a 6-axis desktop arm, a 250 kW packaging-line conveyor, a 10 kWp rooftop PV plant, a 2-lead ambulatory ECG). Sections may add other examples, but the reference system must be visibly designed, built, verified and failure-analysed across the chapter. Each of those chapters contains, somewhere it fits naturally:

- a **requirements table** with IDs (`R1`, `R2`, …), a measurable target and a verification method;
- an **architecture** block diagram (a figure) and the interfaces between blocks;
- at least one **budget** table (power, energy, timing/latency, error/uncertainty, link, thermal or cost) with a margin column;
- a **component-selection** table comparing two to four real part classes against the requirements, with the choice and why;
- **implementation** detail: circuit values, wiring, firmware or software listings, configuration;
- a **verification** table (requirement → test → limit → result → pass/fail);
- a **failure analysis**: an FMEA-style table (failure mode → effect → cause → detection → mitigation) or a worked fault-diagnosis story.

Part I chapters teach the method itself and use one small running system to demonstrate each step (the same system may recur across Part I). Part IX chapters are complete projects: their sections follow the TOC bullets in order, and additionally each project includes a bill of materials with indicative cost, a test-results table, an FMEA and a closing **"Revision B"** subsection listing what the next iteration would change and why. Chapter 40 is the capstone method: it ties Part I's methodology to a full project-report template, illustrated with one capstone worked through end to end.

## Code listings

Code is used where it is the implementation: firmware in C (C11/C17) and C++ (C++17) for microcontrollers; Python for design calculations, simulations, data processing, test automation and engineering tools; IEC 61131-3 Structured Text for PLCs (Ch. 18–21); shell, YAML, JSON or TOML for build, CI and configuration (Ch. 5, 29, 31); MQTT topic and payload examples as JSON (Ch. 11, 35, 38).

- Fenced blocks with a language tag: ` ```c `, ` ```cpp `, ` ```python `, ` ```text ` (for Structured Text, write ` ```text ` and say "IEC 61131-3 Structured Text" in the prose), ` ```bash `, ` ```yaml `, ` ```json `, ` ```toml `.
- Short and complete: a listing shows one idea in at most ~40 lines; elide with a comment, never with code that would not compile.
- Correct: Python listings must run as shown (run them) using only the standard library, numpy, scipy and matplotlib unless the prose names another package and says it is optional. Quote the printed output where the text uses it. C and C++ must be syntactically valid for the stated standard; where a target is named (an STM32G4, an ESP32-S3, an nRF52840, an RP2040, an ATmega328P) register and API names must be plausible for it and marked as illustrative when not a vendor's exact header. Structured Text must follow IEC 61131-3 syntax.
- Code is explained in prose, not by comment walls.

## Voice and method

1. **Start from the system and the problem**, not a definition. Draw systems from across the field: consumer devices, instrumentation and test, automotive and EV, industrial automation and process control, building services, data centres, telecom and IoT, medical devices, aerospace and drones, robotics, renewable and power systems, research labs.
2. **Requirement → design → verification.** Every design decision is traced to a requirement and closed by a test with a limit. Say what was measured (or simulated) and against what.
3. **Every concept gets an engineering destination.** The opening table maps concepts to where an engineer uses them.
4. **Status box after every important law, rule or design rule**, using exactly one of four labels:
   - **Fundamental** — follows from physical law or from the definition of the system (energy conservation in a power budget, the Nyquist rate for alias-free sampling, Friis transmission in free space as the starting point of a link budget).
   - **Derived** — a mathematical consequence of more basic results (root-sum-square combination of independent uncertainties, odometry from wheel increments, battery runtime from capacity and average current, PV string voltage at the coldest cell temperature, amplifier noise referred to the input).
   - **Approximate** — valid under stated simplifying assumptions (lumped thermal model of an enclosure, constant-efficiency converter model, Peukert-free battery capacity, small-angle linearised attitude model, quasi-static power-flow model of a microgrid). State the assumptions and the domain.
   - **Empirical** — fitted to observation or set by practice (derating rules, the 10 °C electrolytic-life rule, cycle-life versus depth-of-discharge curves, PV performance ratios, path-loss exponents, rules of thumb for test coverage or schedule overrun, ML scaling of error with data).

   Format:
   ```
   > **Status of the principle: Name**
   > *Derived.* One sentence on why and where it holds.
   ```
5. **Show why a design works, then where it fails.** A failure is missing physics, a violated assumption, a budget exceeded, an interface misunderstood or a test not run — never bad luck. Each chapter's failure analysis names the mechanism and the change it caused.
6. **Real numbers and real parts.** Tables of representative values with units: sensor accuracies and drifts, ADC ENOB and sample rates, MCU currents per power mode, radio sensitivities and currents, motor constants, PLC scan times, VFD ratings, PV module coefficients, cell capacities and resistances, EV consumptions, link margins, inference latencies, solver run times. Name real part classes where useful (a PT1000 in a 4-wire connection, an ADS1263, an INA228, an STM32G474, an nRF52840, an ESP32-S3, a DRV8833, an AS5600, an MPU-6050/ICM-42688, a Siemens S7-1200-class PLC, a 60-cell 330 W module, an LFP 280 Ah prismatic cell, an SX1262 LoRa transceiver, an ADS1298 ECG front end). Say "typical" or give ranges where values vary. Cite the standard where a limit comes from one (IEC 60751, IEC 61131-3, IEC 61508/62061/ISO 13849, IEC 60204-1, IEC 62443, IEC 61730/61215, IEC 62109, IEC 62619, UN 38.3, ISO 26262, IEC 61851, IEC 60601-1, IEC 61000, IEEE 1547, ETSI EN 300 220, ISO/IEC 17025, GUM/JCGM 100). Prices are indicative and dated ("2026 distributor price, 100 pcs").
7. **Worked examples** as `**Worked example — title.**` paragraphs with full numbers (or a short listing and its computed result). At least three per chapter; Part IX chapters typically have more. Recompute every number.
8. **Respect the boundaries** (see the tables at the end of `TOC.md`). Recap a result from a sibling book in a sentence and use it; never re-derive it. Add a short `> **Boundary.**` note where a chapter leans on another book, with a link to the exact chapter and section.
9. Do not overclaim. State domains of validity, and say when a result is simulated rather than measured.

## Cross-references to the sibling books

When a chapter uses theory owned by another book, cite the exact chapter (and section where useful) with a link. Link targets:

- *Engineering Physics: Top Down* — `https://github.com/The-Studio-of-Sadiq/Engineering-Physics/blob/main/CHAPTERS/CHAPTER%20N.md`, cited as *Engineering Physics*, Ch. N §N.k.
- *Circuits, Signals and Communications* (Book 3) — `https://github.com/The-Studio-of-Sadiq/Circuits-Signals-and-Communications/blob/main/<part folder>/<NN-slug>.md`, cited as *Circuits, Signals and Communications*, Ch. N.
- *Electronics and Computing* (Book 4) — `https://github.com/The-Studio-of-Sadiq/Electronics-and-Computing/blob/main/<part folder>/<NN-slug>.md`, cited as *Electronics and Computing*, Ch. N.
- *Electrical Energy and Machines* (Book 5) — `https://github.com/The-Studio-of-Sadiq/Electrical-Energy-and-Machines/blob/main/<part folder>/<NN-slug>.md`, cited as *Electrical Energy and Machines*, Ch. N.
- *Materials Science and Engineering* — `https://github.com/The-Studio-of-Sadiq/Materials-Science-and-Engineering/blob/main/Chapters/CHAPTER%20N.md`, cited as *Materials Science and Engineering*, Ch. N.
- *The Mathematics Universe* — `https://github.com/The-Studio-of-Sadiq/engineering-mathematics/blob/main/<part folder>/<NN-slug>.md`, cited as *The Mathematics Universe*, Ch. N.

### Integrate the sibling books, do not repeat them

- **Do not re-derive** circuit laws and theorems, transient and AC analysis, Laplace and Bode analysis, transmission-line theory, the sampling theorem, the DFT, digital-filter design, modulation and noise theory, control design (root locus, Nyquist, PID tuning theory, state space), device physics and device models, op-amp circuit analysis, ADC/DAC architectures, computer architecture, RTOS scheduling theory, converter topologies and their steady-state equations, machine equivalent circuits, FOC/DTC, power-flow and fault analysis, protection theory, or the mathematics of numerical methods, statistics and optimisation. State the result in one line (at most one displayed equation), cite it with a link, and move on to using it.
- **Add what the sibling books do not have**: the design procedure, the choice among real parts, the budget, the interface, the code, the test, the failure, and the second iteration.

| Topic used in this book | Owned by (exact place) |
|---|---|
| Circuit laws, network analysis and theorems | *Circuits, Signals and Communications* Ch. 2–4 (`part-1-circuit-fundamentals/`) |
| Capacitors, inductors, first- and second-order transients | Book 3 Ch. 5–7 |
| Phasors, AC power, three-phase circuits | Book 3 Ch. 8–10 (`part-2-transient-and-ac-analysis/`) |
| Laplace domain, two-ports, frequency response and Bode plots, transmission lines | Book 3 Ch. 11–14 (`part-3-advanced-network-theory/`) |
| Signals and systems, LTI systems, sampling and reconstruction | Book 3 Ch. 15–20 (`part-4-signals-and-systems/`) |
| DSP fundamentals, DFT/FFT, digital filters, advanced DSP | Book 3 Ch. 21–24 (`part-5-digital-signal-processing/`) |
| Communication theory, digital modulation, coding, noise, wireless, optical, RF and microwave | Book 3 Ch. 25–32 (`part-6-communication-theory/`) |
| Dynamic-system modelling, feedback and stability, controller design | Book 3 Ch. 33–35 (`part-7-control-system-fundamentals/`) |
| Devices (diodes, BJTs, MOSFETs, IGBTs, wide-bandgap) | *Electronics and Computing* Ch. 1–5 (`part-1-electronic-devices/`) |
| Op-amps, feedback amplifiers, oscillators, analog ICs (references, ADC/DAC circuits) | Book 4 Ch. 8–10 (`part-2-analog-electronics/`) |
| Digital logic and digital system design | Book 4 Ch. 11–15 (`part-3-digital-electronics/`) |
| Computer architecture, microcontrollers, memory, FPGAs, HDLs | Book 4 Ch. 16–19 (`part-4-computer-architecture-and-digital-hardware/`) |
| C/C++, Python, algorithms, scientific computing | Book 4 Ch. 20–24 (`part-5-programming-and-computational-systems/`) |
| Embedded architecture, interfaces (UART, SPI, I²C, CAN, USB), real-time computing, embedded design | Book 4 Ch. 25–28 (`part-6-embedded-and-real-time-systems/`) |
| Power-electronic fundamentals, DC–DC, rectifiers and inverters, motor-drive power stages | Book 4 Ch. 29–32 (`part-7-power-electronics/`) |
| CMOS, VLSI, hardware–software co-design, embedded AI hardware | Book 4 Ch. 33–35 (`part-8-integrated-circuits-and-vlsi/`) |
| Magnetic circuits, induction, energy conversion | *Electrical Energy and Machines* Ch. 1–3 (`part-1-magnetic-circuits-and-energy-conversion/`) |
| Transformers, DC, induction, synchronous and special machines (BLDC, PMSM, stepper, SRM) | Book 5 Ch. 4–9 (`part-2-transformers-and-electrical-machines/`) |
| Drive fundamentals, DC drives, AC drives (V/f, FOC, DTC) | Book 5 Ch. 10–12 (`part-3-motor-drives/`) |
| Renewable generation and energy storage at system level | Book 5 Ch. 15–16 (`part-4-power-generation/`) |
| Power-flow, fault and stability analysis | Book 5 Ch. 17–20 (`part-5-power-system-analysis/`) |
| Distribution systems and protection | Book 5 Ch. 22–23 (`part-6-transmission-distribution-and-protection/`) |
| Power quality, smart grids, grid integration of renewables, energy management | Book 5 Ch. 25–28 (`part-7-power-quality-and-grid-modernization/`) |
| Electrical safety, earthing, installation and cable design | Book 5 Ch. 29–30 (`part-8-electrical-safety-and-engineering-practice/`) |
| Lumped-element (effort–flow) modelling across domains | *Engineering Physics* Ch. 17 |
| Circuits, devices and signals from physics (sketch) | *Engineering Physics* Ch. 18 |
| Machines, structures and thermofluid systems | *Engineering Physics* Ch. 19 |
| Feedback and control across domains | *Engineering Physics* Ch. 21 |
| Heat transfer and thermoelectrics (thermal resistance, Seebeck effect) | *Engineering Physics* Ch. 14 |
| Optics and photonics (photodetectors, LEDs) | *Engineering Physics* Ch. 12 |
| Sensor, piezo-, magnetic and smart materials | *Materials Science and Engineering* Ch. 27, 28–29, 37 |
| Materials for energy (battery and PV materials) | *Materials Science and Engineering* Ch. 40 |
| Degradation, corrosion and failure analysis | *Materials Science and Engineering* Ch. 42–44 |
| Packaging and interconnect materials | *Materials Science and Engineering* Ch. 51 |
| Biomaterials | *Materials Science and Engineering* Ch. 39 |
| Linear algebra, eigenvalues | *The Mathematics Universe* Ch. 8–10 (`part-3-linear-algebra/`) |
| ODEs and PDEs | *The Mathematics Universe* Ch. 11–13 (`part-4-differential-equations/`) |
| Probability, statistics, random processes | *The Mathematics Universe* Ch. 19–21 (`part-6-probability-statistics/`) |
| Numerical methods, optimisation, computational mathematics, mathematical modelling | *The Mathematics Universe* Ch. 22–25 (`part-7-numerical-computational/`) |

Before writing, open the chapters in this table that your chapter touches and skim them, so you know exactly what is covered there and how; cite the real section numbers you saw.

## Figure markers

Planned figures are recorded in the chapter as an HTML comment on its own line, at the exact point the figure should appear (invisible in the PDF until the figure exists):

```
<!-- FIGURE 22.3 | figures/ch22/fig-22-3-string-voltage-window.png | plot | Caption sentence. | Content: what is drawn, axes, data ranges, labels. -->
```

Fields: number, target path, kind (`plot`, `circuit`, `schematic`, `block-diagram`, `timing-diagram`, `state-diagram`, `waveform`, `flowchart`, `layout`, `wiring-diagram`, `kinematic-diagram`, `table-graphic`), caption, and a brief content spec for whoever draws it. Captions and specs must not contain the `|` character.

Figures are drawn by `figures/scripts/chNN.py` (shared style in `figures/scripts/figstyle.py`; circuit drawings may use `schemdraw`, including its flowchart and timing-diagram modules) and saved to the marker's path. `node scripts/insert-figures.mjs` then places each drawn figure directly below its marker; the marker stays as the figure's specification:

```
<!-- FIGURE 22.3 | ... -->

![Figure 22.3 — Caption](../figures/ch22/fig-22-3-string-voltage-window.png)

*Figure 22.3 — Caption.*
```

The full plan is collected in [`FIGURES.md`](FIGURES.md) (`node scripts/figure-plan.mjs`).
