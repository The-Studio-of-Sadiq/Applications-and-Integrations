# Applications and Integrations — Master Syllabus

**Book 6 — Applications & Integrations Core**

**Objective:** Teach readers how to combine the other cores into working systems. The book is project-oriented: it does not repeat the theory of the other books. Each chapter explains the architecture, design process, component selection, implementation, verification and failure analysis of a real engineering system.

Structure: 9 Parts · 40 Chapters. Each part is a folder `part-N-<slug>/`: its `README.md` is the part opener and `NN-<slug>.md` is Chapter NN.

The backbone is **design method → measurement → embedded and connected devices → robots → factories → energy and mobility → communications, signals and medicine → engineering software → complete projects**. One idea runs through all of it: a working system is a chain of requirements, interfaces and budgets (power, timing, accuracy, cost, risk), and every link in that chain is verified against a number written down before the build. The theory each link rests on lives in Books 3–5 and the foundation books; this book is where those results are chosen, combined, built, measured and made to fail safely.

---

## Part I — Engineering Design Methodology · `part-1-engineering-design-methodology/`

### Chapter 1. From Requirement to Working System · `01-from-requirement-to-working-system.md`
- Problem definition
- Stakeholder requirements
- Functional requirements
- Nonfunctional requirements
- System boundaries
- Constraints
- Design specifications
- Requirements traceability
- Acceptance criteria

### Chapter 2. System Architecture · `02-system-architecture.md`
- Functional decomposition
- Block diagrams
- Hardware-software partitioning
- Interfaces
- Data flow
- Energy flow
- Control flow
- Modularity
- Trade-off analysis
- Architecture documentation

### Chapter 3. Modeling and Simulation Workflow · `03-modeling-and-simulation-workflow.md`
- Mathematical modeling
- Equivalent circuits
- System-level simulation
- Component-level simulation
- Numerical solver selection
- Model assumptions
- Parameter estimation
- Sensitivity analysis
- Model validation
- Simulation reproducibility

### Chapter 4. Prototyping and Verification · `04-prototyping-and-verification.md`
- Prototype planning
- Breadboarding
- PCB prototyping
- Instrument selection
- Test plans
- Verification versus validation
- Calibration
- Fault diagnosis
- Regression testing
- Design iteration

### Chapter 5. Engineering Documentation · `05-engineering-documentation.md`
- Schematics
- Block diagrams
- Wiring diagrams
- Bill of materials
- Design calculations
- Test reports
- Version control
- Technical documentation
- Revision management
- Reproducibility

## Part II — Instrumentation and Measurement Systems · `part-2-instrumentation-and-measurement-systems/`

### Chapter 6. Sensors and Transducers · `06-sensors-and-transducers.md`
- Temperature sensors
- Pressure sensors
- Position sensors
- Speed sensors
- Force and strain sensors
- Light sensors
- Magnetic sensors
- Current and voltage sensors
- Sensor selection
- Sensor calibration

### Chapter 7. Measurement and Signal Conditioning · `07-measurement-and-signal-conditioning.md`
- Measurement range and resolution
- Accuracy and precision
- Error and uncertainty
- Bridge circuits
- Instrumentation amplifiers
- Filtering
- Isolation
- ADC and DAC selection
- Sampling
- Noise reduction

### Chapter 8. Data Acquisition Systems · `08-data-acquisition-systems.md`
- DAQ architectures
- Sensor interfaces
- ADC performance
- Sampling rates
- Data logging
- Synchronization
- Real-time acquisition
- Serial and network interfaces
- Data storage
- Measurement validation

### Chapter 9. Instrumentation Projects · `09-instrumentation-projects.md`
- Temperature monitoring
- Energy monitoring
- Motor-speed measurement
- Power-quality measurement
- Battery monitoring
- Sensor calibration systems
- Automated test equipment
- Laboratory data-acquisition systems

## Part III — Embedded and Connected Systems · `part-3-embedded-and-connected-systems/`

### Chapter 10. Embedded-System Integration · `10-embedded-system-integration.md`
- Microcontroller selection
- Sensor and actuator interfaces
- Firmware architecture
- Timing constraints
- Power management
- Fault handling
- Communication interfaces
- Debugging and testing

### Chapter 11. IoT Systems · `11-iot-systems.md`
- Device architecture
- Connectivity
- Telemetry
- MQTT and HTTP fundamentals
- Gateways
- Data storage
- Remote monitoring
- Device provisioning
- Authentication
- Security and reliability

### Chapter 12. Edge Computing and Embedded AI · `12-edge-computing-and-embedded-ai.md`
- Edge versus cloud processing
- Resource constraints
- Data preprocessing
- Model deployment
- Quantization
- Inference performance
- Memory and power constraints
- Sensor fusion
- Model validation
- Failure handling

