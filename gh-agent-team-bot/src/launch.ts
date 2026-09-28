import { basename } from "node:path";

import { gitEnvironment, type Environment } from "./environment.ts";

export function sessionConfiguration(source: Environment): Record<string, string> {
  const keys = ["PATH", "ZDOTDIR", "BASH_ENV", "AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR", "AGENT_TEAM_BOT_ORIGINAL_BASH_ENV"];
  const selected = Object.fromEntries(keys.map((key) => [key, source[key]]));
  return Object.fromEntries(Object.entries(gitEnvironment(selected))
    .filter((entry): entry is [string, string] => entry[1] !== undefined));
}

export function launchCommand(args: string[], source: Environment): string[] {
  if (!args.length) throw new Error("run requires a command.");
  const env = sessionConfiguration(source);
  const options: Record<string, string[]> = {
    claude: ["--settings", JSON.stringify({ env })],
    codex: Object.entries(env).flatMap(([key, value]) => ["-c", `shell_environment_policy.set.${key}=${JSON.stringify(value)}`]),
  };
  return [args[0], ...(options[basename(args[0])] ?? []), ...args.slice(1)];
}
