import { afterAll, beforeAll, expect, test } from "bun:test";
import { mkdir, rm } from "node:fs/promises";
import { resolve } from "node:path";

import { botEmail, botLogin, realGit } from "../src/config.ts";
import { gitEnvironment, shellQuote, type Environment } from "../src/environment.ts";

const directory = resolve(import.meta.dir, "../../tmp", Bun.randomUUIDv7());
const personalEnv: Environment = { ...process.env, GIT_CONFIG_GLOBAL: "/dev/null", GIT_CONFIG_NOSYSTEM: "1", GIT_CONFIG_COUNT: "0" };
const credential = `!${shellQuote(process.execPath)} ${shellQuote(resolve(import.meta.dir, "../src/cli.ts"))} credential`;
const agentEnv = gitEnvironment(personalEnv, credential);

function git(args: string[], env = agentEnv, input = ""): Bun.SyncSubprocess<"pipe", "pipe"> {
  return Bun.spawnSync([realGit, ...args], { cwd: directory, env, stdin: Buffer.from(input), stdout: "pipe", stderr: "pipe" });
}

beforeAll(async () => {
  await mkdir(directory, { recursive: true });
  expect(git(["init", "--initial-branch=bot-auth-test"]).exitCode).toBe(0);
  expect(git(["branch", "--show-current"]).stdout.toString().trim()).toBe("bot-auth-test");
});

afterAll(async () => { await rm(directory, { recursive: true }); });

test("Git records the bot as author and committer", () => {
  const commit = git(["-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "--allow-empty", "-m", "Verify agent identity\n\nCo-Authored-By: GPT-6 <noreply@tm.openai.com>"]);
  expect(commit.exitCode).toBe(0);
  expect(git(["log", "-1", "--format=%an|%ae|%cn|%ce"]).stdout.toString().trim()).toBe(`${botLogin}|${botEmail}|${botLogin}|${botEmail}`);
});

test("Git rewrites the SSH remote only in the agent environment", () => {
  expect(git(["remote", "add", "origin", "git@github.com:Leash-Labs/leash.git"]).exitCode).toBe(0);
  expect(git(["remote", "get-url", "origin"]).stdout.toString().trim()).toBe("https://github.com/Leash-Labs/leash.git");
  expect(git(["remote", "get-url", "origin"], personalEnv).stdout.toString().trim()).toBe("git@github.com:Leash-Labs/leash.git");
});

test("Git does not fall back to a saved personal credential for another owner", () => {
  const fallback = "!f() { printf 'username=human\\npassword=test-only\\n'; }; f";
  expect(git(["config", "credential.helper", fallback]).exitCode).toBe(0);
  const result = git(["credential", "fill"], agentEnv, "protocol=https\nhost=github.com\npath=another-owner/repo.git\n\n");
  expect(result.exitCode).not.toBe(0);
  expect(result.stdout.toString()).not.toContain("test-only");
  expect(result.stderr.toString()).toContain("quit");
});

for (const shell of ["/bin/zsh", "/bin/bash"]) {
  test(`${shell} login preserves the opted-in wrappers`, () => {
    const root = resolve(import.meta.dir, "..");
    const env = {
      ...agentEnv,
      AGENT_TEAM_BOT_ROOT: root,
      AGENT_TEAM_BOT_ORIGINAL_ZDOTDIR: directory,
      AGENT_TEAM_BOT_ORIGINAL_BASH_ENV: "",
      ZDOTDIR: `${root}/shell/zsh`,
      BASH_ENV: `${root}/shell/bash-env.sh`,
    };
    const result = Bun.spawnSync([shell, "-lc", "command -v gh; command -v git"], { env, stdout: "pipe", stderr: "pipe" });
    expect(result.exitCode).toBe(0);
    expect(result.stdout.toString().trim()).toBe(`${root}/bin/gh\n${root}/bin/git`);
  });
}
