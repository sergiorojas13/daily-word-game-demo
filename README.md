# Daily Word Game

A full-stack daily word game built with **FastAPI**, **React** and **SQL Server** — one puzzle per day, persistent state across attempts, and a complete evaluation and scoring engine.

---

## Overview

| Layer | Technology | Role |
|---|---|---|
| Backend | FastAPI + Python | Game logic, validation, persistence |
| Frontend | React + TypeScript + Vite | Player interface and session state |
| Database | SQL Server | Game state and daily assignment persistence |

---

## Architecture

```
┌─────────────────┐        ┌──────────────────────────────┐
│  React Frontend  │──────▶│         FastAPI Backend       │
│  (TypeScript)    │        │                              │
└─────────────────┘        │  ┌────────────┐              │
                            │  │  Daily     │              │
                            │  │  Assignment│              │
                            │  └─────┬──────┘              │
                            │        │                     │
                            │  ┌─────▼──────┐              │
                            │  │ Validation  │              │
                            │  │  Engine     │              │
                            │  └─────┬──────┘              │
                            │        │                     │
                            │  ┌─────▼──────┐              │
                            │  │  Scoring &  │              │
                            │  │  State      │              │
                            │  └─────┬──────┘              │
                            └────────┼─────────────────────┘
                                     │
                                SQL Server
                            (persistent game state)
```

- **Daily assignment logic** ensures every player gets the same puzzle each day
- **Validation engine** evaluates each attempt and returns pattern feedback
- **State persistence** tracks attempts, scores and session progress in SQL Server
- **Frontend** renders the board and interaction flow, consuming the backend API

---

## Features

- Daily puzzle assignment with consistent cross-session delivery
- Attempt validation with pattern evaluation feedback
- Persistent game state across sessions
- Scoring system with attempt limits
- Service-oriented backend structure
- Lightweight, focused React frontend
- SQL-backed persistence layer

---

## Project Structure

```
backend/    API, services and persistence logic
frontend/   React user interface
sql/        SQL scripts for data model and setup
scripts/    PowerShell helper scripts
docs/       Supporting documentation
```

---

## Tech Stack

**Backend** — FastAPI · Python · pyodbc

**Frontend** — React · TypeScript · Vite

**Database** — SQL Server

**Tooling** — PowerShell · Git

---

## Technical Highlights

- **Service-oriented backend**: game logic is split into discrete services (assignment, validation, scoring, state) rather than packed into route handlers — clean separation of concerns and easy to extend
- **Daily assignment engine**: deterministic daily puzzle delivery ensuring all players receive the same word on the same day, with SQL-backed tracking
- **Attempt evaluation**: pattern-matching validation engine that returns positional feedback per character, driving the frontend board state
- **Full-stack state management**: game progress persisted server-side via SQL Server, decoupled from frontend session storage

---

## Configuration

This repository is a **sanitized portfolio version**. Sensitive infrastructure details, internal references and environment-specific values have been removed before publication.

Adapt connection strings and environment config to your target environment before running locally.

---

## Stack

`FastAPI` `React` `TypeScript` `Vite` `SQL Server` `Python` `REST API` `Full-Stack`
