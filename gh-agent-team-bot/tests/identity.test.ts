import { expect, test } from "bun:test";
import { homedir } from "node:os";
import { join } from "node:path";

import { botLogin } from "../src/config.ts";
import { personalEnvironment, personalLogin, personalToken, repositoryToken, type IdentityDependencies } from "../src/identity.ts";

function routing(pages: string[][]): { dependencies: IdentityDependencies; calls: string[] } {
  const calls: string[] = [];
  const dependencies: IdentityDependencies = {
    botToken: async () => { calls.push("bot"); return { token: "bot-test" }; },
    personal: async () => { calls.push("personal"); return "personal-test"; },
    request: async (endpoint: string, token: string): Promise<unknown> => {
      calls.push(`${endpoint}|${token}`);
      const index = Number(new URL(`https://example.test${endpoint}`).searchParams.get("page")) - 1;
      return { total_count: pages.flat().length, repositories: pages[index].map((full_name) => ({ full_name })) };
    },
  };
  return { dependencies, calls };
}

test("outside repositories use personal authentication without attempting bot authentication", async () => {
  const { dependencies, calls } = routing([]);
  expect(await repositoryToken("jcooper036/dotfiles", dependencies)).toEqual({ token: "personal-test", login: personalLogin });
  expect(calls).toEqual(["personal"]);
});

test("installed repositories use the bot and membership matching ignores case", async () => {
  const { dependencies, calls } = routing([["Leash-Labs/leash"]]);
  expect(await repositoryToken("leash-labs/LEASH.git", dependencies)).toEqual({ token: "bot-test", login: botLogin });
  expect(calls).toEqual(["bot", "/installation/repositories?per_page=100&page=1|bot-test"]);
});

test("an installation with no repositories selects personal authentication", async () => {
  const { dependencies, calls } = routing([[]]);
  expect(await repositoryToken("Leash-Labs/leash", dependencies)).toEqual({ token: "personal-test", login: personalLogin });
  expect(calls).toEqual(["bot", "/installation/repositories?per_page=100&page=1|bot-test", "personal"]);
});

test("installation membership is checked across pages before falling back", async () => {
  const { dependencies, calls } = routing([["Leash-Labs/first"], ["Leash-Labs/second"]]);
  expect(await repositoryToken("Leash-Labs/second", dependencies)).toEqual({ token: "bot-test", login: botLogin });
  expect(calls.at(-1)).toBe("/installation/repositories?per_page=100&page=2|bot-test");
  calls.length = 0;
  expect(await repositoryToken("Leash-Labs/public-uninstalled", dependencies)).toEqual({ token: "personal-test", login: personalLogin });
  expect(calls).toEqual(["bot", "/installation/repositories?per_page=100&page=1|bot-test", "/installation/repositories?per_page=100&page=2|bot-test", "personal"]);
});

test("bot issuance and repository listing failures never select personal authentication", async () => {
  for (const operation of ["botToken", "request"] as const) {
    const { dependencies, calls } = routing([]);
    dependencies[operation] = async (): Promise<never> => { throw new Error("test authentication failure"); };
    await expect(repositoryToken("Leash-Labs/leash", dependencies)).rejects.toThrow("test authentication failure");
    expect(calls).not.toContain("personal");
  }
});

test("incomplete repository pagination fails rather than selecting personal authentication", async () => {
  const { dependencies, calls } = routing([]);
  dependencies.request = async (): Promise<unknown> => ({ total_count: 1, repositories: [] });
  await expect(repositoryToken("Leash-Labs/leash", dependencies)).rejects.toThrow("pagination ended");
  expect(calls).not.toContain("personal");
});

test("personal authentication verifies the saved token's account", async () => {
  const calls: string[] = [];
  const readToken = async (): Promise<string> => "personal-test";
  const request = async (endpoint: string, token: string): Promise<unknown> => {
    calls.push(`${endpoint}|${token}`);
    return { login: personalLogin };
  };
  expect(await personalToken({ readToken, request })).toBe("personal-test");
  expect(calls).toEqual(["/user|personal-test"]);
  await expect(personalToken({ readToken, request: async () => ({ login: "someone-else" }) })).rejects.toThrow(`must belong to ${personalLogin}`);
});

test("personal configuration discards session token overrides and restores the XDG gh directory", () => {
  const source = { GH_CONFIG_DIR: "/bot/gh", XDG_CONFIG_HOME: "/personal/config", GH_TOKEN: "test-token", GITHUB_TOKEN: "test-token", GH_ENTERPRISE_TOKEN: "test-token", GITHUB_ENTERPRISE_TOKEN: "test-token", CUSTOM: "kept" };
  const result = personalEnvironment(source);
  expect(result.GH_CONFIG_DIR).toBe("/personal/config/gh");
  expect(result.CUSTOM).toBe("kept");
  expect([result.GH_TOKEN, result.GITHUB_TOKEN, result.GH_ENTERPRISE_TOKEN, result.GITHUB_ENTERPRISE_TOKEN]).toEqual(["", "", "", ""]);
  expect(source.GH_TOKEN).toBe("test-token");
  expect(personalEnvironment({ GH_CONFIG_DIR: "/bot/gh" }).GH_CONFIG_DIR).toBe(join(homedir(), ".config", "gh"));
});
