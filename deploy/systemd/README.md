# systemd user units

1. Edit each `*.service` file and replace `%h/Projects/HashFarm` with the absolute path to this repository on the gaming PC (including spaces if any).
2. Copy units to `~/.config/systemd/user/`:

```bash
cp deploy/systemd/hashfarm-*.service ~/.config/systemd/user/
systemctl --user daemon-reload
```

3. Enable after `monerod` is synced and `.env` is filled:

```bash
systemctl --user enable --now hashfarm-monerod.service
# wait for sync
systemctl --user enable --now hashfarm-p2pool.service hashfarm-xmrig.service hashfarm-monitor.service
```

4. For the monitor, create the venv first:

```bash
cd monitor && python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

5. `loginctl enable-linger "$USER"` if you want user services to survive logout.
