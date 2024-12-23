# Manual Testing

## Authorisation

## Profile

## HabitStacking API

| API Endpoint | Test Case | Expected Outcome | Actual Result |
| ------------ | --------- | ---------------- | ------------- |
|POST `/habit-stacking/`| Users can select predefined habits while creating their habit stacks. | Successful creation of a habit stack with predefined habits. |<img src="documentation/use_predefined_habit.png"> |
|POST `/habit-stacking/`| Users can have the option to enter custom habits manually. | Successful creation of a habit stack with custom habits. |<img src="documentation/use_custom_habit.png">|
|POST `/habit-stacking/`| If the habit stack already exists for the user with the same details, return a 400 Bad Request with a duplicate error message. | Return 400 Bad Request with error message. |<img src="documentation/duplicate_error.png">|
|POST `/habit-stacking/`| The goal can be set to "DAILY" or "NO_GOAL," with "DAILY" being the default if no goal is specified.| Goal defaults to "DAILY" if not provided.|Goal defaults to "DAILY" if not provided.|
|POST `/habit-stacking/`| Attempt to create a habit stack with both predefined and custom values for a single habit raises an error. | Return 400 Bad Request with validation error message. |<img src="documentation/single_habit_error.png">|
|POST `/habit-stacking/`|Create habit stacks with a "DAILY" goal and see logs created automatically.| 7 logs for the next 7 days are created, each with `completed=False` by default.|<img src="documentation/create_stack_and_logs.png"><img src="documentation/automated_logs_list.png">|
|GET `/habit-stacking/`| The authenticated user can view a list of all their habit stacks. | Return 200 OK with a list of habit stacks for the logged-in user. |<img src="documentation/view_habitstack_list.png">|
|GET `/habit-stacking/`| Habit stacks list includes habit1, habit2, and goal. | Return 200 OK with correct habit details for each stack. |Return 200 OK with correct habit details for each stack.| PASS |
|GET `/habit-stacking/{id}/`| The user can retrieve details of their specific habit stack. | Return 200 OK with habit stack details. |<img src="documentation/view_habitstack_detail.png">|
|GET `/habit-stacking/{id}/`| Return 404 Not Found if the habit stack doesn’t exist.| Return 404 Not Found.|<img src="documentation/habitstack_detail_not_found.png">|
|PUT `/habit-stacking/{id}/`| The user can update details of their existing habit stacks. | Return 200 OK with updated habit stack details. |<img src="documentation/update_habitstack.png">|
|DELETE `/habit-stacking/{id}/`| The user can delete their own habit stacks. | Return 204 No Content on successful deletion. |<img src="documentation/204_no_content.png">|
|GET `habit-stacking-logs`|List all habit stacking logs for the authenticated user.|Return 200 OK with a list of logs for the authenticated user, including habit_stack, date, and completed|PASS|
| PATCH `habit-stacking-logs/<int:pk>/`|Update the completed status of a habit stacking log (mark as complete or undo).|Return 200 OK with the updated log reflecting the completed status.|<img src="documentation/update_complete.png"><img src="documentation/Update_complete_undo.png">|
| PATCH `habit-stacking-logs/<int:pk>/`| Attempt to mark a habit stack complete in future time raises an error.| Returns a 400 Bad Request and a validation message.| <img src="documentation/error_future_date.png">|
|PUT `/habit-stacking/<int:pk>/extend/`|Extend the active period of a habit stack by 14 days.|Returns 200 OK with the `active_until` field updated to 14 days from today.| PASS <img src="documentation/test_extend_14.png">|
| PUT `/habit-stacking/<int:pk>/extend/`| Attempt to extend with invalid data - less than 7 days|Returns 400 Bad Request with validation error message.|<img src="documentation/test_less_than7.png">|
|GET `/habit-stacking-logs/`|Verify that new logs are generated for the extended period and no duplicate logs are made.|The list of logs has been update and no duplicate logs are created| PASS|
|POST `/milestone-posts/<int:pk>/share/`|Share a milestone post to the feed.|Returns 201 Created, and the post appears in the feed.||
|GET `/feed/`|Retrieve a list of shared milestones visible to the authenticated user.|Returns 200 OK with a list of milestone posts sorted in reverse chronological order.||
GET `/feed/`|Ensure the feed includes milestones shared by the logged-in user and others.|Returns 200 OK with all relevant milestones visible.|


# Automated Tests

### HabitStackingListViewTests

