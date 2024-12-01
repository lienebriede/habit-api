# Manual Testing

## Authorisation

## Profile

## HabitStacking API

| API Endpoint | Test Case | Expected Outcome | Actual Result |
| ------------ | --------- | ---------------- | ------------- |
| POST `/habit-stacking/` | Users can select predefined habits while creating their habit stacks. | Successful creation of a habit stack with predefined habits. ||
|| Users can have the option to enter custom habits manually. | Successful creation of a habit stack with custom habits. ||
|| If the habit stack already exists for the user with the same details, return a 400 Bad Request with a duplicate error message. | Return 400 Bad Request with error message. ||
|| The goal can be set to "DAILY" or "NO_GOAL," with "DAILY" being the default if no goal is specified.| Goal defaults to "DAILY" if not provided.||
|| Attempt to create a habit stack with both predefined and custom values for a single habit raises an error. | Return 400 Bad Request with validation error message. ||
| GET `/habit-stacking/` | The authenticated user can view a list of all their habit stacks. | Return 200 OK with a list of habit stacks for the logged-in user. ||
|| Return 401 Unauthorized for unauthenticated users. | Return 401 Unauthorized. ||
|| Habit stacks list includes habit1, habit2, and goal. | Return 200 OK with correct habit details for each stack. ||
| POST `/habit-stacking/` | The user cannot view habit stacks of other users. | Return 403 Forbidden or an empty list, depending on implementation. ||
| GET `/habit-stacking/{id}/` | The user can retrieve details of their specific habit stack. | Return 200 OK with habit stack details. ||
|| Return 404 Not Found if the habit stack doesn’t exist.| Return 404 Not Found.||
|| The user cannot access another user's habit stack. | Return 403 Forbidden. ||
| PUT `/habit-stacking/{id}/` | The user can update details of their existing habit stacks. | Return 200 OK with updated habit stack details. ||
|| If the update fails due to validation errors, return 400 Bad Request with appropriate error messages. | Return 400 Bad Request with error message. ||
|| Attempt to update a habit stack that doesn’t belong to the user. | Return 403 Forbidden. ||
| DELETE `/habit-stacking/{id}/` | The user can delete their own habit stacks. | Return 204 No Content on successful deletion. ||
|| Return 403 Forbidden if the user tries to delete a habit stack that doesn’t belong to them. | Return 403 Forbidden. ||
|| Return 404 Not Found if the habit stack does not exist. | Return 404 Not Found.||

# Automated Testing