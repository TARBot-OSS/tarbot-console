# tarbot-console

Shared admin console for the TAR Discord bots (TARVeri, TARClub): split-screen
`prompt_toolkit` TUI, Linux PAM login with lockout, idle session timeout, console-admin
management and security alerts to the bot's log channel.

A bot subclasses `ConsoleCore`, sets `bot_name`, `history_file`, `help_lines`,
`extra_completions` and `alert_channel_names`, and handles its own commands in
`dispatch_command`. Optional hooks: `eval_scope`, `_before_start`, `_alert_before`,
`_alert_guild_primary`, `_alert_guild_fallback`.

The bot's `db` must provide `is_console_admin`, `add_console_admin`, `remove_console_admin`,
`get_console_admins` and `has_any_console_admin`. `settings` may define `enable_console`
and `console_session_timeout`.

## Scrolling

| Action | Keys |
| --- | --- |
| Scroll the output pane (or the logs pane if output is minimized) a page | PgUp / PgDn |
| Scroll the logs pane a page | Ctrl+Up / Ctrl+Down, Shift+PgUp / Shift+PgDn |
| Scroll the pane under the pointer | Mouse wheel (3 lines per tick) |
| Jump both panes to the newest line | Ctrl+End |

A pane keeps following new lines until you scroll up, and follows again once you scroll back
to the bottom. Each pane keeps the last 5,000 lines.

Inside tmux, the mouse wheel reaches the console only with mouse mode on. Without it, tmux
scrolls its own history over the console instead. Turn it on with `tmux set -g mouse on`, or
add `set -g mouse on` to `~/.tmux.conf`.