| Test | Expected Result | Outcome |
| ---- | --------------- | ------- |
| `test_habit_stacking_list_view_authenticated` | Should return a list of habit stacks for the authenticated user |PASS|
| `test_habit_stacking_list_view_unauthenticated` | Should return `403 Forbidden` when an unauthenticated user tries to access |PASS|
| `test_create_habit_stack` | Should create a new habit stack for the authenticated user |PASS|
| `test_create_habit_stack_validation_error` | Should return `400 Bad Request` for invalid habit stack data |PASS|
| `test_create_habit_stack_unauthenticated` | Should return `403 Forbidden` when trying to create a habit stack without authentication |PASS|

### HabitStackingDetailViewTests

| Test | Expected Result | Outcome |
| ---- | --------------- | ------- |
| `test_habit_stacking_detail_view_authenticated` | Should return details of the habit stack for the authenticated user |PASS|
| `test_habit_stacking_detail_view_unauthenticated` | Should return `403 Forbidden` when an unauthenticated user tries to access |PASS|
| `test_habit_stacking_detail_view_forbidden` | Should return `403 Forbidden` if the habit stack belongs to another user |PASS|
| `test_update_habit_stack` | Should update the habit stack with new data |PASS|
| `test_update_habit_stack_forbidden` | Should return `403 Forbidden` when trying to update someone else’s habit stack |PASS|
| `test_delete_habit_stack` | Should delete the habit stack and return `204 No Content`|PASS|
| `test_delete_habit_stack_forbidden` | Should return `403 Forbidden` when trying to delete someone else's habit stack |PASS|

### HabitStackingLogListViewTests
| Test | Expected Result | Outcome |
| ---- | --------------- | ------- |
| `test_habit_stacking_log_list_authenticated`| Should return a list of habit stacking logs for the authenticated user. |PASS|
| `test_habit_stacking_log_list_unauthenticated`|Should return `403 Forbidden` when an unauthenticated user tries to access the habit stacking logs.|PASS|
|`test_habit_stacking_log_auto_creation_7_days`|Should automatically create 7 habit stacking logs for the authenticated user, one for each of the next 7 days, when a habit stack is created with a DAILY goal.|PASS|

### HabitStackingLogEditViewTests
| Test | Expected Result | Outcome |
| ---- | --------------- | ------- |
| `test_habit_stacking_log_update_complete`|Should update the log's completed status to True.|PASS|
|`test_habit_stacking_log_update_undo`|Should update the log's completed status back to False.|PASS|

### StreakAndMilestoneTrackerTests
| Test | Expected Result | Outcome |
| ---- | --------------- | ------- |
| `test_update_streak_and_completions_on_success`|Streak and total completions should increase by 1 upon habit completion.|PASS|
|`test_streak_reset_on_incompletion`|Streak should reset to 0 when the habit is not completed.|PASS|
|`test_milestone_achieved`|Milestone message should be generated, and total completions should increase to the next milestone.|PASS|
|`test_multiple_milestones`|Multiple milestones should be achieved and milestone dates should be recorded.|PASS|
|`test_no_future_logs_allowed`| Habit completion should not be logged for future dates, and streak/completions should remain unchanged.|PASS|

### HabitStackingExtendAndLogTests
| Test | Expected Result | Outcome |
| ---- | --------------- | ------- |
|`test_extend_habit_stack_success`|Should successfully extend the active_until field by 7 or 14 days and return 200 OK|PASS|
|`test_extend_habit_stack_unauthenticated`|Should return 403 Forbidden for unauthenticated users attempting to extend a habit stack|PASS|
|`test_extend_habit_stack_not_found`|Should return 404 Not Found for an invalid habit stack ID|PASS|
|`test_habit_stacking_logs_updated_after_extend`|Should create new logs for the extended dates after successfully extending the habit stack|PASS|
|`test_habit_stacking_logs_no_duplicates`|Should not create duplicate logs if the habit stack is extended multiple times|PASS|

### MilestonePostTests
| Test | Expected Result | Outcome |
| ---- | --------------- | ------- |
|`test_share_milestone_post_success`|Should allow a user to successfully share a milestone post to the feed.|PASS|
|`test_share_milestone_post_unauthorized`|Should prevent unauthorized users from sharing milestone posts.|PASS|
|`test_view_shared_milestones_on_feed`|Should display both the user's and other users' shared milestone posts.|PASS|

<img src="documentation/automated_tests_habit_stack.png">
