import { expect, test } from "bun:test";

import { credential } from "../src/credential.ts";
import { repositoryToken } from "../src/identity.ts";

test("credential helper gives Git the selected repository identity", async () => {
  const request = async (): Promise<unknown> => ({ total_count: 1, repositories: [{ full_name: "Leash-Labs/leash" }] });
  const select = (repository: string): ReturnType<typeof repositoryToken> => repositoryToken(repository, {
    botToken: async () => ({ token: "synthetic-bot" }), request, personal: async () => "synthetic-personal",
  });
  for (const [repository, token] of [["Leash-Labs/leash", "synthetic-bot"], ["Leash-Labs/uninstalled", "synthetic-personal"], ["jcooper036/tunnel-tool", "synthetic-personal"]]) {
    const outputs: string[] = [];
    await credential("get", `protocol=https\nhost=github.com\npath=${repository}.git\n\n`, select, (value) => { outputs.push(value); });
    expect(outputs.join("")).toBe(`username=x-access-token\npassword=${token}\n\n`);
  }
});

test("credential helper never loads either credential for an untrusted host", async () => {
  const outputs: string[] = [];
  await credential("get", "protocol=https\nhost=evil.test\npath=jcooper036/tunnel-tool\n\n", async () => { throw new Error("Unexpected authentication"); }, (value) => { outputs.push(value); });
  expect(outputs).toEqual(["quit=true\n\n"]);
});
