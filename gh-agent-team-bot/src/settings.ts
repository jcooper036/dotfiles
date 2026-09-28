import { chmod, mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { z } from "zod";

import { cachePath } from "./config.ts";

export const agentSchema = z.enum(["claude", "codex"]);
export type Agent = z.infer<typeof agentSchema>;
const environmentSchema = z.record(z.string(), z.string());
const stateSchema = z.object({ previous: z.record(z.string(), z.string().nullable()), installed: environmentSchema });
const manifestSchema = z.object({ claude: stateSchema.optional(), codex: stateSchema.optional() });
export type InstallState = z.infer<typeof stateSchema>;
export type Manifest = z.infer<typeof manifestSchema>;

export function agentPath(agent: Agent): string {
  return join(homedir(), agent === "claude" ? ".claude/settings.json" : ".codex/config.toml");
}

export function patchTomlEnv(source: string, values: Record<string, string | undefined>): string {
  const lines = source.split("\n");
  const start = lines.findIndex((line) => line.trim() === "[shell_environment_policy.set]");
  const following = start < 0 ? -1 : lines.findIndex((line, index) => index > start && /^\s*\[/.test(line));
  const end = following < 0 ? lines.length : following;
  const additions = Object.entries(values).filter(([, value]) => value !== undefined)
    .map(([key, value]) => `${key} = ${JSON.stringify(value)}`);
  if (start < 0) return `${source.trimEnd()}\n\n[shell_environment_policy.set]\n${additions.join("\n")}\n`;
  const kept = lines.slice(start + 1, end).filter((line) => {
    const key = line.match(/^\s*([A-Za-z_][A-Za-z_0-9]*)\s*=/)?.[1];
    return !key || !(key in values);
  });
  lines.splice(start + 1, end - start - 1, ...kept, ...additions);
  return `${lines.join("\n").trimEnd()}\n`;
}

export function readEnvironment(agent: Agent, source: string): Record<string, string> {
  if (agent === "claude") {
    const parsed = z.object({ env: environmentSchema.optional() }).parse(JSON.parse(source || "{}"));
    return parsed.env ?? {};
  }
  const parsed = z.object({ shell_environment_policy: z.object({ set: environmentSchema.optional() }).optional() }).parse(Bun.TOML.parse(source));
  return parsed.shell_environment_policy?.set ?? {};
}

export function patchEnvironment(agent: Agent, source: string, values: Record<string, string | undefined>): string {
  if (agent === "codex") {
    const patched = patchTomlEnv(source, values);
    Bun.TOML.parse(patched);
    return patched;
  }
  const settings = JSON.parse(source || "{}");
  const env = { ...readEnvironment(agent, source), ...values };
  settings.env = Object.fromEntries(Object.entries(env).filter(([, value]) => value !== undefined));
  if (!Object.keys(settings.env).length) delete settings.env;
  return `${JSON.stringify(settings, null, 2)}\n`;
}

export async function readConfig(path: string): Promise<string> {
  const file = Bun.file(path);
  return await file.exists() ? file.text() : "";
}

export async function saveConfig(path: string, contents: string): Promise<void> {
  const original = await readConfig(path);
  if (original === contents) return;
  const backupPath = join(cachePath, "backups", new Date().toISOString().replaceAll(":", "-"));
  await mkdir(backupPath, { recursive: true, mode: 0o700 });
  await Bun.write(join(backupPath, path.replaceAll("/", "_")), original, { mode: 0o600 });
  await mkdir(dirname(path), { recursive: true, mode: 0o700 });
  await Bun.write(path, contents, { mode: 0o600 });
  await chmod(path, 0o600);
}

export async function readManifest(): Promise<Manifest> {
  const source = await readConfig(join(cachePath, "installations.json"));
  return manifestSchema.parse(JSON.parse(source || "{}"));
}

export async function saveManifest(manifest: Manifest): Promise<void> {
  await saveConfig(join(cachePath, "installations.json"), `${JSON.stringify(manifest, null, 2)}\n`);
}

export function uninstallValues(current: Record<string, string>, state: InstallState): Record<string, string | undefined> {
  return Object.fromEntries(Object.entries(state.installed)
    .filter(([key, value]) => current[key] === value)
    .map(([key]) => [key, state.previous[key] ?? undefined]));
}
