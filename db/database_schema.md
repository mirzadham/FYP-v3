# Academic Database Schema

This document describes the structure of the `academic.db` SQLite database.

## Tables Overview

| Table | Description |
|-------|-------------|
| `courses` | Stores course information |
| `prerequisites` | Stores course prerequisite relationships |

---

## Table Details

### `courses`

Stores information about available courses.

| Column | Type | Primary Key | Description |
|--------|------|-------------|-------------|
| `course_code` | TEXT | ✅ | Unique identifier for the course |
| `course_name` | TEXT | | Name of the course |
| `credit_hours` | TEXT | | Number of credit hours |
| `description` | TEXT | | Course description |

---

### `prerequisites`

Links courses to their required prerequisite courses.

| Column | Type | Primary Key | Description |
|--------|------|-------------|-------------|
| `course_code` | TEXT | | The course that has prerequisites |
| `prereq_code` | TEXT | | The prerequisite course code |

## Relationships

```
courses.course_code ──┬──< prerequisites.course_code
                      │
                      └──< prerequisites.prereq_code
```

The `prerequisites` table creates a many-to-many relationship, allowing a course to have multiple prerequisites and a course to be a prerequisite for multiple other courses.
