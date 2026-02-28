from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from auth import require_auth, github_login, github_callback, logout
from github import create_repo, list_repos
from ai import ai_chat
from db import init_db

app = FastAPI(title="AstraFlux")
init_db()


# ================= UI =================
@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    require_auth(request)

    return HTMLResponse("""
    
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>AstraFlux Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <!-- Tailwind Play CDN -->
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

  <style type="text/tailwindcss">
    :root {
      --color-brand: #7c3aed;
      --color-brand-soft: rgba(124, 58, 237, 0.38);
      --color-bg-start: #020617;
      --color-bg-end: #020617;
      --font-display: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    body {
      font-family: var(--font-display);
      background:
        radial-gradient(circle at top left, rgba(56,189,248,0.28), transparent 55%),
        radial-gradient(circle at top right, rgba(244,114,182,0.28), transparent 55%),
        radial-gradient(circle at bottom, rgba(129,140,248,0.3), transparent 60%),
        radial-gradient(circle at center, rgba(15,23,42,1), rgba(2,6,23,1));
      color: #e5e7eb;
      min-height: 100vh;
    }

    .glass-shell {
      backdrop-filter: blur(22px);
      -webkit-backdrop-filter: blur(22px);
      background:
        radial-gradient(circle at top left, rgba(56,189,248,0.14), transparent 55%),
        radial-gradient(circle at bottom right, rgba(168,85,247,0.18), transparent 55%),
        rgba(15,23,42,0.9);
      border-radius: 1.75rem;
      border: 1px solid rgba(148,163,184,0.35);
      box-shadow:
        0 30px 80px rgba(15,23,42,0.95),
        0 0 0 1px rgba(15,23,42,0.9) inset;
    }

    .nav-pill {
      background: rgba(15,23,42,0.9);
      border-radius: 999px;
      border: 1px solid rgba(75,85,99,0.8);
      box-shadow: 0 14px 30px rgba(0,0,0,0.8);
    }

    .nav-btn {
      transition: background 0.15s ease, color 0.15s ease, box-shadow 0.15s ease, transform 0.12s ease;
    }

    .nav-btn-primary {
      background: radial-gradient(circle at top left, rgba(129,140,248,1), rgba(124,58,237,1));
      color: #f9fafb;
      box-shadow:
        0 12px 30px rgba(79,70,229,0.85),
        0 0 0 1px rgba(248,250,252,0.4);
    }

    .nav-btn-primary:hover {
      transform: translateY(-1px);
      box-shadow:
        0 16px 40px rgba(79,70,229,1),
        0 0 0 1px rgba(248,250,252,0.5);
    }

    .nav-btn-ghost {
      color: #9ca3af;
    }

    .nav-btn-ghost:hover {
      background: rgba(15,23,42,0.9);
      color: #e5e7eb;
      box-shadow: 0 14px 30px rgba(15,23,42,0.9);
      transform: translateY(-1px);
    }

    .primary-action {
      background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
      border-radius: 1rem;
      box-shadow:
        0 16px 40px rgba(79,70,229,0.9),
        0 0 0 1px rgba(248,250,252,0.45);
      color: #f9fafb;
      transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.12s ease;
    }

    .primary-action:hover {
      transform: translateY(-1px);
      filter: saturate(1.2);
      box-shadow:
        0 20px 50px rgba(79,70,229,1),
        0 0 0 1px rgba(248,250,252,0.55);
    }

    .primary-action:active {
      transform: translateY(1px) scale(0.98);
      box-shadow:
        0 10px 26px rgba(79,70,229,0.85),
        0 0 0 1px rgba(248,250,252,0.45);
    }

    .card {
      border-radius: 1.2rem;
      border: 1px solid rgba(148,163,184,0.45);
      background: linear-gradient(
        145deg,
        rgba(15,23,42,0.95),
        rgba(15,23,42,0.96)
      );
      box-shadow:
        0 18px 45px rgba(0,0,0,0.9),
        0 0 0 1px rgba(15,23,42,1) inset;
    }

    .card-soft {
      border-radius: 1.2rem;
      border: 1px solid rgba(55,65,81,0.9);
      background: radial-gradient(circle at top left, rgba(15,23,42,1), rgba(15,23,42,1));
      box-shadow:
        0 20px 50px rgba(0,0,0,0.85),
        0 0 0 1px rgba(30,64,175,0.35);
    }

    .badge {
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.6);
      background: rgba(15,23,42,0.9);
    }

    .repos-list li {
      border-radius: 0.9rem;
      border: 1px solid rgba(55,65,81,0.85);
      background: radial-gradient(circle at top left, rgba(15,23,42,1), rgba(15,23,42,1));
      transition: border 0.15s ease, transform 0.12s ease, box-shadow 0.16s ease, background 0.16s ease;
    }

    .repos-list li:hover {
      border-color: rgba(129,140,248,0.95);
      background: radial-gradient(circle at top left, rgba(30,64,175,0.4), rgba(15,23,42,1));
      transform: translateY(-1px);
      box-shadow:
        0 16px 40px rgba(30,64,175,0.9),
        0 0 0 1px rgba(148,163,184,0.5);
    }

    .repos-list a {
      text-decoration: none;
    }

    .repos-list a:hover {
      text-decoration: underline;
    }

    .console-panel {
      background: radial-gradient(circle at top left, rgba(15,23,42,1), rgba(15,23,42,1));
      border-radius: 0.9rem;
      border: 1px solid rgba(31,41,55,0.9);
      box-shadow:
        0 18px 48px rgba(0,0,0,0.9),
        0 0 0 1px rgba(148,163,184,0.35);
    }

    .console-dots span {
      display: inline-block;
      width: 0.55rem;
      height: 0.55rem;
      border-radius: 999px;
    }

    .glow-dot {
      box-shadow:
        0 0 10px rgba(34,197,94,0.9),
        0 0 30px rgba(34,197,94,0.95);
    }
  </style>
</head>

<body class="px-4 py-6 md:px-8 md:py-10 flex items-center justify-center">
  <div class="w-full max-w-6xl">
    <!-- Top header -->
    <header class="mb-6 md:mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-2 px-4 py-1 badge text-[10px] uppercase tracking-[0.22em] text-slate-400">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 glow-dot"></span>
          AstraFlux Control Surface
        </div>
        <h1 class="mt-3 text-3xl md:text-4xl font-semibold tracking-tight text-slate-50">
          AstraFlux <span class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-violet-400 to-pink-400">Dashboard</span> 🚀
        </h1>
        <p class="mt-2 text-xs md:text-sm text-slate-400 max-w-xl">
          Orchestrate repositories, jump into AI chat, and route into AstraFlux Pusher from a single **command** center.
        </p>
      </div>
      <div class="flex items-center gap-3 justify-end">
        <button
          onclick="logout()"
          type="button"
          class="px-3 py-2 text-[11px] md:text-xs font-medium rounded-xl border border-slate-600/80 bg-slate-900/80 text-slate-300 hover:bg-slate-800 hover:border-slate-400 transition-colors"
        >
          Logout
        </button>
        <button
          type="button"
          onclick="window.location.href='http://127.0.0.1:8001'"
          class="primary-action px-4 py-2 text-[11px] md:text-xs font-semibold uppercase tracking-[0.18em] flex items-center gap-2"
        >
          <span class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-slate-950/50 border border-slate-100/40 text-[10px]">
            ⤴
          </span>
          Push codes and files
        </button>

 <button
          type="button"
          onclick="window.location.href='http://127.0.0.1:8000/open-deployer'"
          class="primary-action px-4 py-2 text-[11px] md:text-xs font-semibold uppercase tracking-[0.18em] flex items-center gap-2"
        >
          <span class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-slate-950/50 border border-slate-100/40 text-[10px]">
            ⤴
          </span>
          Auto Deployer
        </button>
      </div>
    </header>

    <!-- Main shell -->
    <main class="glass-shell p-4 md:p-6 lg:p-8">
      <!-- Nav actions -->
      <div class="mb-6 flex flex-wrap gap-3 items-center justify-between">
        <div class="nav-pill inline-flex items-center gap-1 p-1">
          <button
            type="button"
            class="nav-btn nav-btn-primary px-4 py-2 text-[11px] md:text-xs font-semibold rounded-full flex items-center gap-2"
            onclick="createRepo()"
          >
            <span class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-slate-950/50 border border-slate-100/40 text-[10px]">
              +
            </span>
            Create Repo
          </button>
          <button
            type="button"
            class="nav-btn nav-btn-ghost px-4 py-2 text-[11px] md:text-xs font-medium rounded-full flex items-center gap-2"
            onclick="loadRepos()"
          >
            <span class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-slate-950/50 border border-slate-100/40 text-[10px]">
              📂
            </span>
            Load Repos
          </button>
          <button
            type="button"
            class="nav-btn nav-btn-ghost px-4 py-2 text-[11px] md:text-xs font-medium rounded-full flex items-center gap-2"
            onclick="openAI()"
          >
            <span class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-slate-950/50 border border-slate-100/40 text-[10px]">
              🤖
            </span>
            AI Chat
          </button>
        </div>

        <div class="text-[11px] text-slate-400 flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 glow-dot"></span>
          Connected to GitHub workspace · ready to **launch**
        </div>
      </div>

      <!-- Dashboard grid -->
      <div class="grid gap-6 md:grid-cols-[minmax(0,1.1fr)_minmax(0,0.95fr)]">
        <!-- Repositories card -->
        <section class="card p-4 md:p-5 flex flex-col">
          <div class="flex items-center justify-between gap-3 mb-3">
            <div>
              <h2 class="text-sm md:text-base font-semibold text-slate-100">
                Repositories
              </h2>
              <p class="text-[11px] text-slate-400">
                Fetch and open your GitHub repos directly from this **panel**.
              </p>
            </div>
            <button
              type="button"
              onclick="loadRepos()"
              class="px-3 py-1.5 text-[11px] font-medium rounded-full border border-slate-600/80 bg-slate-900/80 text-slate-300 hover:bg-slate-800 hover:border-slate-400 transition-colors"
            >
              Refresh
            </button>
          </div>

          <div class="mt-2 flex-1 min-h-[140px]">
            <ul id="repos" class="repos-list space-y-2 text-sm text-slate-200">
              <!-- Filled by loadRepos() -->
            </ul>

            <div id="repos-empty" class="mt-3 text-xs text-slate-500">
              No repositories loaded yet. Click <span class="text-indigo-400">Load Repos</span> to **pull** your list.
            </div>
          </div>
        </section>

        <!-- AI + activity column -->
        <section class="space-y-4 md:space-y-5">
          <!-- AI Chat -->
          <div id="ai-card" class="card-soft p-4 md:p-5">
            <div class="flex items-center justify-between gap-3 mb-3">
              <div>
                <h2 class="text-sm md:text-base font-semibold text-slate-100 flex items-center gap-2">
                  AI Co-Pilot
                  <span class="px-2 py-0.5 text-[9px] uppercase tracking-[0.18em] rounded-full border border-emerald-400/40 bg-emerald-400/10 text-emerald-200">
                    Live
                  </span>
                </h2>
                <p class="text-[11px] text-slate-400">
                  Chat with your AI assistant about commits, docs, or any **idea**.
                </p>
              </div>
              <button
                type="button"
                onclick="toggleAI()"
                class="px-3 py-1.5 text-[11px] font-medium rounded-full border border-slate-600/80 bg-slate-900/80 text-slate-300 hover:bg-slate-800 hover:border-slate-400 transition-colors"
              >
                <span id="ai-toggle-label">Hide</span>
              </button>
            </div>

            <div id="ai" class="space-y-3 mt-1">
              <textarea
                id="msg"
                rows="4"
                class="w-full text-xs md:text-sm rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-500/70"
                placeholder="Ask anything about your project, code, or documentation…"
              ></textarea>
              <div class="flex items-center justify-between gap-2">
                <button
                  type="button"
                  onclick="send()"
                  class="primary-action px-4 py-2 text-[11px] md:text-xs font-semibold uppercase tracking-[0.18em] flex items-center gap-2"
                >
                  <span>Send</span>
                  <span class="inline-flex h-4 w-4 items-center justify-center rounded-full bg-slate-950/40 border border-slate-100/40 text-[9px]">
                    ↗
                  </span>
                </button>
                <p class="text-[10px] text-slate-500">
                  Replies stream below in a lightweight **console**.
                </p>
              </div>

              <div class="console-panel mt-3 p-3">
                <div class="flex items-center justify-between mb-2">
                  <div class="console-dots flex items-center gap-1">
                    <span style="background:#ef4444"></span>
                    <span style="background:#f59e0b"></span>
                    <span style="background:#22c55e"></span>
                  </div>
                  <span class="text-[10px] text-slate-500 uppercase tracking-[0.18em]">
                    AI · output
                  </span>
                </div>
                <pre
                  id="out"
                  class="max-h-48 overflow-auto text-[11px] md:text-[12px] leading-relaxed text-slate-200"
                ></pre>
              </div>
            </div>
          </div>

          <!-- Session info / Helper -->
          <div class="card p-4 md:p-5 text-[11px] md:text-xs text-slate-400">
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-semibold text-slate-100">
                Session insights
              </h3>
              <span class="px-2 py-0.5 rounded-full border border-slate-600/80 bg-slate-900/80 text-[9px] uppercase tracking-[0.18em] text-slate-400">
                AstraFlux
              </span>
            </div>
            <p class="mb-1">
              • Use <span class="text-indigo-300">Create Repo</span> to instantly scaffold a new GitHub repository in your linked account.
            </p>
            <p class="mb-1">
              • Tap <span class="text-indigo-300">Load Repos</span> to sync your latest repos and open them in a new **tab**.
            </p>
            <p>
              • Jump into <span class="text-indigo-300">AstraFlux Pusher</span> for code and file generation, then wire it to your API when you are ready.
            </p>
          </div>
        </section>
      </div>
    </main>

    <!-- Tiny footer -->
    <footer class="mt-4 text-center text-[10px] md:text-[11px] text-slate-500">
      AstraFlux Dashboard · Design-focused shell — backend hooks and GitHub logic stay exactly as you **implement** them.
    </footer>
  </div>

  <script>
    // ===== Your original JS logic, kept intact and just slightly enhanced for UX =====

    function createRepo() {
      const name = prompt("Repo name:");
      if (!name) return;
      fetch("/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo: name })
      })
        .then(r => r.json())
        .then(d => {
          alert(d.message);
          // Optional auto-refresh of repos
          loadRepos();
        })
        .catch(err => {
          console.error(err);
          alert("Failed to create repo.");
        });
    }

    function loadRepos() {
      fetch("/repos")
        .then(r => r.json())
        .then(d => {
          const ul = document.getElementById("repos");
          const empty = document.getElementById("repos-empty");
          ul.innerHTML = "";
          if (!d.repos || d.repos.length === 0) {
            empty.style.display = "block";
            return;
          }
          empty.style.display = "none";
          d.repos.forEach(r => {
            const li = document.createElement("li");
            li.className = "px-3 py-2 flex items-center justify-between gap-3";
            li.innerHTML = `
              <div class="min-w-0">
                <a href="${r.url}" target="_blank" class="text-indigo-300 hover:text-indigo-200 text-sm truncate">
                  ${r.name}
                </a>
                <div class="text-[10px] text-slate-500 truncate">
                  ${r.url}
                </div>
              </div>
              <span class="text-[10px] px-2 py-0.5 rounded-full border border-slate-600/80 text-slate-400">
                Repo
              </span>
            `;
            ul.appendChild(li);
          });
        })
        .catch(err => {
          console.error(err);
          alert("Failed to load repos.");
        });
    }

    function openAI() {
      const aiSection = document.getElementById("ai");
      const label = document.getElementById("ai-toggle-label");
      aiSection.style.display = "block";
      label.textContent = "Hide";
    }

    function toggleAI() {
      const aiSection = document.getElementById("ai");
      const label = document.getElementById("ai-toggle-label");
      const current = getComputedStyle(aiSection).display;
      if (current === "none") {
        aiSection.style.display = "block";
        label.textContent = "Hide";
      } else {
        aiSection.style.display = "none";
        label.textContent = "Show";
      }
    }

    function send() {
      const msgEl = document.getElementById("msg");
      const out = document.getElementById("out");
      const message = msgEl.value.trim();
      if (!message) {
        alert("Please type a message first.");
        return;
      }

      out.textContent = "Thinking...";
      fetch("/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      })
        .then(r => r.json())
        .then(d => {
          out.textContent = d.reply;
        })
        .catch(err => {
          console.error(err);
          out.textContent = "Error: unable to reach AI endpoint.";
        });
    }

    function logout() {
      fetch("/auth/logout", { method: "POST" })
        .then(() => window.location.replace("/login"))
        .catch(err => {
          console.error(err);
          window.location.replace("/login");
        });
    }
  </script>
</body>
</html>
    """)


