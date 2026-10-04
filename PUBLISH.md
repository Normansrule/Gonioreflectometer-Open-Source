# Publish to a private GitHub repo (fresh Ubuntu terminal)

Copy each block into the terminal in order. Works on native Ubuntu and WSL2.

**1 · Tools** (GitHub CLI install from its official docs [R70])

```bash
sudo apt update && sudo apt install -y git unzip wget python3 python3-venv
sudo mkdir -p -m 755 /etc/apt/keyrings \
 && out=$(mktemp) && wget -nv -O"$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg \
 && cat "$out" | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
 && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
 && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
 && sudo apt update && sudo apt install -y gh
```

**2 · Log in** (browser; `workflow` scope lets the CI file push)

```bash
gh auth login --hostname github.com --git-protocol https --web --scopes workflow
gh auth setup-git
```

**3 · Unzip** (finds the zip in `~/Downloads` or the Windows Downloads folder under WSL)

```bash
mkdir -p ~/projects && cd ~/projects
ZIP=$(ls -t ~/Downloads/Gonioreflectometer-Open-Source*.zip /mnt/c/Users/*/Downloads/Gonioreflectometer-Open-Source*.zip 2>/dev/null | head -1); echo "$ZIP"
unzip -oq "$ZIP" -d ~/projects && cd ~/projects/Gonioreflectometer-Open-Source
```

**4 · Create the private repo, push, load milestones and checklists**

```bash
bash scripts/publish.sh
```

`scripts/publish.sh` does: create `Gonioreflectometer-Open-Source` as **private** → push `main` → create or update labels, 11 milestones, 49 checklist issues (re-runs update renamed items; ticked boxes on unchanged issues are kept) → try to enable Pages from `/docs` → run the tests.

**Pages note:** private repos need GitHub Pro/Team for Pages. Without it, open `docs/index.html` locally (equations need internet for KaTeX).