## Part IV — Robotics and Mechatronics · `part-4-robotics-and-mechatronics/`

### Chapter 13. Robotics Fundamentals · `13-robotics-fundamentals.md`
- Robot architectures
- Degrees of freedom
- Coordinate frames
- Forward kinematics
- Inverse kinematics
- Joint and Cartesian motion
- Workspace
- Actuator selection
- Mechanical-electrical integration

### Chapter 14. Mobile Robotics · `14-mobile-robotics.md`
- Differential-drive robots
- Wheel encoders
- Line-following robots
- Obstacle detection
- Odometry
- Path planning fundamentals
- Localization
- Navigation
- Battery and motor sizing
- Robot testing

### Chapter 15. Robot Electronics and Control · `15-robot-electronics-and-control.md`
- Motor drivers
- Encoder interfaces
- Sensor fusion
- Embedded controllers
- PID implementation
- Feedback loops
- Timing and latency
- Communication buses
- Power distribution
- Fault recovery

### Chapter 16. Drones and Aerial Robotics · `16-drones-and-aerial-robotics.md`
- Multirotor architecture
- Brushless motors
- Electronic speed controllers
- Propeller selection
- Flight-controller architecture
- IMUs
- Attitude estimation
- Flight-control loops
- Battery sizing
- Safety and testing

### Chapter 17. Robotic System Integration · `17-robotic-system-integration.md`
- Mechanical design interfaces
- Electronics integration
- Firmware
- Control
- Power distribution
- Communication
- Calibration
- System identification
- Hardware-in-the-loop testing
- Field testing

## Part V — Industrial Automation · `part-5-industrial-automation/`

### Chapter 18. Industrial Control Architecture · `18-industrial-control-architecture.md`
- Industrial control systems
- PLCs
- Remote I/O
- Distributed control systems
- Supervisory control and data acquisition
- Human-machine interfaces
- Industrial networking
- Control panels
- System commissioning

### Chapter 19. Industrial Sensors and Actuators · `19-industrial-sensors-and-actuators.md`
- Proximity sensors
- Limit switches
- Industrial temperature sensors
- Pressure transmitters
- Flow measurement
- Solenoid valves
- Contactors
- Relays
- Pneumatic and hydraulic interfaces
- Industrial motor actuators

### Chapter 20. Industrial Motor Control · `20-industrial-motor-control.md`
- Motor starters
- Contactors
- Overload protection
- Variable-frequency drives
- Speed regulation
- Interlocks
- Emergency stops
- Fault monitoring
- Control-panel design
- Commissioning

### Chapter 21. Industrial Communication and Safety · `21-industrial-communication-and-safety.md`
- Modbus
- CAN-based industrial networks
- Industrial Ethernet
- Fieldbus fundamentals
- Network diagnostics
- Functional safety fundamentals
- Safety interlocks
- Fail-safe behavior
- Industrial cybersecurity
- Maintenance documentation

## Part VI — Renewable Energy and Electric Mobility · `part-6-renewable-energy-and-electric-mobility/`

### Chapter 22. Solar PV System Design · `22-solar-pv-system-design.md`
- Solar resource assessment
- PV module characteristics
- String sizing
- Inverters
- MPPT
- Battery integration
- Protection
- Cable sizing
- System losses
- Performance evaluation

### Chapter 23. Battery Energy Systems · `23-battery-energy-systems.md`
- Battery-pack architecture
- Cell selection
- Series and parallel configurations
- Battery-management systems
- State estimation
- Thermal management
- Charging
- Protection
- Degradation monitoring
- Safety testing

### Chapter 24. Electric Vehicles · `24-electric-vehicles.md`
- EV architecture
- Traction motors
- Inverters
- DC–DC converters
- Battery packs
- Charging systems
- Regenerative braking
- Vehicle energy consumption
- Thermal constraints
- Charging infrastructure

### Chapter 25. Microgrids and Hybrid Energy Systems · `25-microgrids-and-hybrid-energy-systems.md`
- Solar-wind-storage integration
- Hybrid architectures
- Load profiles
- Energy management
- Grid-connected operation
- Islanded operation
- Inverter coordination
- Protection
- Reliability
- Economic evaluation

## Part VII — Communications, Signal Processing, and Biomedical Applications · `part-7-communications-signal-processing-and-biomedical/`

### Chapter 26. Communication-System Integration · `26-communication-system-integration.md`
- RF front-end architecture
- Antenna selection
- Transceiver interfaces
- Link budgets
- Channel constraints
- Wireless sensor networks
- Communication reliability
- Interference mitigation
- System testing

### Chapter 27. Practical Signal Processing · `27-practical-signal-processing.md`
- Sensor-noise reduction
- Filtering
- Spectral analysis
- Feature extraction
- Event detection
- Audio processing
- Image processing
- Real-time DSP
- Embedded implementation
- Performance evaluation

