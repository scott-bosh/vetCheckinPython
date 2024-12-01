# Veterinary Check-In System

## Overview

The Veterinary Check-In System is a Python application designed to manage the check-in, status tracking, and discharge of animals at a veterinary clinic. It uses **SQLite** for database operations and includes features for robust error handling, user-friendly interaction, and scalable functionality.

---

## Features

- **Animal Check-Ins**: Record the details of animals visiting the clinic.
- **Status Tracking**: Retrieve detailed information about an animal by its unique ID.
- **Discharge Process**: Remove animals from the system once their visit is complete.
- **Input Validation**: Ensures only valid data is entered, reducing errors.
- **Scalable Design**: Easily add new species or extend functionality.

---

## Requirements

- **Python 3.8 or higher**
- Libraries:
  - `sqlite3` (Standard Library)
  - `datetime` (Standard Library)
  - `dataclasses` (Standard Library for Python 3.7+)
  - `contextlib` (Standard Library)
  - `logging` (Standard Library)
  - `typing` (Standard Library)
