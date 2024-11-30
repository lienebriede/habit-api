<h2 align="center">Habit API</h2>

## Table of Contents

# Models

### Profile model

The `Profile` model stores additional information about the user beyond what is stored in Django's default `User` model. It represents a one-to-one relationship between the `User` model and the `Profile`.

*Fields:*
- `owner`: A One-to-One relationship with the built-in User model. Each Profile is associated with a single User.
- `created_at`: A timestamp that records when the profile was created. This field is automatically set when the profile is first saved.
- `updated_at`: A timestamp that updates each time the profile is modified.
- `name`: An optional field to store the user's name, which can be left blank.


# API endpoints

| URL | Notes | HTTP Method | CRUD Operations |
| --- | ----- | ------------| --------------- |
| `dj-rest-auth/registration/` | Create new user | POST | Create |
| `dj-rest-auth/login/` | Login new user | POST | Read |
| `dj-rest-auth/logout/` | Logout new user | POST | Delete |
| `/profiles/` | List all profiles. | GET | Read |
| `/profiles/<int:pk>/` | Retrieve a profile based on the provided profile ID. | GET | Read |
| | Update a profile based on the provided profile ID. | PUT | Update |

# Testing

See [testing.md](testing.md) for all the tests conducted.

