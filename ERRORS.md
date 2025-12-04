# FocusDeck Backend Error Codes and Meanings

This document lists all common error codes/messages the backend may return via its API, and explains what each one means

## Error Codes and Descriptions

### 400 — Bad Request
- The request is missing required fields (like 'notes', 'email', or 'password'), the JSON is invalid, or the data isn't what the API expects.

### 401 — Unauthorized
- (Not common in current code) — Usually means the client forgot to provide a Firebase ID token, or passed an invalid/expired token. Most auth errors are passed as messages instead.

### 403 — Forbidden
- (Rare in typical use) — User attempted to access content they don't own, or a Firebase security rule issue.

### 500 — Internal Server Error
- Any uncaught Python exception, unexpected error, or problem contacting Firebase, Firestore, or the AI provider. Typical for code bugs or dependency failures.

---

## Example Error Messages (per 'error' JSON field)

### Authentication
- `Invalid email address`: Email is not formatted correctly during signup.
- `Email not verified. Please check your inbox...` : You have not clicked the verification email link after registration.
- `EMAIL_EXISTS`: The email is already registered (coming directly from Firebase Auth).
- `INVALID_PASSWORD`: Wrong password on login attempt.
- `EMAIL_NOT_FOUND`: Tried to log in with an unregistered email.
- `Login failed`: Catch-all, usually another Firebase Auth/Identity Toolkit error.

### Generation/API
- `No JSON array found`: The Gemini AI output could not be parsed as a list of flashcards (try splitting notes, or revise the input).
- `Failed to generate.`: Gemini/AI call failed or the model returned unexpected results.
- Any error message coming directly from the Gemini API (may include rate limit, network error, quota, etc).

### Firestore/Database
- "error": "<actual error message from Firestore/Firebase>" — for example, permission issues, quota errors, malformed data, or not found.

---

## Error JSON Structure

Every failed response will look like this:

```
{
  "success": false,
  "error": "…meaningful error message…",
  "type": "…Python/Exception class…"
}
```

- "error" contains the descriptive message you can show to users or log for debugging.
- "type" gives the Python exception class for advanced debugging.

---
## Debugging advice
- "EMAIL_..." and "INVALID_..." errors come from Firebase Auth.
- Errors with JSON/flashcards/study guide generation come from the Gemini/AI layer.
- Anything else is likely a database, configuration, or backend bug.

Check the error message and type, then refer to the above if you get stuck troubleshooting or need to communicate with development/support.

