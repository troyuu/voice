# Set up Jamaica's computer

Use this when Jamaica asks her desktop AI to install version 0.3.1. The AI runs the commands. Jamaica handles her sign-ins and chooses which apps to allow.

## 1. Prepare the workstation

- Use a local Codex task in the ChatGPT desktop app on Jamaica's Mac or Windows PC. Run setup as her ordinary user in the same environment the desktop app uses.
- Use the supplied ZIP. If you can't see it, ask Jamaica to select it or its folder. Extract it to a stable folder she owns (outside Downloads or temporary folders), retaining the hidden `.agents`, `.codex`, and `.codex-plugin` directories. If it's already extracted, use that folder. Don't overwrite an existing install. Start in the folder containing this guide, confirm the version in `plugins/jamaica-command-center/.codex-plugin/plugin.json` is `0.3.1`, and stop if it differs. No GitHub account or project clone is needed. The installer may download missing third-party tools, including Hermes from its upstream source.
- Check `git --version`, `codex --version`, and `uv --version`. Install only missing prerequisites. On macOS with Homebrew, use `brew install git`, `brew install --cask codex`, or `brew install uv` as needed. On Windows with WinGet, use `winget install --id Git.Git -e` or `winget install --id astral-sh.uv -e` as needed. For Codex use the official Windows standalone installer. If a package manager is unavailable, follow the relevant vendor instructions. Refresh PATH in the current task and verify each command before proceeding. [Git downloads](https://git-scm.com/downloads) · [OpenAI Docs for Codex CLI](https://learn.chatgpt.com/docs/codex/cli#getting-started) · [Astral uv installation](https://docs.astral.sh/uv/getting-started/installation/)
- Check `codex login status`. If needed, open `codex login` in Jamaica's own terminal and let her sign in with ChatGPT. Keep passwords, device codes, local auth files and tokens out of chat, tickets and this checkout.

## 2. Run the installer from the extracted folder

```text
uv run --python 3.12 python scripts/setup_computer.py install
```

This checks the pack, installs a checksum-verified, pinned Hermes Agent if the command is missing, installs the Jamaica Tools marketplace plugin, checks its seven skills, and configures the main assistant and six specialists. Its local tool server is called `jamaica-hermes`. Platform installers may prompt for permissions. Explain those prompts to Jamaica and let her choose.

If a previous install points to another location, the ZIP installer stops rather than fetching a different project copy. Tell Jamaica which location conflicts and ask before changing it. If an existing launcher is broken, first locate the user's working Hermes installation and restore its launcher to PATH. Preserve customized specialists. Keep the extracted folder in place for future plugin loading.

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
