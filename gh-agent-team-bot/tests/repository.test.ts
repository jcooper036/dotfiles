import { expect, test } from "bun:test";
import { argumentRepository, parseRepository } from "../src/repository.ts";

test("GitHub remotes and PR URLs identify the repository", () => {
  for (const value of ["jcooper036/tunnel-tool", "git@github.com:jcooper036/tunnel-tool.git", "https://github.com/jcooper036/tunnel-tool/pull/1", "ssh://git@github.com:22/jcooper036/tunnel-tool.git"]) {
    expect(parseRepository(value)).toBe("jcooper036/tunnel-tool");
  }
  expect(parseRepository("https://github.com.evil.test/owner/repo")).toBeUndefined();
});

test("explicit repository arguments override context", () => {
  for (const args of [["pr", "create", "-R", "jcooper036/tunnel-tool"], ["pr", "list", "--repo=jcooper036/tunnel-tool"], ["issue", "list", "-Rjcooper036/tunnel-tool"], ["api", "/repos/jcooper036/tunnel-tool/pulls"], ["repo", "clone", "jcooper036/tunnel-tool"], ["pr", "view", "https://github.com/jcooper036/tunnel-tool/pull/2"]]) {
    expect(argumentRepository(args)).toBe("jcooper036/tunnel-tool");
  }
  expect(() => argumentRepository(["pr", "create", "--repo", "invalid"])).toThrow();
  expect(() => argumentRepository(["pr", "create", "-R", "Leash-Labs/leash", "--repo=jcooper036/tunnel-tool"])).toThrow("Conflicting");
});

test("URLs in issue bodies never change the selected identity", () => {
  expect(argumentRepository(["issue", "create", "--body", "https://github.com/jcooper036/tunnel-tool"])).toBeUndefined();
  expect(argumentRepository(["pr", "view", "--json", "number", "https://github.com/jcooper036/tunnel-tool/pull/2"])).toBe("jcooper036/tunnel-tool");
  expect(argumentRepository(["api", "--method", "POST", "repos/Leash-Labs/leash/issues", "--raw-field", "body", "https://github.com/jcooper036/tunnel-tool"])).toBe("Leash-Labs/leash");
});
