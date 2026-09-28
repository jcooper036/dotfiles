import { readdir, stat } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { z } from "zod";

export const owner = "Leash-Labs";
export const slug = "jacob-agent-team";
export const botLogin = `${slug}[bot]`;
export const botEmail = `335096379+${botLogin}@users.noreply.github.com`;
export const projectPath = join(homedir(), "dotfiles/gh-agent-team-bot");
export const secretsPath = join(homedir(), ".secrets");
export const envPath = join(secretsPath, "github_team_bot.env");
export const cachePath = join(homedir(), ".cache/gh-agent-team-bot");
export const realGh = "/opt/homebrew/bin/gh";
export const realGit = "/usr/bin/git";

const configSchema = z.object({
  appId: z.string().regex(/^\d+$/),
  clientId: z.string().min(1).optional(),
  privateKeyPath: z.string().min(1),
  installationId: z.string().regex(/^\d+$/).optional(),
});

export type Config = z.infer<typeof configSchema>;

export function parseEnv(source: string): Record<string, string> {
  return Object.fromEntries(source.split("\n").flatMap((line) => {
    const match = line.match(/^\s*(?:export\s+)?(AGENT_TEAM_BOT_[A-Z_]+)\s*=\s*(.*?)\s*$/);
    if (!match) return [];
    const value = match[2].replace(/^(["'])(.*)\1$/, "$2");
    return [[match[1], value]];
  }));
}

export async function requirePrivate(path: string, directory = false): Promise<void> {
  const info = await stat(path);
  if ((info.mode & 0o077) !== 0 || info.uid !== process.getuid?.()) {
    throw new Error(`Restrict ${path} to its owner: chmod ${directory ? "700" : "600"} '${path}'`);
  }
}

export async function loadConfig(): Promise<Config> {
  await requirePrivate(secretsPath, true);
  await requirePrivate(envPath);
  const values = parseEnv(await Bun.file(envPath).text());
  const keys = (await readdir(secretsPath)).filter((name) => name.startsWith(slug) && name.endsWith(".pem"));
  const configuredKey = values.AGENT_TEAM_BOT_PRIVATE_KEY_PATH;
  if (!configuredKey && keys.length !== 1) {
    throw new Error("Set AGENT_TEAM_BOT_PRIVATE_KEY_PATH in github_team_bot.env; expected exactly one matching PEM.");
  }
  const privateKeyPath = (configuredKey ?? join(secretsPath, keys[0]))
    .replace(/^~(?=\/)/, homedir()).replace(/^\$HOME(?=\/)/, homedir());
  await requirePrivate(privateKeyPath);
  return configSchema.parse({
    appId: values.AGENT_TEAM_BOT_APP_ID,
    clientId: values.AGENT_TEAM_BOT_CLIENT_ID,
    privateKeyPath,
    installationId: values.AGENT_TEAM_BOT_INSTALLATION_ID,
  });
}
