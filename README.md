# Daily Word Game Demo

A full-stack daily word game demo built with **FastAPI**, **React** and **SQL Server**.

This project showcases the implementation of a lightweight daily puzzle experience inspired by word-based guessing games. It includes backend services, state persistence, daily assignment logic, attempt evaluation, scoring rules and a polished web interface.

## Overview

The application delivers one puzzle per day and keeps track of user progress across attempts. It was designed as a compact but complete full-stack demo with a clear separation between backend, frontend and database logic.

## Features

- Daily puzzle assignment
- Attempt validation and pattern evaluation
- Persistent game state
- Scoring and attempt limits
- Backend service-oriented structure
- React frontend with a lightweight UI
- SQL-based persistence layer
- Portfolio-safe sanitized version for public sharing

## Tech Stack

### Backend
- FastAPI
- Python
- pyodbc

### Frontend
- React
- TypeScript
- Vite

### Database
- SQL Server

### Tooling
- PowerShell
- Git / GitHub

## Project Structure

```text
backend/   API, services and persistence logic
frontend/  React user interface
sql/       SQL scripts for data model and setup
scripts/   PowerShell helper scripts
docs/      Supporting documentation
Architecture Notes

The project is split into two main layers:

Backend: handles daily assignment, validation, submission, persistence and game state retrieval
Frontend: renders the board, current session state and player interaction flow

The backend follows a service-based structure, while the frontend keeps the interaction layer lightweight and focused.

Portfolio Note

This repository is a sanitized portfolio version of the project. Sensitive infrastructure details, internal references and environment-specific values were removed or neutralized before publication.

Why this project is relevant

This demo highlights practical skills in:

full-stack development
API design
frontend/backend integration
SQL-backed application state
portfolio-safe project packaging
deployment-oriented thinking
Status

Portfolio-ready demo version.
