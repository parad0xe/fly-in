_This project has been created as part of the 42 curriculum by nlallema_

# Fly-In

![ci workflow](https://github.com/parad0xe/fly-in/actions/workflows/ci.yml/badge.svg)

## Table of contents

- [Description](#description)
- [Usage](#usage)
- [Algorithm](#algorithm)
- [Visual Representation](#visual-representation)
- [Resources](#resources)

## Description

Developed in Python, this project focuses on designing an efficient routing system to navigate a fleet of drones from a start zone to an end zone in the fewest possible simulation turns. The simulation takes place within a graph representing a network of connected zones. The pathfinding algorithm must dynamically handle different zone types (such as restricted or priority zones) while strictly respecting maximum capacity constraints for both the zones and their connections.

## Usage

To **install** the project's dependencies and virtual environment:

```bash
make install
```

To run the main program:

```bash
make run ARGS="<file> [-v | -vv]"
```

### Arguments & Options

| Argument / Flag | Description |
|-----------------|-------------|
| file | The path to the map file to be solved. |
| -v | Run with INFO logging level. |
| -vv | Run with DEBUG logging level. |

### Development commands

| Command | Description |
|--------|-------------|
| make tests | Run the test suite. |
| make clean | Remove temporary files and project caches. |
| make lint | Check code against flake8 and mypy norms. |
| make lint-strict | Check code against strict flake8 and mypy norms. |
| make debug | Run the program using the Python built-in debugger. |

## Algorithm

The solver's implementation is based on a combination of the LaCAM (Lazy Constraints Addition search for MAPF) and PIBT (Priority Inheritance with Backtracking) algorithms.

**LaCAM** is a search-based, sub-optimal, complete, quick, and scalable MAPF (Multi-Agent Path Finding) algorithm. It utilizes a two-level search strategy to find solutions efficiently:

- **Low-level:** Searches for valid configurations based on agents' location constraints.  
- **High-level:** Searches for a sequence of all agents' locations, strictly following the constraints established by the low-level search.

**PIBT** repeats one-timestep prioritized planning until the goal is reached. At every timestep:

1. Each agent first updates its unique priority.  
2. Agents sequentially determine their next location in decreasing order of priority, avoiding nodes that have already been requested by higher-priority agents.

*Note:* Prioritization alone can still cause deadlocks (e.g., when a stuck agent cannot move anywhere without colliding with other agents). PIBT relies on its backtracking mechanism to resolve these specific deadlock scenarios.

### Implementation choices

The decision to implement the LaCAM algorithm is primarily driven by the need for scalability, rather than brute-forcing all possible path combinations. Although classified as a sub-optimal algorithm, its integration with PIBT provides exceptional speed and local conflict resolution. This combination allows the system to seamlessly adapt to much larger graphs and easily manage a significantly higher number of agents (drones).

### Implementation strategy

While LaCAM and PIBT provide the core pathfinding mechanics, they were specifically adapted to handle the project's unique constraints:
- **Zone Types:** The algorithms evaluate path lengths and movement costs, prioritizing `priority` zones (cost 1) while correctly managing the delayed traversal of `restricted` zones (cost 2) without allowing drones to wait on the connections.
- **Capacities:** The low-level search strictly enforces `max_drones` for zone occupancy and `max_link_capacity`.

## Visual representation

To enhance the user experience and provide a clear understanding of the simulation, a graphical interface was built using PyQt6. The visualizer features:

- **Interactive Map:** A fully navigable map with camera zoom and panning capabilities to easily explore complex graphs.  
- **Live Animations:** Smooth animations displaying the drones (agents) moving along their computed paths toward the solution.  
- **Information Overlays:** Detailed data overlays for each item (zones, connections, agents) to easily monitor constraints, capacities, and types.  
- **Keymap Management:** Custom keyboard shortcuts to control the simulation playback and camera efficiently.

### Visualizer controls

| Key | Action |
|-----|--------|
| A | Move to the previous step in the simulation. |
| D | Move to the next step in the simulation. |
| R | Reset the simulation to the initial state. |
| Space | Toggle auto-running the simulation (play/pause). |
| Q | Quit the application. |

## Resources

### AI usage

As per the project guidelines, AI tools were utilized during the development of this project for:

- **Documentation:** Generating and refining the project's documentation and README.md.  
- **Testing:** Assisting in the generation of test cases to ensure code reliability and handle edge cases.  
- **Research & Comprehension:** Breaking down and explaining complex concepts from research papers related to the LaCAM and PIBT algorithms.

### Qt / PyQt

[Web: PyQt6 Documentation](https://doc.qt.io/qtforpython-6/PySide6/)\
[Web: Qt Matrix m11](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTransform.html#PySide6.QtGui.QTransform.m11)\
[Web: Qt Style Sheets](https://doc.qt.io/qtforpython-6/overviews/qtwidgets-stylesheet.html#qt-style-sheets)\
[Web: Qt Signals (pyqtSignal)](https://www.tutorialspoint.com/pyqt/pyqt_new_signals_with_pyqtsignal.htm)

### Maximum flow algorithms

[Web: Push-Relabel Algorithm](https://cp-algorithms.com/graph/push-relabel.html)\
[Web: Push-Relabel Algorithm (Improved Version)](https://cp-algorithms.com/graph/push-relabel-faster.html)\
[PDF: A Second Course – The Push-Relabel Algorithm](https://timroughgarden.org/w16/l/l3.pdf)\
[YouTube: A Second Course – The Push-Relabel Algorithm](https://www.youtube.com/watch?v=0hI89H39USg)

### Multi-Agent Path Finding (MAPF)

[Web: Increasing Cost Tree Search for MAPF](https://www.sciencedirect.com/science/article/pii/S0004370212001543)\
[PDF: Traffic Flow Optimisation for Lifelong MAPF](https://harabor.net/data/papers/chls-aaai24-tfoflmapf.pdf)\
[PDF: Conflict-Based Search for Optimal MAPF](https://www.sciencedirect.com/science/article/pii/S0004370214001386)\
[PDF: Priority Inheritance with Backtracking (PIBT)](https://www.ijcai.org/proceedings/2019/0076.pdf)

### LaCAM algorithm

[Web: LaCAM – Search-Based Algorithm for Quick MAPF](https://ojs.aaai.org/index.php/AAAI/article/view/26377)\
[PDF: Improving LaCAM](https://www.ijcai.org/proceedings/2023/0028.pdf)\
[PDF: Engineering LaCAM](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p1501.pdf)\
[PDF: Minimizing Makespan with LaCAM](https://openreview.net/pdf?id=ppr77dTFWR)

### Heuristic search

[YouTube: A\* Heuristic Search](https://youtu.be/8_dGurEKXDk)
