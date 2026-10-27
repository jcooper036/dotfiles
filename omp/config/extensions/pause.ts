/**
 * Pause/resume for every omp session on this machine. `omp-pause` writes the
 * state file, `omp-reconnect` removes it; each session polls it, tells its agent
 * what happened, and blocks tool calls while paused. See omp/README.md.
 */
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";

const STATUS_KEY = "pause";
const POLL_MS = 2_000;
const STATE_FILE = process.env.OMP_PAUSE_FILE ?? join(homedir(), ".omp", "agent", "pause.json");

interface PauseState {
	reason?: string;
	since?: string;
}

/** The pause request, or undefined when not paused. A half-written file counts as paused. */
function readPause(): PauseState | undefined {
	if (!existsSync(STATE_FILE)) return undefined;
	try {
		return JSON.parse(readFileSync(STATE_FILE, "utf8")) as PauseState;
	} catch {
		return {};
	}
}

function pausedText(state: PauseState): string {
	const reason = state.reason ? ` Reason: ${state.reason}.` : "";
	return (
		`[PAUSED] The user is away and their connection is going down.${reason} ` +
		"Finish or safely park what you are doing now: leave no half-applied edits, and write down in your reply where you stopped and what is next. " +
		"Then end your turn. Tool calls are blocked until the connection returns. You will be told when to resume; do not try to work around the block."
	);
}

const RESUMED_TEXT =
	"[RESUMED] The connection is back. Continue the work you were doing before the pause from where you stopped. Re-check any state that may have changed while you were paused.";

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", async () => {
		if (!readPause()) return;
		return {
			block: true,
			reason: "Paused: the user's connection is down. Do not retry. End your turn; you will be told when to resume.",
		};
	});

	/** Per-session state lives in this closure; module scope is shared across child sessions. */
	pi.on("session_start", async (_event, ctx: ExtensionContext) => {
		let paused = false;
		let wasBusy = false;

		function check(): void {
			const state = readPause();
			if (state && !paused) {
				paused = true;
				wasBusy = !ctx.isIdle();
				ctx.ui.setStatus(STATUS_KEY, "PAUSED");
				pi.sendMessage(
					{ customType: "pause", content: pausedText(state), display: true },
					{ deliverAs: wasBusy ? "steer" : "nextTurn" },
				);
			} else if (!state && paused) {
				paused = false;
				ctx.ui.setStatus(STATUS_KEY, undefined);
				pi.sendMessage(
					{ customType: "pause", content: RESUMED_TEXT, display: true },
					wasBusy ? { deliverAs: "nextTurn", triggerTurn: true } : { deliverAs: "nextTurn" },
				);
				wasBusy = false;
			}
		}

		check();
		ctx.setInterval(check, POLL_MS);
	});
}
