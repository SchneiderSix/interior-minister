## CRITICAL: File Editing on Windows

### ⚠️ MANDATORY: Always Use Backslashes on Windows for File Paths

**When using Edit or MultiEdit tools on Windows, you MUST use backslashes (`\`) in file paths, NOT forward slashes (`/`).**

#### ❌ WRONG - Will cause errors:
```
Edit(file_path: "D:/repos/project/file.tsx", ...)
MultiEdit(file_path: "D:/repos/project/file.tsx", ...)
```

#### ✅ CORRECT - Always works:
```
Edit(file_path: "D:\repos\project\file.tsx", ...)
MultiEdit(file_path: "D:\repos\project\file.tsx", ...)
```

## Session hygiene
- Close Claude Code terminals when done, don't leave sessions hanging
- Use `claude ps` to check for orphaned sessions

## Notifications

When you give me any answer, notify me using:
powershell.exe -c "[System.Media.SystemSounds]::Beep.Play()"

## Rust Enforcement Rules

### Ownership & Safety — Non-Negotiable

- **NEVER** bypass, workaround, or simplify ownership logic. Follow Rust's ownership, borrowing, and lifetime model as designed.
- **NEVER** use `.clone()` or `Rc`/`Arc` just to silence the borrow checker — only when the design genuinely requires shared ownership.
- **NEVER** use `unsafe` without explicit developer approval and a written justification.
- Prefer zero-copy patterns. If data must be copied, justify it.
- Respect the type system — no `unwrap()` in production paths, use proper error handling (`Result`, `?` operator, `thiserror`/`anyhow`).

### Resource Usage — Mandatory Constraints

1. **Single-thread builds**: Always build with `cargo build -j 1`. Never use more than 1 CPU thread for compilation.
2. **Low resource enforcement**: At every implementation step, evaluate:
   - Time complexity of the chosen approach (prefer O(1)/O(log n) over O(n)/O(n²) when possible)
   - Memory allocation patterns (stack over heap, avoid unnecessary `Box`/`Vec` allocations)
   - Follow official Rust performance guidelines and core principles
3. **Documentation check**: Before modifying anything related to a dependency, fetch and verify the latest documentation for that crate using Context7 or official docs.

### Build Hygiene — Artifact Cleanup

- After build steps, delete unused files and artifacts that won't be needed (stale `.d` files, orphaned build outputs, unused generated files).
- Rust rebuilds frequently — intermediate artifacts accumulate. Clean them proactively.
- **Exception**: Do NOT delete incremental compilation cache (`target/debug/incremental/`, `target/release/incremental/`) until the project reaches a major version (1.0, 2.0, etc.). These speed up rebuilds significantly.
- Use `cargo clean -p <crate>` for targeted cleanup over `cargo clean` (full wipe) when possible.

### Changelog — Single Source of Truth

- Maintain a single `CHANGELOG.md` file at the project root for all workflow history.
- Every meaningful change (feature, fix, refactor, dependency update) gets an entry.
- Format: date, category, brief description of what changed and why.
- This file is the authoritative project history — keep it concise and current.

### Runtime Restrictions

- **Node.js is FORBIDDEN**. Never use `node`, `npm`, or `npx`.
- If Python is needed, use `uv` (e.g., `uv run`, `uvx`).
- If JavaScript/TypeScript is needed, use `bun` exclusively.

### Dependency Management

**RULE: When adding any new package (any language), always check for security vulnerabilities before committing.**

ALWAYS pin exact versions — never use ranges, `^`, `~`, `>=`, or `*` in any manifest file.

#### Rust (Cargo.toml)

Pin exact versions — never use `^` or `~`.

```sh
# Audit current project (requires cargo-audit)
cargo audit

# Check specific crate advisories
cargo audit --db /path/to/advisory-db

# Check for outdated dependencies
cargo outdated
```

#### Python (pyproject.toml / requirements.txt)

Pin exact versions — never use `>=`, `~=`, `^`, or `*`. Use `==` only.

```toml
# pyproject.toml — ✅ CORRECT
dependencies = [
    "polars==1.5.0",
    "httpx==0.27.2",
]

# pyproject.toml — ❌ WRONG
dependencies = [
    "polars>=1.5.0",
    "httpx~=0.27",
]
```

```txt
# requirements.txt — ✅ CORRECT
polars==1.5.0
httpx==0.27.2

# requirements.txt — ❌ WRONG
polars>=1.5.0
httpx~=0.27
```

```sh
# Audit Python dependencies
uv run pip-audit

# Check for outdated dependencies
uv pip list --outdated
```

#### JavaScript/TypeScript (package.json)

Pin exact versions — never use `^`, `~`, or `*`. Use `bun` exclusively (Node.js is forbidden).

```jsonc
// package.json — ✅ CORRECT
"dependencies": {
    "svelte": "5.0.0",
    "vite": "6.1.0"
}

// package.json — ❌ WRONG
"dependencies": {
    "svelte": "^5.0.0",
    "vite": "~6.1.0"
}
```

```sh
# Audit JS/TS dependencies
bun audit

# Check for outdated dependencies
bun outdated
```

### MCP Server Versions (pinned in ~/.claude.json)

Keep these pinned to audited versions. When updating, re-audit first.

| Server | Package | Pinned Version | Last Audited |
|--------|---------|---------------|--------------|
| Playwright | `@playwright/mcp` | 0.0.64 | 2026-02-10 |
| Sequential Thinking | `@modelcontextprotocol/server-sequential-thinking` | 2025.12.18 | 2026-02-10 |
| Context7 | `@upstash/context7-mcp` | 2.1.1 | 2026-02-10 |
| Morph LLM | `@morph-llm/morph-fast-apply` | 0.8.1 | 2026-02-10 |
| Svelte | `@sveltejs/mcp` | 0.1.20 | 2026-02-10 |
| Serena | `serena` (Python/uvx) | git HEAD | 2026-02-10 |