### Chapter 28. Biomedical Instrumentation · `28-biomedical-instrumentation.md`
- Biopotential measurement
- ECG acquisition
- EMG acquisition
- Biomedical sensors
- Isolation and safety
- Signal conditioning
- Noise rejection
- Medical data acquisition
- Basic biomedical signal analysis
- Regulatory and ethical considerations

## Part VIII — Engineering Software and Computational Tools · `part-8-engineering-software-and-computational-tools/`

### Chapter 29. Engineering Software Workflows · `29-engineering-software-workflows.md`
- Requirements and modeling
- Numerical computation
- Circuit simulation
- System simulation
- Version-controlled projects
- Reproducible builds
- Automated testing
- Data import and export
- Results visualization
- Engineering documentation

### Chapter 30. Scientific and Engineering Computing · `30-scientific-and-engineering-computing.md`
- Numerical solvers
- Parameter sweeps
- Optimization
- Simulation automation
- Data processing
- Computational performance
- Parallel processing
- Verification of numerical results
- Model validation
- Scientific data management

### Chapter 31. Engineering Software Architecture · `31-engineering-software-architecture.md`
- Modular software design
- Domain models
- File-based project formats
- Plugin versus built-in architecture
- APIs and interfaces
- GUI design
- Data interoperability
- Version control
- Automated testing
- Long-term maintainability

### Chapter 32. AI and Machine Learning for EEE · `32-ai-and-machine-learning-for-eee.md`
- Engineering datasets
- Data cleaning
- Feature engineering
- Regression
- Classification
- Time-series forecasting
- Anomaly detection
- Surrogate models
- Physics-informed modeling
- Model evaluation
- Uncertainty
- Deployment constraints

### Chapter 33. Engineering Simulation and Digital Twins · `33-engineering-simulation-and-digital-twins.md`
- Physical-system models
- Numerical simulation
- Model calibration
- Co-simulation
- Digital-twin architectures
- Real-time data integration
- Parameter estimation
- Validation
- Uncertainty quantification
- Simulation-based design

## Part IX — Interdisciplinary Engineering Projects · `part-9-interdisciplinary-engineering-projects/`

### Chapter 34. Project: Autonomous Line-Following Robot · `34-project-autonomous-line-following-robot.md`
- Requirements
- Sensor selection
- Motor selection
- Circuit design
- Embedded firmware
- Control algorithm
- Power budgeting
- Testing
- Performance optimization

### Chapter 35. Project: Smart Energy Monitor · `35-project-smart-energy-monitor.md`
- Voltage and current measurement
- Signal conditioning
- Power calculations
- Embedded processing
- Data logging
- Communications
- Calibration
- Safety
- Validation

### Chapter 36. Project: Solar Battery System · `36-project-solar-battery-system.md`
- Load estimation
- PV sizing
- Battery sizing
- Converter selection
- Charge control
- Protection
- Monitoring
- Efficiency
- Economic assessment

### Chapter 37. Project: Closed-Loop Motor Drive · `37-project-closed-loop-motor-drive.md`
- Motor characterization
- Encoder integration
- Power stage
- Current and speed measurement
- Controller design
- Firmware
- Protection
- Performance testing

### Chapter 38. Project: Wireless Sensor Network · `38-project-wireless-sensor-network.md`
- Sensor selection
- Node architecture
- Communication protocol
- Power budgeting
- Data acquisition
- Network reliability
- Security
- Deployment and testing

### Chapter 39. Project: Engineering Simulation Tool · `39-project-engineering-simulation-tool.md`
- Problem definition
- Governing equations
- Numerical solver
- Input validation
- Visualization
- Benchmarking
- Verification
- Documentation
- Reproducible results

### Chapter 40. Capstone Engineering Project · `40-capstone-engineering-project.md`
- Problem selection
- Literature review
- Requirements
- Architecture
- Detailed design
- Implementation
- Verification and validation
- Cost analysis
- Risk assessment
- Final technical report

---

## Boundaries inside this book

Parts I–VIII own the methods and the subsystems; Part IX applies them end to end to one concrete design each and points back instead of repeating them.

