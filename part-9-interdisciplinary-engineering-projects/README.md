# Part IX — Interdisciplinary Engineering Projects

Parts I to VIII built the methods and the subsystems one at a time. Part IX puts them together. Each chapter is one complete project, carried from a problem statement to a tested system: requirements with IDs, an architecture, budgets with margins, real parts, design calculations, firmware or tool code, a test plan with limits, test results, a bill of materials with indicative cost, a failure analysis and a closing "Revision B" that says what the next iteration would change and why. The projects differ in kind (a fast mobile robot, a mains-connected instrument, an energy system, a motor drive, a radio network, a piece of engineering software, and the method for a capstone of the reader's own). Theory is not repeated: each chapter points back to the chapter that owns a method and to the sibling book that owns the physics, and spends its pages on integration decisions and on what went wrong in the first build.

## By the end of this part you should understand

- How stakeholder needs become requirements that each end in a test with a numerical limit.
- How power, energy, timing, accuracy, mass and cost budgets are written before the build and closed by measurement.
- How to choose among real part classes against the requirements, and record why.
- Why first prototypes fail where they do (missing lag in a control loop, a phase error invisible at unity power factor, a battery sized without derating, a radio budget without fade margin) and how failure analysis turns those findings into design changes.
- How subsystems are verified separately and then together, and how results are reported with their uncertainty.
- How a complete project is documented so that someone else could rebuild it, test it and improve it.

## Chapters

| Chapter | Central question | What it delivers |
|---|---|---|
| [34 — Project: Autonomous Line-Following Robot](34-project-autonomous-line-following-robot.md) | Which sensor geometry, motors and control structure let a 170 g robot lap a 15 m track in under 10 s without leaving the line? | Sensor and motor selection, circuit, 1 kHz firmware, gain-scheduled cascade control, power budget, track tests, speed profile |
| [35 — Project: Smart Energy Monitor](35-project-smart-energy-monitor.md) | How do a CT, a divider and a 24-bit ADC become a safe, connected energy measurement good to class 1 at PF 0.5? | Front end and error budget, power calculation, metrology firmware, logging, MQTT, calibration, isolation, IEC 62053-21 validation |
| [36 — Project: Solar Battery System](36-project-solar-battery-system.md) | How are PV array, battery and converters sized so that an off-grid or hybrid load is served through the worst month at an acceptable cost? | Load estimate, PV and battery sizing, converters, charge control, protection, monitoring, efficiency, life-cycle cost |
| [37 — Project: Closed-Loop Motor Drive](37-project-closed-loop-motor-drive.md) | How is a motor characterised and driven so that speed and current loops meet their specifications with the protection a real drive needs? | Motor characterisation, encoder, power stage, sensing, controller design, firmware, protection, performance tests |
| [38 — Project: Wireless Sensor Network](38-project-wireless-sensor-network.md) | How do battery-powered nodes deliver their data reliably and securely for years from a real site? | Node architecture, protocol, energy budget, acquisition, reliability, security, deployment and field tests |
| [39 — Project: Engineering Simulation Tool](39-project-engineering-simulation-tool.md) | How is an engineering calculation turned into a tool that others can trust, run and maintain? | Equations, solver, input validation, visualisation, benchmarks, verification, documentation, reproducibility |
| [40 — Capstone Engineering Project](40-capstone-engineering-project.md) | How does a reader run a project of their own from problem selection to final report? | The capstone method tied to Part I, a project-report template, cost and risk analysis, and one capstone worked through end to end |

## How this part connects to the rest of the book

Every project leans on Part I: requirements (Chapter 1), architecture (Chapter 2), modelling (Chapter 3), verification (Chapter 4) and documentation (Chapter 5). Each then draws on the part that owns its subsystems: the line follower on Chapters 14 and 15; the energy monitor completes Chapter 9's compact project using Chapters 7, 8 and 11; the solar battery system applies Chapters 22, 23 and 25; the motor drive builds on Chapter 15 and Part V; the sensor network applies Chapters 11, 21 and 26; the simulation tool applies Chapters 29 to 31 and 33; the capstone uses all of them.

The theory lives in the sibling books and is cited, not re-derived: circuits, signals, sampling and control in [*Circuits, Signals and Communications*](https://github.com/The-Studio-of-Sadiq/Circuits-Signals-and-Communications); devices, microcontrollers, embedded interfaces, real-time computing and power electronics in [*Electronics and Computing*](https://github.com/The-Studio-of-Sadiq/Electronics-and-Computing); machines, drives, storage, power quality and safety in [*Electrical Energy and Machines*](https://github.com/The-Studio-of-Sadiq/Electrical-Energy-and-Machines); physics, materials and mathematics in [*Engineering Physics*](https://github.com/The-Studio-of-Sadiq/Engineering-Physics), [*Materials Science and Engineering*](https://github.com/The-Studio-of-Sadiq/Materials-Science-and-Engineering) and [*The Mathematics Universe*](https://github.com/The-Studio-of-Sadiq/engineering-mathematics).
