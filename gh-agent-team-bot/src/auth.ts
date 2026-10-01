import { createPrivateKey, sign } from "node:crypto";
import { chmod, mkdir, rename } from "node:fs/promises";
import { join } from "node:path";
import { z } from "zod";

import { cachePath, loadConfig, owner, realGh, requirePrivate, slug, type Config } from "./config.ts";

const appSchema = z.object({ id: z.number(), slug: z.string(), owner: z.object({ login: z.string() }) });
const installationSchema = z.object({
  id: z.number(), app_id: z.number(), account: z.object({ login: z.string() }),
  repository_selection: z.string(), permissions: z.record(z.string(), z.string()),
});
const tokenSchema = z.object({ token: z.string().min(1), expires_at: z.iso.datetime() });
const cachedTokenSchema = tokenSchema.extend({ appId: z.string(), installationId: z.number() });
export type CachedToken = z.infer<typeof cachedTokenSchema>;

export function freshToken(value: unknown, appId: string, installationId: string | undefined, now = Date.now()): CachedToken | undefined {
  const parsed = cachedTokenSchema.safeParse(value);
  if (!parsed.success) return undefined;
  const token = parsed.data;
  if (token.appId !== appId || (installationId && String(token.installationId) !== installationId)) return undefined;
  return Date.parse(token.expires_at) > now + 300_000 ? token : undefined;
}

export async function appJwt(config: Config): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const header = Buffer.from(JSON.stringify({ alg: "RS256", typ: "JWT" })).toString("base64url");
  const payload = Buffer.from(JSON.stringify({ iat: now - 60, exp: now + 540, iss: config.clientId ?? config.appId })).toString("base64url");
  const unsigned = `${header}.${payload}`;
  const key = createPrivateKey(await Bun.file(config.privateKeyPath).text());
  return `${unsigned}.${sign("RSA-SHA256", Buffer.from(unsigned), key).toString("base64url")}`;
}

export async function api(endpoint: string, token: string, method = "GET"): Promise<unknown> {
  const child = Bun.spawn([realGh, "api", "--hostname", "github.com", "--method", method, "--header", `Authorization: Bearer ${token}`, endpoint], {
    env: { ...process.env, GH_TOKEN: token, GITHUB_TOKEN: "", GH_DEBUG: "", GH_HOST: "github.com" },
    stdout: "pipe", stderr: "pipe",
  });
  const [output, error, status] = await Promise.all([new Response(child.stdout).text(), new Response(child.stderr).text(), child.exited]);
  if (status !== 0) throw new Error(`gh api ${method} ${endpoint} exited ${status}: ${error.replaceAll(token, "[redacted]").trim()}`);
  return JSON.parse(output);
}

export async function installation(config: Config, jwt: string): Promise<z.infer<typeof installationSchema>> {
  const app = appSchema.parse(await api("/app", jwt));
  if (String(app.id) !== config.appId || app.slug !== slug || app.owner.login !== owner) {
    throw new Error("Private key does not identify the expected Leash-Labs/jacob-agent-team app.");
  }
  const result = installationSchema.parse(await api(`/orgs/${owner}/installation`, jwt));
  if (result.app_id !== app.id || result.account.login !== owner) throw new Error("Unexpected installation identity.");
  if (config.installationId && config.installationId !== String(result.id)) throw new Error("Configured installation ID does not match Leash-Labs.");
  return result;
}

export async function saveToken(value: CachedToken): Promise<void> {
  await mkdir(cachePath, { recursive: true, mode: 0o700 });
  await requirePrivate(cachePath, true);
  const path = join(cachePath, `${Bun.randomUUIDv7()}.json`);
  await Bun.write(path, JSON.stringify(value), { mode: 0o600 });
  await chmod(path, 0o600);
  await rename(path, join(cachePath, "token.json"));
}

export async function accessToken(force = false): Promise<CachedToken> {
  const config = await loadConfig();
  const file = Bun.file(join(cachePath, "token.json"));
  if (!force && await file.exists()) {
    await requirePrivate(cachePath, true);
    await requirePrivate(file.name!);
    const cached = freshToken(await file.json(), config.appId, config.installationId);
    if (cached) return cached;
  }
  const jwt = await appJwt(config);
  const installed = await installation(config, jwt);
  const issued = tokenSchema.parse(await api(`/app/installations/${installed.id}/access_tokens`, jwt, "POST"));
  const value = { ...issued, appId: config.appId, installationId: installed.id };
  await saveToken(value);
  return value;
}

export async function rejectToken(): Promise<void> {
  const file = Bun.file(join(cachePath, "token.json"));
  if (await file.exists()) await file.delete();
}
