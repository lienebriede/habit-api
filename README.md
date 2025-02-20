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
- `created_at`: A DateTimeField that automatically records when the habit stack is created.
- `active_until`: A DateField that defines the duration until which the habit stack is considered active. This field is used for extending habit stacks. Defaults to 7 days from the creation date.

*Methods:*

- `extend_habit(days)`
Extends the active period of the habit stack by the specified number of days.

*Note:*

It is not possible to create a habit stack with all habit fields (both predefined and custom) left empty. At least one habit field must be provided for each position in the stack (either predefined or custom).

### HabitStackingLog Model

The `HabitStackingLog` model tracks the progress of a user's habit stack on a daily basis. It records whether a habit has been completed for a specific user on a given date, allowing for progress tracking over time.

*Fields:*

- `habit_stack`: A ForeignKey linking to the `HabitStacking` model, which represents the user's habit stack.
- `user`: A ForeignKey linking to the built-in `User` model, indicating which user the log belongs to.
- `date`: A DateField that records the date for the log entry, which corresponds to the specific day the habit stacking progress is being tracked.
- `completed`: A BooleanField that indicates whether the user has completed the habit stack for the given day. The default value is False.

### Milestone Model

The `Milestone` model tracks significant achievements for a habit stack. Milestones provide motivation and feedback as users progress in completing their habits.

*Fields:*

- `habit_stack`: ForeignKey linking to the `HabitStacking` model.
- `date_achieved`: A DateField recording when the milestone was achieved.
- `description`: A CharField describing the milestone

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
| `/habit-stacking/<int:pk>/extend/` | Extend the duration of a specific habit stack by a specified number of days.| POST | Create | 
| `/habit-stacking/<int:pk>/progress/`| Retrieve progress details for a habit stack. | GET| Read|
|`/habit-stacking-logs/`| List all habit stacking logs for the authenticated user. | GET|Read|
| `habit-stacking-logs/<int:pk>/`|Update the completion status of a specific habit stacking log.|PATCH|Update|


# Testing

See [testing.md](testing.md) for all the tests conducted.

# Bugs and Issues

1. 
During testing, users were able to access and modify each other's profiles and habit stacks, violating the website's privacy principles. The error messages were unclear, revealing the need for stricter permissions to ensure data security.

*Fix:*
Permissions were updated to ensure only authenticated users can access their own data. A custom permission was implemented to enforce ownership, allowing users to view, modify, or delete only their own habit stacks. The permission class `IsOwnerOrReadOnly` was changed to `IsAuthenticatedAndOwnerOrReadOnly` to ensure that users could only interact with their own data.

2. 
During testing, users were able to mark habits as completed for future dates, resulting in invalid milestone tracking and streaks being incorrectly calculated. This violated the websites's principle of reflecting real-time progress.

*Fix:*
Validation logic was added to the `HabitStackingLogSerializer` and the `StreakAndMilestoneTracker` model to restrict habit completion to the current or past dates only. Any attempt to mark a habit as completed on a future date now raises a `ValidationError`. This ensures data integrity and realistic progress tracking.

3. 
During testing, attempting to extend the active period of a habit stack occasionally triggered an `IntegrityError` due to duplicate log entries. This happened when a request tried to create a habit log for a combination of `habit_stack_id`, `user_id`, and `date` that already existed.

*Fix:* To address this issue, a duplicate-check mechanism was added to the `HabitExtendView`. Before creating new habit logs, the backend now filters for existing logs that match the intended date range and skips those dates to avoid duplication. Additionally, the response was updated to return a meaningful success or partial-success message.

4. 
The `check_and_deactivate` function in the HabitStacking model is designed to automatically set a habit stack's goal to `'NO_GOAL'` once the `active_until` date is passed. However, this function requires explicit calls to execute, and to automate it, a cron job or a scheduled task would need to be installed. Without this automation, the function remains unused and inactive.

*Decision:*
The habit stack can remain set to `'DAILY'`, and users can manually extend it when desired. Logs will still be generated from the date the user clicks the extend button, ensuring no loss of functionality. The `check_and_deactivate` function has been removed from the model, if needed, a cron job can be added to periodically call this function and automatically deactivate outdated habit stacks. For now, this enhancement is deferred to keep the system simpler and maintainable.

5.
The `goal` field and related functionality caused excessive complexity during development. The added logic for goals complicated the codebase and led to frequent issues with synchronization across models, particularly for goal tracking and habit stack management.

*Decision:*
The `goal` field and its functionality were removed from the project to simplify development and focus on core features. Milestones and habit stack logs now handle progress tracking in a straightforward way. The goal feature can be reintroduced in future iterations if needed.

6.
The `StreakAndMilestoneTracker` model was removed due to redundancy and overcomplication.

*Fix:*
The `StreakAndMilestoneTracker` model was replaced with the `Milestone` model, which focuses solely on tracking milestones. Streak-related calculations were moved to the views, ensuring better separation of concerns. The functions for calculating streaks, milestones, and progress tracking are now managed in the views and serializers, providing cleaner and more maintainable code.

7.
During API testing, users were unable to access their own profiles via the `/profiles/{id}/` endpoint because the `/profiles/` list view was restricted, returning an empty result. This prevented authenticated users from retrieving or updating their own profile information.

*Fix:*
The profile list view was modified to return only the authenticated user's profile, and the frontend was updated to first fetch the user’s ID via /dj-rest-auth/user/ before making a request to `/profiles/{id}/`. This ensures that users can only access their own profiles while maintaining privacy and security.

