import { chmod, lstat, mkdir, readlink, symlink } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { appJwt, installation } from "./auth.ts";
import { cachePath, envPath, loadConfig, projectPath } from "./config.ts";
import { sessionConfiguration } from "./launch.ts";
import { agentPath, agentSchema, patchEnvironment, readConfig, readEnvironment, readManifest, saveConfig, saveManifest, uninstallValues, type Agent, type Manifest } from "./settings.ts";

const sourcePath = resolve(dirname(fileURLToPath(import.meta.url)), "..");

async function linkProject(): Promise<void> {
  if (sourcePath === projectPath) return;
  const exists = await Bun.file(join(projectPath, "package.json")).exists();
  if (exists) {
    const info = await lstat(projectPath);
    if (!info.isSymbolicLink() || resolve(dirname(projectPath), await readlink(projectPath)) !== sourcePath) {
      throw new Error(`${projectPath} already exists and is not this checkout.`);
    }
    return;
  }
  await symlink(sourcePath, projectPath);
}

async function prepare(): Promise<void> {
  const config = await loadConfig();
  const installed = await installation(config, await appJwt(config));
  await mkdir(join(cachePath, "gh"), { recursive: true, mode: 0o700 });
  await chmod(cachePath, 0o700);
  for (const name of ["gh", "git", "git-credential-agent-team"]) await chmod(join(sourcePath, "bin", name), 0o755);
  await linkProject();
  const contents = (await readConfig(envPath)).replace(/^\s*(?:export\s+)?AGENT_TEAM_BOT_INSTALLATION_ID=.*\n?/gm, "").trimEnd();
  await saveConfig(envPath, `${contents}\nAGENT_TEAM_BOT_INSTALLATION_ID=${installed.id}\n`);
  process.stdout.write(`Installation ID: ${installed.id}\n`);
}

function installedEnvironment(current: Record<string, string>): Record<string, string> {
  const paths = (process.env.PATH ?? "/usr/bin:/bin").split(":")
    .filter((path) => !path.includes("/.codex/tmp/") && !path.endsWith("/codex-path"));
  const shell = Object.fromEntries(["ZDOTDIR", "BASH_ENV", "AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR", "AGENT_TEAM_BOT_ORIGINAL_BASH_ENV"]
    .map((key) => [key, current[key] ?? process.env[key]]));
  return sessionConfiguration({ ...shell, PATH: [...new Set(paths)].join(":") });
}

async function installAgent(agent: Agent, manifest: Manifest): Promise<void> {
  const source = await readConfig(agentPath(agent));
  const current = readEnvironment(agent, source);
  const installed = installedEnvironment(current);
  const previous = Object.fromEntries(Object.keys(installed).map((key) => [key, current[key] ?? null]));
  manifest[agent] = { installed, previous: { ...previous, ...manifest[agent]?.previous } };
  await saveManifest(manifest);
  await saveConfig(agentPath(agent), patchEnvironment(agent, source, installed));
  process.stdout.write(`Enabled for ${agent} on this machine.\n`);
}

async function uninstallAgent(agent: Agent, manifest: Manifest): Promise<void> {
  const state = manifest[agent];
  if (!state) { process.stdout.write(`${agent}: no managed installation.\n`); return; }
  const source = await readConfig(agentPath(agent));
  const values = uninstallValues(readEnvironment(agent, source), state);
  await saveConfig(agentPath(agent), patchEnvironment(agent, source, values));
  const conflicts = Object.keys(state.installed).filter((key) => !(key in values));
  delete manifest[agent];
  await saveManifest(manifest);
  process.stdout.write(`Disabled for ${agent}.${conflicts.length ? ` Left modified settings: ${conflicts.join(", ")}` : ""}\n`);
}

async function main(): Promise<void> {
  const [operation, target] = process.argv.slice(2);
  if (!["install", "uninstall"].includes(operation)) throw new Error("Usage: bun src/install.ts <install|uninstall> <claude|codex|both>");
  const agents: Agent[] = target === "both" ? ["claude", "codex"] : [agentSchema.parse(target)];
  const manifest = await readManifest();
  if (operation === "install") await prepare();
  for (const agent of agents) await (operation === "install" ? installAgent : uninstallAgent)(agent, manifest);
  process.stdout.write("Restart the selected agents to apply the change. Shared dotfiles and shell configuration are unchanged.\n");
}

if (import.meta.main) await main().catch((error: unknown) => {
  process.stderr.write(`gh-agent-team-bot: ${error instanceof Error ? error.message : "Setup failed"}\n`);
  process.exitCode = 1;
});
