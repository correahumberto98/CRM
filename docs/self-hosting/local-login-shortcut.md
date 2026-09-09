# Local development login shortcut (macOS)

Double-click `ABRIR-CRM.command` in the local CRM folder. It runs the versioned `scripts/open-crm.command`, starts the local Docker services and frontend if needed, and opens the default browser signed in as `admin@example.com`. If prompted, choose the desired organization. Docker Desktop must be running; Node and pnpm must be available on PATH. The local wrapper supplies the installed runtime paths on this computer.

The shortcut uses the normal single-use magic-link verification flow with a two-minute expiration. It does not create accounts, change passwords or expose a login-bypass web endpoint. Only an existing active user is eligible. Running the shortcut again invalidates previous unused links for that user.

The command requires both Django DEBUG=True and CRM_LOCAL_LOGIN=1, and rejects non-loopback FRONTEND_URL values. The launcher sets the opt-in only for the management-command process, checks for a local Unix-socket Docker engine and opens only http://localhost:5173. DEBUG=False blocks link issuance even if the opt-in is set. Never enable DEBUG in a public deployment. Regular browser authentication and organization permissions remain in effect.

The repository script accepts an optional existing local user's email as its first argument. It requires local shell/Docker access and is not callable from the website. No credential or generated link is saved in the repository. Production email login remains a separate setup task.
