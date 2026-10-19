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
