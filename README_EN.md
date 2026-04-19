# Learning_Schedule

[中文版本](README.md)

This repository is a 24-month learning engineering roadmap focused on Embodied AI, DRL, control, ROS2, vision, and VLA. The goal is not only collecting resources, but turning the roadmap into executable monthly tasks with reproducible outputs.

## Structure

- [learning_plan_outline.md](learning_plan_outline.md): module breakdown and weighting
- [roadmap.md](roadmap.md): two-year high-level path and stage goals
- [resource_index.md](resource_index.md): curated learning resources by module
- [monthly_plans/README.md](monthly_plans/README.md): index for all monthly plans
- [monthly_plans/M01.md](monthly_plans/M01.md) to [monthly_plans/M24.md](monthly_plans/M24.md): execution cards by month
- [app.py](app.py): local desktop planning app (Tkinter)

## Recommended Reading Order

1. Read [learning_plan_outline.md](learning_plan_outline.md) to understand scope and priorities.
2. Read [roadmap.md](roadmap.md) to understand the stage sequence.
3. Use [resource_index.md](resource_index.md) for learning resources.
4. Execute from [monthly_plans/README.md](monthly_plans/README.md) month by month.

## Local Planner App

The local app in [app.py](app.py) reads monthly markdown plans and turns them into actionable todos.

### Features

- Browse monthly plan content
- Auto-extract tasks from key sections:
  - 核心任务
  - 关键实验
  - 交付物
  - 验收标准
- Toggle task completion by double-click or Space
- Add and remove custom tasks
- Persist progress locally
- Built-in multiple theme colors with runtime switching

### Run

```bash
/home/zhaoran/miniconda3/bin/python app.py
```

### Data Persistence

App state is stored at:

`~/.local/share/learning_schedule_planner/state.json`

Saved data includes:

- per-month task completion states
- per-month custom tasks
- app settings (including selected theme)

## Notes

- The app does not modify original markdown plan files.
- If no GUI appears, make sure you are running inside a Linux desktop session with Tk display access.
- File/folder references in this repository have been migrated to English names.
