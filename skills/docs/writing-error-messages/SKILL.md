---
name: writing-error-messages
description: >-
    Use when writing, reviewing, or rewriting human-facing error messages, form validation errors, empty states, authentication failures, error notifications, support copy, and CLI or API errors.
    Produces specific, actionable, blameless, accessible, and privacy-safe error communications.
---

# Writing Error Messages

## Quickstart

Before drafting any error message, identify:

1. **Audience:** end user, administrator, developer, support agent, or infrastructure operator.
2. **Failure:** what action failed and what remained intact or safely preserved.
3. **Cause:** known, unknown, user-fixable, server-side, third-party dependency, or security-sensitive.
4. **Recovery:** what the reader can do right now, what the system will do next, and where to get help if it persists.

Then, apply this structure:

```text
[What happened]
[Reassurance, if applicable]. [Why it happened, if known and safe to disclose]. [Specific corrective action]. [Fallback path if it continues failing].
```

Example:

```text
Could not connect your account
Your changes were saved, but we could not connect the account due to server instability. Please try connecting again. If the issue persists, contact support.
```

## Fundamental Rules

| Rule                              | What to Do                              | What to Avoid                                     |
| --------------------------------- | --------------------------------------- | ------------------------------------------------- |
| State what happened               | "Could not save your file."             | Generic "Something went wrong" with no context    |
| State what was unaffected         | "Your draft remains saved."             | Leaving user guessing whether data was lost       |
| Provide actionable next steps     | "Check your card number and try again." | "OK" or "Close" as the only options               |
| Use plain language                | "Could not connect to Google Drive."    | "Fetch failed" or "status code 500" for end users |
| Do not blame the user             | "Organization name is required."        | "You forgot to enter the organization name."      |
| Respect the situation's gravity   | Calm, direct, professional tone         | "Oops!", forced humor, or sarcastic phrasing      |
| Be specific when safe             | "Enter a date in the past."             | "Invalid input."                                  |
| Be generic when security requires | "Incorrect email or password."          | "Email exists, but password was incorrect."       |

## Message Anatomy

Use only the elements demanded by the situation:

| Element            | Purpose                     | Pattern                                                                           |
| ------------------ | --------------------------- | --------------------------------------------------------------------------------- |
| Title              | Summarize the failed action | "Could not save changes"                                                          |
| Body               | Explain cause and outcome   | "Your draft remains open, but could not be saved because the connection dropped." |
| Primary action     | Tell the reader what to do  | "Try again", "Update billing", "Choose another file"                              |
| Fallback action    | Provide an escape hatch     | "If this continues, contact support."                                             |
| Diagnostic details | Help developers or support  | Error code, Request ID (`requestId`), logs                                        |

Keep UI body copy to 1 to 2 short sentences. Push diagnostic details into expandable panels or log outputs.

## Validation and Form Errors

For field-level errors:

- Position the error adjacent to the related input, and summarize at the top for long forms.
- Mirror the exact label name of the field for easy identification.
- Explain how to fix, not just that it failed.
- Retain the user's previously entered input so they can adjust rather than retype.
- Avoid premature validation before the user has finished typing.

Good patterns:

```text
Enter a valid email address
Enter a date in the past
Password must be at least 12 characters
Select a file smaller than 10 MB
```

Avoid:

```text
This field is required
Invalid input
Illegal value provided
Validation error
```

## Accessibility and Empty States

- Place the error visually where the reader's focus already rests.
- Never rely exclusively on color (red). Use explicit text, clear icons, and accessible attributes (`aria-describedby`, `aria-invalid`).
- On page-level form submissions, move keyboard focus to the error summary block.
- Do not mistake empty results for errors. If a search returns no records, render a helpful empty state: "No invoices found" paired with a "Create invoice" button.

## Security and Privacy Guardrails

Specificity is not always desirable. Use deliberately generic messages when details could leak account existence, credentials, personal information, or fraud vectors.

For authentication and password recovery:

```text
Invalid email or password
If an account is associated with this email, we have sent password reset instructions.
```

Never disclose:

```text
This email is registered, but the password was incorrect
This account was locked due to excessive failed attempts
No account exists for the provided email
```

## Developer-Facing and CLI Errors

When the audience is technical and can act directly on the error, provide structured detail:

```text
Could not read configuration file
Expected TOML format in ./app.config.toml, but found invalid syntax at line 12: missing closing quote.
Fix the syntax error and run `app deploy` again.
```

Actionable details:

- Which command, file, environment variable, or resource failed.
- Expected value versus received value.
- Smallest corrective command or fix step.
- Request ID or log file path for debugging.

## Final Checklist

Before shipping an error message, verify:

1. What happened?
2. Did the user lose anything or generate duplicate data?
3. Why did it happen (if safe to disclose)?
4. What is the recommended next action?
5. What happens if the user does nothing?
6. Where can they find help if the recommended fix fails?
