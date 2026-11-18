# Set up Jamaica's computer

Use this when Jamaica asks her desktop AI to install version 0.3.0. The AI runs the commands. Jamaica handles her sign-ins and chooses which apps to allow.

## 1. Prepare the workstation

- Use a local Codex task in the ChatGPT desktop app on Jamaica's Mac or Windows PC. Run setup as her ordinary user in the same environment the desktop app uses.
- Clone the public release into a permanent folder she owns. For example, run `git clone --branch v0.3.0 --depth 1 https://github.com/troyuu/voice.git Jamaica-Command-Center`, then `cd Jamaica-Command-Center`. If the destination exists, verify its origin and tag, or use a new folder to preserve local edits. A release ZIP already extracted to a permanent folder also works.
- Check `git --version`, `codex --version`, and `uv --version`. Install only missing prerequisites. On macOS with Homebrew, use `brew install git`, `brew install --cask codex`, or `brew install uv` as needed. On Windows with WinGet, use `winget install --id Git.Git -e` or `winget install --id astral-sh.uv -e` as needed. For Codex use the official Windows standalone installer. If a package manager is unavailable, follow the relevant vendor instructions. Refresh PATH in the current task and verify each command before proceeding. [Git downloads](https://git-scm.com/downloads) · [OpenAI Docs for Codex CLI](https://learn.chatgpt.com/docs/codex/cli#getting-started) · [Astral uv installation](https://docs.astral.sh/uv/getting-started/installation/)
- Check `codex login status`. If needed, open `codex login` in Jamaica's own terminal and let her sign in with ChatGPT. Keep passwords, device codes, local auth files and tokens out of chat, tickets and this checkout.

## 2. Run the installer from the clone

```text
uv run --python 3.12 python scripts/setup_computer.py install
```

This checks the pack, installs a checksum-verified, pinned Hermes Agent if the command is missing, installs the Jamaica Tools marketplace plugin, checks its seven skills, and configures the main assistant and six specialists. Its local tool server is called `jamaica-hermes`. Platform installers may prompt for permissions. Explain those prompts to Jamaica and let her choose.

For an older GitHub install, the installer can refresh the existing `troyuu/voice` marketplace. If an existing launcher is broken, first locate the user's working Hermes installation and restore its launcher to PATH. If another marketplace or a customized specialist has the same name, preserve it and explain the conflict before replacing anything. Keep the clone available for future plugin loading.

## 3. Sign in and verify

Start this in a terminal visible to Jamaica. It skips profiles that already have their own sign-in. Choose a fresh ChatGPT sign-in for each remaining profile.

```text
uv run --python 3.12 python scripts/setup_computer.py login
```

Then run:

```text
uv run --python 3.12 python scripts/setup_computer.py verify
```

Verification checks the enabled plugin version and sends one synthetic message through Codex to each Hermes profile. Report ready when all seven reply. Exit 2 means sign-in is pending. For an individual retry, run `uv run --python 3.12 python scripts/check_hermes_connection.py --role ROLE` using the role from the report.

## 4. Check desktop control

In the desktop app, open **Settings → Computer use → Any App** and follow the install or enable prompt. Older versions show **Plugins → Computer Use**. Jamaica chooses the apps she allows. macOS may ask for Screen Recording and Accessibility. On Windows, keep the target app visible on the active desktop. Open a fresh local task and ask Jamaica to allow a harmless test such as reading a result in Calculator. Report separately whether Hermes answered and whether the desktop control test worked. [OpenAI Computer Use setup](https://learn.chatgpt.com/docs/computer-use#set-up-computer-use)

Connect email, calendar, or calling accounts when Jamaica selects one for a task. The public release contains blank examples. Private profiles and sessions are stored on her own computer.