| Topic | Owned by | Applied (not repeated) in |
|---|---|---|
| Requirements, traceability, acceptance criteria | Ch. 1 | every chapter; Ch. 34–40 |
| Architecture, interfaces, trade studies | Ch. 2 | Ch. 10, 17, 18, 25, 31, 34–40 |
| Modeling, simulation, sensitivity, validation workflow | Ch. 3 | Ch. 30, 33, 39 |
| Prototyping, test plans, calibration procedure, regression | Ch. 4 | Ch. 9, 17, 34–40 |
| Schematics, BOMs, test reports, revision control | Ch. 5 | Ch. 29, 40 |
| Sensor principles and selection | Ch. 6 | Ch. 14, 16, 19, 28, 34, 38 |
| Signal conditioning, uncertainty, ADC selection | Ch. 7 | Ch. 8, 9, 28, 35 |
| DAQ architecture, logging, synchronisation | Ch. 8 | Ch. 9, 17, 35, 38 |
| Short instrumentation projects (temperature, energy, speed, power quality, battery, calibration rigs, ATE) | Ch. 9 | energy monitor in full: Ch. 35 |
| MCU selection, firmware architecture, timing, fault handling | Ch. 10 | Ch. 15, 16, 34, 35, 37, 38 |
| IoT device, connectivity, MQTT/HTTP, provisioning, security | Ch. 11 | Ch. 35, 38 |
| Edge inference, quantisation, embedded AI | Ch. 12 | Ch. 32 (training side) |
| Kinematics, frames, actuator selection | Ch. 13 | Ch. 14, 16, 17 |
| Differential drive, odometry, line following, navigation | Ch. 14 | line follower in full: Ch. 34 |
| Motor drivers, encoders, PID implementation, robot buses | Ch. 15 | Ch. 16, 17, 34, 37 |
| Multirotor design and flight control | Ch. 16 | — |
| Robot integration, system identification, HIL, field tests | Ch. 17 | Ch. 33, 34 |
| PLCs, DCS, SCADA, HMIs, panels, commissioning | Ch. 18 | Ch. 19–21 |
| Industrial sensors and actuators | Ch. 19 | Ch. 20 |
| Starters, overloads, VFDs, interlocks, E-stops | Ch. 20 | Ch. 21 |
| Modbus, CAN, industrial Ethernet, functional safety, OT security | Ch. 21 | Ch. 38 |
| PV design | Ch. 22 | Ch. 25, 36 |
| Battery packs, BMS, state estimation | Ch. 23 | Ch. 24, 25, 36 |
| EV system integration | Ch. 24 | — |
| Microgrids and hybrid systems, energy management | Ch. 25 | Ch. 36 |
| RF front ends, antennas, link budgets, WSN radios | Ch. 26 | Ch. 11, 38 |
| Practical filtering, spectral analysis, features, embedded DSP | Ch. 27 | Ch. 28, 32, 35 |
| Biomedical front ends, patient safety, regulation | Ch. 28 | — |
| Engineering software workflow, reproducible builds, testing | Ch. 29 | Ch. 39 |
| Solvers, sweeps, optimisation, performance, numerical verification | Ch. 30 | Ch. 33, 39 |
| Software architecture of engineering tools | Ch. 31 | Ch. 39 |
| Machine learning for engineering data | Ch. 32 | Ch. 12 (deployment), Ch. 33 |
| Digital twins, co-simulation, calibration, UQ | Ch. 33 | Ch. 40 |
| Complete projects | Ch. 34–39 | Ch. 40 (capstone method) |

## Boundary

This book owns engineering design method, system architecture and integration, component selection, verification and validation, and complete application systems: instrumentation, embedded and IoT devices, robots and drones, industrial automation, PV, battery, EV and microgrid systems, communication links, practical DSP, biomedical front ends, engineering software and digital twins. It owns the *integration* decisions — which device, which interface, which budget, which test — and the failure analysis of the assembled system. The theory under each subsystem is cited from the book that owns it, in one line with a link, and never re-derived.

## Relation to the other books

| Topic | Where it lives |
|---|---|
| Linear algebra, ODEs and PDEs, transforms, probability and statistics, numerical methods and optimisation (the mathematics itself) | The Mathematics Universe |
| Mechanics, electromagnetism, thermodynamics, heat transfer, optics, lumped-element modelling (the physics itself) | Engineering Physics |
| Material properties (conductors, dielectrics, magnets, semiconductors, battery and PV materials), corrosion and degradation, packaging | Materials Science and Engineering |
| Circuit laws, transients, AC analysis, Laplace domain, frequency response, transmission lines, signals and systems, sampling, DFT, digital filters, communication theory, RF, noise, modelling and feedback control theory | Circuits, Signals and Communications (Book 3) |
| Devices, analog and digital circuits, op-amps, ADC/DAC circuits, computer architecture, microcontrollers, embedded interfaces (UART, SPI, I²C, CAN), RTOS and scheduling, C/C++ and Python, scientific computing, power-electronic converters, inverters and motor-drive power stages | Electronics and Computing (Book 4) |
| Machines, drive control (V/f, FOC, DTC), generation, energy storage, power-system analysis, protection, power quality, grid integration of renewables, smart grids, electrical safety and installation design | Electrical Energy and Machines (Book 5) |
| Requirements to working systems: design method, instrumentation, embedded and IoT systems, robotics, industrial automation, renewable and EV systems, communication and biomedical integration, engineering software, digital twins and complete projects | **This book** |
