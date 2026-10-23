/**
 * Weekly quota status: puts the active account's 7-day usage percent in the
 * status line through `ctx.ui.setStatus`, rendered by the `status` segment.
 * Only Claude (anthropic) and Codex (openai-codex) are queried; every other
 * provider shows "Weekly Quota Unknown".
 */
import type { UsageReport } from "@oh-my-pi/pi-ai";
import type { ExtensionAPI, ExtensionContext } from "@oh-my-pi/pi-coding-agent";

const STATUS_KEY = "weekly-quota";
const UNKNOWN = "Weekly Quota Unknown";
const SUPPORTED: Record<string, true> = { anthropic: true, "openai-codex": true };
/** Usage endpoints are rate limited; the built-in usage segment uses the same 5 minutes. */
const REFRESH_MS = 5 * 60_000;
/** After a turn, refetch at most this often so the percent tracks the work. */
const TURN_REFRESH_MS = 60_000;
/** Cheap local check for a model switch while idle. */
const MODEL_POLL_MS = 2_000;
const FETCH_TIMEOUT_MS = 15_000;

/** The account-wide 7-day window; tiered caps (e.g. Claude's Fable pool) are separate allowances. */
function weeklyFraction(report: UsageReport): number | undefined {
	const weekly = report.limits.filter(l => (l.window?.id ?? l.scope.windowId) === "7d");
	const limit = weekly.find(l => !l.scope.tier) ?? weekly[0];
	return limit?.amount.usedFraction;
}

/** The report for the account this session is using, when several are logged in. */
function activeReport(ctx: ExtensionContext, provider: string, reports: UsageReport[]): UsageReport | undefined {
	const candidates = reports.filter(r => r.provider === provider);
	if (candidates.length <= 1) return candidates[0];
	const identity = ctx.modelRegistry.authStorage.oauth.identity(provider, ctx.sessionManager.getSessionId());
	const match = candidates.find(
		r =>
			(identity?.accountId !== undefined && r.metadata?.accountId === identity.accountId) ||
			(identity?.email !== undefined && r.metadata?.email === identity.email),
	);
	return match ?? candidates[0];
}

export default function (pi: ExtensionAPI) {
	let provider: string | undefined;
	let fetchedAt = 0;
	/** Provider of the fetch in progress; a fetch for a provider we switched away from never blocks or stamps the new one. */
	let inFlightFor: string | undefined;

	async function refresh(ctx: ExtensionContext): Promise<void> {
		const target = provider;
		if (!target || !SUPPORTED[target] || inFlightFor === target) return;
		inFlightFor = target;
		try {
			const reports = await ctx.modelRegistry.authStorage.usage.reports({
				signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
			});
			if (provider !== target) return;
			fetchedAt = Date.now();
			const report = reports ? activeReport(ctx, target, reports) : undefined;
			const used = report ? weeklyFraction(report) : undefined;
			ctx.ui.setStatus(STATUS_KEY, used === undefined ? UNKNOWN : `Weekly ${Math.round(used * 100)}%`);
		} catch {
			// Keep the last value; the next refresh window retries.
			if (provider === target) fetchedAt = Date.now();
		} finally {
			if (inFlightFor === target) inFlightFor = undefined;
		}
	}

	function sync(ctx: ExtensionContext, maxAgeMs: number): void {
		const current = ctx.model?.provider;
		if (current !== provider) {
			provider = current;
			fetchedAt = 0;
			ctx.ui.setStatus(STATUS_KEY, UNKNOWN);
		}
		if (Date.now() - fetchedAt >= maxAgeMs) void refresh(ctx);
	}

	pi.on("session_start", async (_event, ctx) => {
		if (!ctx.hasUI) return;
		sync(ctx, REFRESH_MS);
		ctx.setInterval(() => sync(ctx, REFRESH_MS), MODEL_POLL_MS);
	});

	pi.on("agent_end", async (_event, ctx) => {
		if (ctx.hasUI) sync(ctx, TURN_REFRESH_MS);
	});
}
