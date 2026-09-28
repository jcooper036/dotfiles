import { describe, expect, test } from "bun:test";
import { generateKeyPairSync, verify } from "node:crypto";
import { mkdir, rm } from "node:fs/promises";
import { resolve } from "node:path";

import { appJwt, freshToken } from "../src/auth.ts";
import { acceptsCredential, parseCredential } from "../src/credential.ts";
import { gitEnvironment } from "../src/environment.ts";
import { launchCommand } from "../src/launch.ts";
import { patchTomlEnv, uninstallValues } from "../src/settings.ts";

describe("token renewal", () => {
  const now = Date.parse("2026-09-28T12:00:00Z");
  const valid = { token: "test-token", appId: "123", installationId: 456, expires_at: "2026-09-28T13:00:00Z" };

  test("reuses the correct unexpired installation token", () => {
    expect(freshToken(valid, "123", "456", now)).toEqual(valid);
  });

  test("renews five minutes early and rejects another app or installation", () => {
    expect(freshToken({ ...valid, expires_at: "2026-09-28T12:05:00Z" }, "123", "456", now)).toBeUndefined();
    expect(freshToken(valid, "999", "456", now)).toBeUndefined();
    expect(freshToken(valid, "123", "789", now)).toBeUndefined();
  });
});

test("JWT verifies cryptographically and compensates for clock skew", async () => {
  const path = resolve(import.meta.dir, "../../tmp", Bun.randomUUIDv7());
  await mkdir(path, { recursive: true });
  const { privateKey, publicKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
  const privateKeyPath = `${path}/key.pem`;
  await Bun.write(privateKeyPath, privateKey.export({ type: "pkcs8", format: "pem" }), { mode: 0o600 });
  const jwt = await appJwt({ appId: "123", clientId: "Iv1.example", privateKeyPath });
  const [header, payload, signature] = jwt.split(".");
  expect(verify("RSA-SHA256", Buffer.from(`${header}.${payload}`), publicKey, Buffer.from(signature, "base64url"))).toBe(true);
  const claims = JSON.parse(Buffer.from(payload, "base64url").toString());
  expect(claims.iss).toBe("Iv1.example");
  expect(claims.exp - claims.iat).toBe(600);
  expect(claims.iat).toBeLessThan(Math.floor(Date.now() / 1000));
  await rm(path, { recursive: true });
});

test("Git credential requests cannot disclose the token to another host or owner", () => {
  expect(acceptsCredential(parseCredential("protocol=https\nhost=github.com\npath=Leash-Labs/leash.git\n\n"))).toBe(true);
  for (const input of [
    "protocol=https\nhost=github.com.evil.test\npath=Leash-Labs/leash.git",
    "protocol=http\nhost=github.com\npath=Leash-Labs/leash.git",
    "protocol=https\nhost=github.com\npath=someone-else/leash.git",
    "protocol=https\nhost=github.com",
  ]) expect(acceptsCredential(parseCredential(input))).toBe(false);
});

test("agent environment overrides human authorship without losing inherited Git settings", () => {
  const env = gitEnvironment({ PATH: "/usr/bin", GIT_AUTHOR_NAME: "Jacob", GIT_CONFIG_COUNT: "1", GIT_CONFIG_KEY_0: "test.original", GIT_CONFIG_VALUE_0: "kept" });
  expect(env.GIT_AUTHOR_NAME).toBe("jacob-agent-team[bot]");
  expect(env.GIT_CONFIG_VALUE_0).toBe("kept");
  expect(env.GIT_CONFIG_KEY_1).toBe("credential.https://github.com.helper");
  expect(env.GIT_CONFIG_VALUE_1).toBe("");
});

test("Codex patch preserves unrelated settings and is idempotent", () => {
  const original = '[shell_environment_policy.set]\nEXISTING = "keep"\nPATH = "old"\n\n[features]\nexample = true\n';
  const updated = patchTomlEnv(original, { PATH: "/agent/bin:/usr/bin", GIT_AUTHOR_NAME: "bot" });
  expect(Bun.TOML.parse(updated)).toEqual({ shell_environment_policy: { set: { EXISTING: "keep", PATH: "/agent/bin:/usr/bin", GIT_AUTHOR_NAME: "bot" } }, features: { example: true } });
  expect(patchTomlEnv(updated, { PATH: "/agent/bin:/usr/bin", GIT_AUTHOR_NAME: "bot" })).toBe(updated);
});

test("uninstall restores previous values and preserves later user changes", () => {
  expect(uninstallValues({ PATH: "/agent/bin", GIT_AUTHOR_NAME: "new-choice", CUSTOM: "untouched" }, {
    installed: { PATH: "/agent/bin", GIT_AUTHOR_NAME: "bot", GH_TOKEN: "" },
    previous: { PATH: "/original/bin", GIT_AUTHOR_NAME: null, GH_TOKEN: null },
  })).toEqual({ PATH: "/original/bin" });
});

test("session launch supplies agent-specific overrides without passing inherited secrets as arguments", () => {
  const source = { PATH: "/usr/bin", GH_TOKEN: "human-secret", PRIVATE_KEY: "private-secret" };
  const claude = launchCommand(["claude", "--continue"], source);
  expect(claude[1]).toBe("--settings");
  expect(JSON.parse(claude[2]).env.GIT_AUTHOR_NAME).toBe("jacob-agent-team[bot]");
  expect(claude.at(-1)).toBe("--continue");
  const codex = launchCommand(["codex", "resume"], source);
  expect(codex).toContain('shell_environment_policy.set.GIT_AUTHOR_NAME="jacob-agent-team[bot]"');
  expect(codex.at(-1)).toBe("resume");
  expect(JSON.stringify([claude, codex])).not.toContain("secret");
  expect(launchCommand(["/bin/zsh", "-lc", "pwd"], source)).toEqual(["/bin/zsh", "-lc", "pwd"]);
});
