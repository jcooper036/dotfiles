import { delimiter, join } from "node:path";
import { homedir } from "node:os";

import { botEmail, botLogin, cachePath, projectPath } from "./config.ts";

export type Environment = Record<string, string | undefined>;

export function shellQuote(value: string): string {
  return `'${value.replaceAll("'", "'\\''")}'`;
}

export function gitSettings(credential = `!${shellQuote(join(projectPath, "bin/git-credential-agent-team"))}`): [string, string][] {
  return [
    ["credential.https://github.com.helper", ""],
    ["credential.https://github.com.helper", credential],
    ["credential.https://github.com.useHttpPath", "true"],
    ["http.https://github.com/.extraheader", ""],
    ["url.https://github.com/.insteadOf", "git@github.com:"],
    ["url.https://github.com/.insteadOf", "ssh://git@github.com/"],
    ["url.https://github.com/.insteadOf", "ssh://git@github.com:22/"],
    ["url.https://github.com/.insteadOf", "git://github.com/"],
  ];
}

export function sessionEnvironment(source: Environment): Record<string, string> {
  const bin = join(projectPath, "bin");
  const paths = (source.PATH ?? "/usr/bin:/bin:/opt/homebrew/bin").split(delimiter);
  return {
    AGENT_TEAM_BOT_ACTIVE: "1",
    AGENT_TEAM_BOT_ROOT: projectPath,
    AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR: source.AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR ?? source.ZDOTDIR ?? homedir(),
    AGENT_TEAM_BOT_ORIGINAL_BASH_ENV: source.AGENT_TEAM_BOT_ORIGINAL_BASH_ENV ?? source.BASH_ENV ?? "",
    ZDOTDIR: join(projectPath, "shell/zsh"),
    BASH_ENV: join(projectPath, "shell/bash-env.sh"),
    PATH: [bin, ...paths.filter((path) => path !== bin)].join(delimiter),
    GIT_AUTHOR_NAME: botLogin,
    GIT_AUTHOR_EMAIL: botEmail,
    GIT_COMMITTER_NAME: botLogin,
    GIT_COMMITTER_EMAIL: botEmail,
    GIT_TERMINAL_PROMPT: "0",
    GH_CONFIG_DIR: join(cachePath, "gh"),
    GH_PROMPT_DISABLED: "1",
    GH_TOKEN: "",
    GITHUB_TOKEN: "",
    GH_ENTERPRISE_TOKEN: "",
    GITHUB_ENTERPRISE_TOKEN: "",
  };
}

export function gitEnvironment(source: Environment, credential?: string): Environment {
  const count = Number(source.GIT_CONFIG_COUNT ?? 0);
  if (!Number.isSafeInteger(count) || count < 0) throw new Error("Invalid GIT_CONFIG_COUNT.");
  const result = { ...source, ...sessionEnvironment(source) };
  gitSettings(credential).forEach(([key, value], index) => {
    result[`GIT_CONFIG_KEY_${count + index}`] = key;
    result[`GIT_CONFIG_VALUE_${count + index}`] = value;
  });
  result.GIT_CONFIG_COUNT = String(count + gitSettings().length);
  return result;
}
