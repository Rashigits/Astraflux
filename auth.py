import time
import secrets
import requests
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from db import get_db

def require_auth(request: Request):
    if request.cookies.get("logged_in") != "yes":
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = request.cookies.get("gh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")
    return token

def github_login():
    state = secrets.token_urlsafe(16)
    r = RedirectResponse(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&scope=repo&state={state}"
    )
    r.set_cookie("oauth_state", state, httponly=True, secure=False)
    return r

def github_callback(code: str, state: str, request: Request):
    if state != request.cookies.get("oauth_state"):
        raise HTTPException(400, "Invalid state")

    token = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code
        }
    ).json().get("access_token")

    if not token:
        raise HTTPException(401, "GitHub auth failed")

    user = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    ).json()

    username = user["login"]
    ip = request.client.host
    now = int(time.time())

    with get_db() as db:
        db.execute(
            "INSERT INTO login_logs (github_username, ip_address, login_time) VALUES (?,?,?)",
            (username, ip, now)
        )

    r = RedirectResponse("/ui")
    r.set_cookie("logged_in", "yes", httponly=True, secure=False)
    r.set_cookie("gh_token", token, httponly=True, secure=False)
    r.delete_cookie("oauth_state")
    return r

def logout():
    r = RedirectResponse("/login", status_code=303)
    r.delete_cookie("logged_in")
    r.delete_cookie("gh_token")
    return r
