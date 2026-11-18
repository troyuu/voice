# voice

voice helps you handle messages, calls, and everyday office work in ChatGPT Work or Codex. Tell it what you need in your own words. It recommends an approach, does the routine parts, and asks before actions that need your approval.

Public source: [github.com/troyuu/voice](https://github.com/troyuu/voice)

## Install with the ChatGPT desktop app

Save `voice-v0.4.0.zip` on your computer. In the ChatGPT desktop app, open a Work task with local computer access and paste:

> Please install voice v0.4.0 on my computer from the ZIP I was given. If you can’t see it, ask me to select it. Unzip it into a folder I can keep, check that it’s version 0.4.0, and follow SETUP.md. Use this copy; don’t clone the project from GitHub. Install all seven skills, connect my main assistant and six helpers to Hermes, and help me turn on Computer Use for the apps I choose. Guide me one step at a time when I need to sign in or approve something. Never ask me to paste a password or code into chat. Test with sample data only, then tell me what’s ready and what still needs me.

The [computer setup guide](SETUP.md) starts from the ZIP; no GitHub account is needed. You’ll need internet for missing tools and Hermes sign-in and verification. Complete sign-ins yourself in your terminal or browser.

## What it helps with

- Email and text-message triage, drafts, replies, and follow-ups
- Approved bulk outreach
- Call preparation, dialing assistance, notes, outcomes, and follow-ups
- Calendar, CRM, browser, data-entry, file, and research tasks
- Task-scoped computer control through explicit or inferred **Pilot mode**
- Turning repeated work into reviewed skills or specialist agent teams

## What you can say

```text
Help me answer these emails. Tell me which ones are urgent first.
```

```text
Prepare me for my call with this supplier. When I say Ready, open the call.
```

```text
Take care of today's confirmed appointments in the CRM and calendar.
```

The assistant starts with:

```text
Recommendation: ...
What I'll do: ...
Approval: ...
```

Routine work then continues automatically. Important actions still pause for you.

## Friendly operating rules

- You own the task. You can correct it, narrow it, or stop it at any point.
- The assistant leads with the approach it believes will work best and briefly explains a better alternative when needed.
- The assistant uses plain language and asks only one question at a time.
- Recommendations help you decide; they don't override what you asked for.
- Normal mode asks before sending, dialing, submitting, publishing, or deleting.
- You don't need a magic phrase. “Send this email” or “take care of it” allows routine actions for that one clearly defined task.
- The preview says when the assistant is treating a request as Pilot mode and names the outcome it will own.
- Requests for advice, a draft, or a review remain in normal mode. If you say “show me first,” the assistant waits.
- Pilot mode does not bypass passwords, security prompts, payments, contracts, permissions, destructive actions, privacy, consent, or other high-risk boundaries.
- Every bulk outreach batch needs one final approval.
- You remain the speaker on calls. The assistant waits for you to say **Ready** before dialing.

## Private local state

Each person installs the same ZIP under their own operating-system account and signs in to their own tools. The ZIP contains no user profile, credentials, or workflow history, only example files. You don't have to provide a name. On a shared computer, use separate macOS or Windows accounts: switching chats alone does not separate local files.

### Learning a routine

Say **“Make me a helper that drafts reminders for suppliers who haven't replied.”** The assistant can also offer one after helping you finish the same kind of task three times. It counts completed tasks, not screen activity, and you can say “don't track this.” Nothing runs in the background.

The assistant tests the helper on made-up examples, shows you what it does, and asks before turning it on. Each new helper uses an existing Hermes specialist and must get a test reply before installation. It needs no new sign-in if that specialist is already connected. Your counts and drafts stay in `.local/share/voice/runtime` under your user folder, outside the repository.

Run contributor checks with Python 3.11 or newer:

```text
python3 scripts/validate_pack.py
python3 -m unittest discover -s tests -v
```

The unit tests use local sample data. The separate Hermes connection check above sends synthetic challenges to the configured model.
