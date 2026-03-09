# Fly-In

![ci workflow](https://github.com/parad0xe/fly-in/actions/workflows/ci.yml/badge.svg)

_This project has been created as part of the 42 curriculum by nlallema_

## Table of Contents

- [Description](#description)
- [Usage](#usage)
- [Ressources](#resources)

## Description



## Usage

To **_install_** the project virtual environment :

```bash
make install
```

To **_run_** the program :

```bash
make run ARGS="file [-v[v]]"
```

#### Available positional argumments

| Arguments | Description              |
|-----------|--------------------------|
| file      | The path to the map file |

#### Available flag options

| Flags | Description        |
|-------|--------------------|
| -v    | Run with log INFO  |
| -vv   | Run with log DEBUG |

To run the **__tests__** :

```bash
make tests
```

To **_clean_** project environment:

```bash
make clean
```

To **_clean_** project cache:

```bash
make cache-clean
```

To check flake8 and mypy **_norms_** :

```bash
make lint
```

To check flake8 and mypy **_norms_** with **_strict_** flags :

```bash
make lint-strict
```

To run the program with the **_python debugger_** :

```bash
make debug
```


## Resources

[Web: PyQt6](https://doc.qt.io/qtforpython-6/PySide6/)\
[Web: Qt Matrix m11](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTransform.html#PySide6.QtGui.QTransform.m11)\
[Web: Qt StyleSheet](https://doc.qt.io/qtforpython-6/overviews/qtwidgets-stylesheet.html#qt-style-sheets)\
[Web: Qt Signal](https://www.tutorialspoint.com/pyqt/pyqt_new_signals_with_pyqtsignal.htm)

[Web: Maximum flow - Push-relabel algorithm](https://cp-algorithms.com/graph/push-relabel.html)\
[Web: Maximum flow - Push-relabel algorithm improved](https://cp-algorithms.com/graph/push-relabel-faster.html)\
[Pdf: A Second Course: The Push-Relabel Algorithm](https://timroughgarden.org/w16/l/l3.pdf)\
[Youtube: A Second Course: The Push-Relabel Algorithm](https://www.youtube.com/watch?v=0hI89H39USg)

[Web: Increasing cost tree search - MAPF](https://www.sciencedirect.com/science/article/pii/S0004370212001543)\
[Pdf: Traffic flow optimisation for Lifelong - MAPF](https://harabor.net/data/papers/chls-aaai24-tfoflmapf.pdf)\
[Pdf: Conflict-based search for optimal MAPF](https://www.sciencedirect.com/science/article/pii/S0004370214001386)\
[Pdf: Priority Inheritance with Backtracking (PIBT) for Iterative MAPF](https://www.ijcai.org/proceedings/2019/0076.pdf)

[Web: LaCAM: Search-Based Algorithm for Quick Multi-Agent Pathfinding](https://ojs.aaai.org/index.php/AAAI/article/view/26377)\
[Pdf: LaCAM: Improving LaCAM](https://www.ijcai.org/proceedings/2023/0028.pdf)\
[Pdf: Engineering LaCAM](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p1501.pdf)\
[Pdf: Minimizing Makespan with LaCAM](https://openreview.net/pdf?id=ppr77dTFWR)


[Youtube: Recherche heuristique A\*](https://youtu.be/8_dGurEKXDk)
