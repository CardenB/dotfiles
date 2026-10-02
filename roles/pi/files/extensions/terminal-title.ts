/**
 * Drops pi's "π - " prefix from the terminal title, so tmux pane titles and terminal
 * tabs lead with the session name.
 *
 * Pi rebuilds the title on session start, reload, and rename, after extension
 * handlers run, so setting the title once is not enough; this wraps the terminal's
 * setTitle instead. A widget factory is the only extension hook that receives the
 * TUI and its terminal, so the wrapper is installed from an empty widget.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const PREFIX = "π - ";
const PATCHED = Symbol.for("terminal-title.patched");

type PatchableTerminal = { setTitle(title: string): void; [PATCHED]?: true };

function stripPrefix(terminal: PatchableTerminal): void {
	if (terminal[PATCHED]) return;
	const setTitle = terminal.setTitle.bind(terminal);
	terminal.setTitle = (title) => setTitle(title.startsWith(PREFIX) ? title.slice(PREFIX.length) : title);
	terminal[PATCHED] = true;
}

export default function (pi: ExtensionAPI) {
	pi.on("session_start", (_event, ctx) => {
		if (!ctx.hasUI) return;
		ctx.ui.setWidget(
			"terminal-title",
			(tui) => {
				stripPrefix(tui.terminal as PatchableTerminal);
				return { render: () => [], invalidate() {} };
			},
			{ placement: "belowEditor" },
		);
	});
}
