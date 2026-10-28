# Changelog

All notable changes to *Applications and Integrations*. Dates are ISO 8601. Versions follow the tags in this repository; each release attaches the compiled PDF.

## [1.0.0] — 2026-10-28

First complete edition.

### Added
- **Part I — Engineering Design Methodology** (Chapters 1–5): requirements and traceability, system architecture, modelling and simulation workflow, prototyping and verification, engineering documentation. Running systems: CCM-1, an LTE-M vaccine-refrigerator monitor (Ch. 1–3), and PM-4, a 12 V rack power monitor (Ch. 4–5).
- **Part II — Instrumentation and Measurement Systems** (6–9): sensors and transducers on a motor test bench, an isolated strain-gauge module, a distributed dynamometer DAQ, and eight compact laboratory instrumentation projects.
- **Part III — Embedded and Connected Systems** (10–12): a smart radiator valve, a pharmacy cold-chain IoT fleet, and an edge-AI pump condition monitor.
- **Part IV — Robotics and Mechatronics** (13–17): a 6-axis lab arm, a hospital delivery robot and its motor-control board, an inspection quadcopter, and a collaborative-arm integration programme.
- **Part V — Industrial Automation** (18–21): a water-treatment control system, a dairy CIP skid, a quarry conveyor MCC, and a palletising cell's networks and functional safety.
- **Part VI — Renewable Energy and Electric Mobility** (22–25): an 11 kWp school PV roof, a 215 kWh LFP battery cabinet, an urban delivery van, and a hospital microgrid.
- **Part VII — Communications, Signal Processing, and Biomedical Applications** (26–28): a LoRaWAN water-utility network, a pump-vibration DSP node, and a seven-day ambulatory ECG recorder.
- **Part VIII — Engineering Software and Computational Tools** (29–33): a reproducible buck-converter design workflow, a heatsink design computation, the FeederCheck cable-sizing tool, transformer-fleet machine learning, and a pump-set digital twin.
- **Part IX — Interdisciplinary Engineering Projects** (34–40): line-following robot, smart energy monitor, solar battery system for a health post, 400 W PMSM servo drive, vineyard frost-monitoring sensor network, PCB thermal simulation tool, and the AquaSol capstone.
- Every chapter in Parts II–IX carries one reference system through requirements, architecture, budgets, component selection, implementation, verification and FMEA; Part IX adds BOMs, test results and a Revision B.
- Nine part openers; boundaries inside the book and with Books 3–5 and the foundation books in `TOC.md`.
- Code listings in C, C++, Python and IEC 61131-3 Structured Text; every Python listing runs and prints the output quoted in the text.
- 225 figures, each drawn by a reproducible script in `figures/scripts/chNN.py` from the chapter's own numbers; figure plan in `FIGURES.md`.
- `pdf/Applications-and-Integrations.pdf` with clickable contents, PDF bookmarks and KaTeX math, built by `scripts/build-pdf.mjs`.
- MCP server (`mcp/server.mjs`) to list, read, search and typeset the book and fetch its figures.
- Book checks (`scripts/check-book.mjs`), CI and release workflows, issue and pull-request templates, community files, citation file, social preview image and wiki generator.

### Fixed (before release, from figure-agent cross-checks)
- Ch. 1–4: Listing 3.2 output and supercapacitor margin; adaptive-reporting battery life; function-to-requirement allocation of F8 (Figure 2.1 redrawn); thermal time constants; validation residuals and crossings; shunt-current wording.
- Ch. 5–8: decoupling distance and address straps; uncertainty totals; isolation-barrier capacitance; bridge output swing; DAQ packet count (Figure 8.5 redrawn), time-alignment budget and host-stall test result.
- Ch. 9–12: M/T speed quantisation; energy-meter base current; stall margin and battery dip; BOOT state in the valve FSM; TLS budget; LoRaWAN duty cycle and alarm counts.
- Ch. 13–16: joint-move arc direction; IK residual; gear speed limit; settling budget; robot energy shares; regenerative bus balance with hotel loads (Figure 15.6 redrawn); cascade bandwidths (Figure 16.4 redrawn).
- Ch. 17–20: CAN FD bus load; joint FSM stop-timeout fault and reset (listing); brake-chopper timings; commissioning effort; contactor ratings; RTD versus thermocouple ranges; feed-loop dead time.
- Ch. 21–24: brake-test limit; CAN load; DC cabling loss (Figures 22.4–22.5 redrawn); rack current sharing and system limit (Figure 23.2 redrawn); cold pack resistance; regenerative efficiency chain.
- Ch. 25–28: microgrid surplus window and dispatch; link margins and antenna coverage; DSP cycle budget; ECG recorder energy budget; QRS test record length (Figure 28.6 redrawn).
- Ch. 29–32: loss-model and load-step wording; fin efficiency; project-file exception path; heat-wave dates.
- Ch. 33–36: solver step sizes; line-sensor threshold in firmware; energy-meter low-PF test point and calibration residuals (Figure 35.4 redrawn); solar-system critical load, ripple and LCOE.
- Ch. 37–40: MOSFET edge times; duty-cycle limit from current sampling; belt-resonance inertia split and notch width; wet-bulb value; spreading-factor assignment (Figure 38.3 redrawn); delivery ratio; LU scaling; transient validation table.