# ================= ROOT =================
@app.get("/")
def root(req: Request):
    try:
        require_auth(req)
        return RedirectResponse("/ui")
    except:
        return RedirectResponse("/login")


# ================= AUTH =================
@app.get("/login", response_class=HTMLResponse)
def login():
    return "<a href='/auth/login'>Login with GitHub</a>"

@app.post("/login")
def login_post():
    return RedirectResponse("/login")

@app.get("/auth/login")
def login_gh():
    return github_login()


@app.get("/auth/callback")
def callback(code: str, state: str, req: Request):
    return github_callback(code, state, req)


@app.post("/auth/logout")
def do_logout():
    return logout()


# ================= AI =================
@app.post("/ai/chat")
async def chat(req: Request):
    require_auth(req)
    msg = (await req.json())["message"]
    return {"reply": ai_chat(msg)}


# ================= GITHUB =================
@app.post("/create")
async def create(request: Request):
    token = require_auth(request)
    data = await request.json()
    ok, msg = create_repo(token, data["repo"])
    return {"message": "Repo created" if ok else msg}


@app.get("/repos")
def repos(request: Request):
    token = require_auth(request)
    repos = list_repos(token)
    return {"repos": repos}

# Token
@app.get("/open-deployer")
def open_deployer(req: Request):
    token = require_auth(req)
    return RedirectResponse(
        f"http://127.0.0.1:8002/auth/handshake?token={token}"
    )

