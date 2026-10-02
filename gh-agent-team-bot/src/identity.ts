import { homedir } from "node:os";
import { join } from "node:path";
import { z } from "zod";

import { accessToken, api } from "./auth.ts";
import { botLogin, owner, realGh } from "./config.ts";
import { type Environment } from "./environment.ts";

export const personalLogin = "jcooper036";
const accountSchema = z.object({ login: z.string() });
const repositoriesSchema = z.object({
  total_count: z.number().int().nonnegative(),
  repositories: z.array(z.object({ full_name: z.string() })),
});
const repositorySchema = z.string().regex(/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/);

export type RepositoryIdentity = { token: string; login: string };
export type IdentityDependencies = {
  botToken: () => Promise<{ token: string }>;
  request: typeof api;
  personal: () => Promise<string>;
};
export type PersonalDependencies = {
  readToken: () => Promise<string>;
  request: typeof api;
};

export function personalEnvironment(source: Environment): Environment {
  return {
    ...source,
    GH_CONFIG_DIR: join(source.XDG_CONFIG_HOME || join(homedir(), ".config"), "gh"),
    GH_TOKEN: "",
    GITHUB_TOKEN: "",
    GH_ENTERPRISE_TOKEN: "",
    GITHUB_ENTERPRISE_TOKEN: "",
    GH_DEBUG: "",
    GH_HOST: "github.com",
    GH_PROMPT_DISABLED: "1",
  };
}

async function readPersonalToken(): Promise<string> {
  const child = Bun.spawn([realGh, "auth", "token", "--hostname", "github.com", "--user", personalLogin], {
    env: personalEnvironment(process.env), stdout: "pipe", stderr: "pipe",
  });
  const [output, , status] = await Promise.all([
    new Response(child.stdout).text(), new Response(child.stderr).text(), child.exited,
  ]);
  if (status !== 0) throw new Error(`Cannot load saved GitHub authentication for ${personalLogin}: gh exited ${status}.`);
  return z.string().min(1).parse(output.trim());
}

export async function personalToken(dependencies: PersonalDependencies = { readToken: readPersonalToken, request: api }): Promise<string> {
  const token = await dependencies.readToken();
  const account = accountSchema.parse(await dependencies.request("/user", token));
  if (account.login.toLowerCase() !== personalLogin.toLowerCase()) {
    throw new Error(`Saved GitHub authentication must belong to ${personalLogin}; received ${account.login}.`);
  }
  return token;
}

async function installedRepository(repository: string, token: string, request: typeof api): Promise<boolean> {
  let seen = 0;
  for (let index = 0; ; index += 1) {
    const page = repositoriesSchema.parse(await request(`/installation/repositories?per_page=100&page=${index + 1}`, token));
    if (page.repositories.some((entry) => entry.full_name.toLowerCase() === repository.toLowerCase())) return true;
    seen += page.repositories.length;
    if (seen >= page.total_count) return false;
    if (!page.repositories.length) throw new Error("GitHub installation repository pagination ended before total_count.");
  }
}

export async function repositoryToken(repository: string, dependencies: IdentityDependencies = {
  botToken: accessToken, request: api, personal: personalToken,
}): Promise<RepositoryIdentity> {
  const normalized = repositorySchema.parse(repository.replace(/\.git$/, ""));
  if (normalized.split("/")[0].toLowerCase() === owner.toLowerCase()) {
    const issued = await dependencies.botToken();
    if (await installedRepository(normalized, issued.token, dependencies.request)) return { token: issued.token, login: botLogin };
  }
  return { token: await dependencies.personal(), login: personalLogin };
}
