/**
 * Powerbar segments matching the Cursor CLI statusline:
 * - poppy-workspace: [poppy:<workspace>] in the workspace's color, from
 *   ~/.local/bin/poppy-workspace-color.
 * - auth-status: AUTH / NEED_AUTH (gcloud and application-default credentials)
 *   from ~/.local/bin/auth-status, which caches the authcli check.
 */

import { execFile } from "node:child_process";
import { realpathSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { join, relative, resolve, sep } from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

const BIN = join(homedir(), ".local", "bin");
const AUTH_HELPER = join(BIN, "auth-status");
const COLOR_HELPER = join(BIN, "poppy-workspace-color");
const WORKSPACES_ROOT = process.env.POPPY_WORKSPACES_ROOT ?? join(homedir(), "workspaces");
const REFRESH_MS = 15_000;

function run(command: string, args: string[]): Promise<string> {
	return new Promise((done) => {
		execFile(command, args, { timeout: 2000 }, (error, stdout) => done(error ? "" : stdout.trim()));
	});
}

function realpath(path: string): string {
	try {
		return realpathSync(path);
	} catch {
		return resolve(path);
	}
}

function workspaceFromCwd(cwd: string): string | undefined {
	const root = realpath(WORKSPACES_ROOT);
	const workspace = relative(root, realpath(cwd)).split(sep)[0];
	if (!workspace || workspace.startsWith("..") || workspace === ".poppy") return undefined;
	try {
		return statSync(join(root, workspace)).isDirectory() ? workspace : undefined;
	} catch {
		return undefined;
	}
}

export default function (pi: ExtensionAPI) {
	let timer: ReturnType<typeof setInterval> | undefined;
	let followUp: ReturnType<typeof setTimeout> | undefined;

	function register() {
		pi.events.emit("powerbar:register-segment", { id: "poppy-workspace", label: "Poppy Workspace" });
		pi.events.emit("powerbar:register-segment", { id: "auth-status", label: "Auth Status" });
	}

	async function updateWorkspace(ctx: ExtensionContext) {
		const workspace = workspaceFromCwd(ctx.cwd);
		const badge = `[poppy:${workspace ?? "none"}]`;
		const code = workspace ? Number.parseInt(await run(COLOR_HELPER, ["--code", workspace]), 10) : Number.NaN;
		if (code >= 0 && code <= 255) {
			// theme.fg wraps the text and resets the foreground after it, so this color applies to the badge only.
			pi.events.emit("powerbar:update", { id: "poppy-workspace", text: `\x1b[38;5;${code}m${badge}`, color: "text" });
		} else {
			pi.events.emit("powerbar:update", { id: "poppy-workspace", text: badge, color: "muted" });
		}
	}

	async function updateAuth() {
		const status = await run(AUTH_HELPER, []);
		const color = status === "AUTH" ? "success" : status === "NEED_AUTH" ? "error" : undefined;
		pi.events.emit("powerbar:update", { id: "auth-status", text: color ? status : undefined, color });
	}

	register();

	pi.on("session_start", async (_event, ctx) => {
		register();
		if (timer) clearInterval(timer);
		if (followUp) clearTimeout(followUp);
		timer = setInterval(() => void updateAuth(), REFRESH_MS);
		await Promise.all([updateWorkspace(ctx), updateAuth()]);
		// The first call may only start the background check.
		followUp = setTimeout(() => void updateAuth(), 2000);
	});

	pi.on("turn_end", async () => {
		await updateAuth();
	});

	pi.on("session_shutdown", async () => {
		if (timer) clearInterval(timer);
		if (followUp) clearTimeout(followUp);
		timer = undefined;
		followUp = undefined;
	});
}
