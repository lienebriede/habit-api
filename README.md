<h2 align="center">Habit API</h2>

## Table of Contents

# Models

### Profile Model

The `Profile` model stores additional information about the user beyond what is stored in Django's default `User` model. It represents a one-to-one relationship between the `User` model and the `Profile`.

*Fields:*
- `owner`: A One-to-One relationship with the built-in User model. Each Profile is associated with a single User.
- `created_at`: A timestamp that records when the profile was created. This field is automatically set when the profile is first saved.
- `updated_at`: A timestamp that updates each time the profile is modified.
- `name`: An optional field to store the user's name, which can be left blank.

### PredefinedHabit Model

The `PredefinedHabit` model represents a habit that is predefined and available for users to choose from when creating their habit stacks. This model stores a list of predefined habits that can be reused by different users.

*Fields:*

- `name`: A CharField that stores the name of the predefined habit. This field is unique, ensuring that each habit name is distinct in the database.

### HabitStacking Model

The `HabitStacking` model allows users to create custom habit stacks by choosing from a list of predefined habits or by adding their own custom habits.

*Fields:*

- `user`: A ForeignKey linking to the built-in User model. 
- `predefined_habit1`: A ForeignKey linking to the PredefinedHabit model, allowing the user to select the first predefined habit for the habit stack. This field is optional and can be left blank.
- `custom_habit1`: A CharField that allows the user to define a custom habit for the first habit stack position. This field is optional and can be left blank.
- `predefined_habit2`: A ForeignKey linking to the PredefinedHabit model, allowing the user to select the second predefined habit for the habit stack. This field is optional and can be left blank.
- `custom_habit2`: A CharField that allows the user to define a custom habit for the second habit stack position. This field is optional and can be left blank.
- `goal:` A CharField that represents the goal associated with the habit stack. It can either be set to 'DAILY' (the default value) or 'NO_GOAL'.
- `created_at`: A DateTimeField that automatically records when the habit stack is created.

*Note:*

It is not possible to create a habit stack with all habit fields (both predefined and custom) left empty. At least one habit field must be provided for each position in the stack (either predefined or custom).

### HabitStackingLog Model

The `HabitStackingLog` model tracks the progress of a user's habit stack on a daily basis. It records whether a habit has been completed for a specific user on a given date, allowing for progress tracking over time.

*Fields:*

- `habit_stack`: A ForeignKey linking to the `HabitStacking` model, which represents the user's habit stack.
- `user`: A ForeignKey linking to the built-in `User` model, indicating which user the log belongs to.
- `date`: A DateField that records the date for the log entry, which corresponds to the specific day the habit stacking progress is being tracked.
- `completed`: A BooleanField that indicates whether the user has completed the habit stack for the given day. The default value is False.

# API Endpoints

| URL | Notes | HTTP Method | CRUD Operations |
| --- | ----- | ------------| --------------- |
| `dj-rest-auth/registration/` | Create new user | POST | Create |
| `dj-rest-auth/login/` | Login new user | POST | Read |
| `dj-rest-auth/logout/` | Logout new user | POST | Delete |
| `/profiles/` | List all profiles. | GET | Read |
| `/profiles/<int:pk>/` | Retrieve a profile based on the provided profile ID. | GET | Read |
| | Update a profile based on the provided profile ID. | PUT | Update |
| `/habit-stacking/` | List all habit stacks for the authenticated user. | GET | Read |
|| Create a new habit stack for the authenticated user. | POST | Create |
| `/habit-stacking/<int:pk>/` | Retrieve a specific habit stack by ID. | GET | Read |
|| Update a habit stack for the authenticated user. | PUT | Update |
|| Delete a habit stack for the authenticated user. | DELETE | Delete |
| `/habit-stacking-logs/`| List all habit stacking logs for the authenticated user. | GET|Read|

# Testing

See [testing.md](testing.md) for all the tests conducted.

# Issues

1. 
During testing, users were able to access and modify each other's profiles and habit stacks, violating the website's privacy principles. The error messages were unclear, revealing the need for stricter permissions to ensure data security.

*Fix:*
Permissions were updated to ensure only authenticated users can access their own data. A custom permission was implemented to enforce ownership, allowing users to view, modify, or delete only their own habit stacks. The permission class `IsOwnerOrReadOnly`` was changed to IsAuthenticatedAndOwnerOrReadOnly` to ensure that users could only interact with their own data.