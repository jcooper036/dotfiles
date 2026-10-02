import { realGit } from "./config.ts";
import { type Environment } from "./environment.ts";

export function parseRepository(value: string): string | undefined {
  const match = value.match(/^(?:https:\/\/github\.com\/|ssh:\/\/git@github\.com(?::22)?\/|git@github\.com:)?([\w.-]+)\/([\w.-]+)(?:\/.*)?$/);
  return match ? `${match[1]}/${match[2].replace(/\.git$/, "")}` : undefined;
}

export function argumentRepository(args: string[]): string | undefined {
  let selected: string | undefined;
  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index];
    if (argument === "-R" || argument === "--repo") {
      const repository = parseRepository(args[index + 1] ?? "");
      if (!repository) throw new Error("Expected a github.com owner/repository for --repo.");
      if (selected && selected.toLowerCase() !== repository.toLowerCase()) throw new Error("Conflicting repository arguments.");
      selected = repository;
      index += 1;
    }
    if (argument.startsWith("--repo=") || (argument.startsWith("-R") && argument.length > 2)) {
      const repository = parseRepository(argument.replace(/^(?:--repo=|-R)/, ""));
      if (!repository) throw new Error("Expected a github.com owner/repository for --repo.");
      if (selected && selected.toLowerCase() !== repository.toLowerCase()) throw new Error("Conflicting repository arguments.");
      selected = repository;
    }
  }
  if (selected) return selected;
  const url = args.find((argument) => argument.startsWith("https://github.com/"));
  if (url) return parseRepository(url);
  if (args[0] === "api") {
    const endpoint = args.find((argument) => /^\/?repos\//.test(argument));
    return endpoint ? parseRepository(endpoint.replace(/^\/?repos\//, "")) : undefined;
  }
  if (args[0] === "repo" && ["clone", "view", "fork", "create"].includes(args[1])) {
    const target = args[2];
    if (target && !target.startsWith("-")) return parseRepository(target);
  }
  return undefined;
}

export function localRepository(env: Environment, cwd = process.cwd()): string | undefined {
  if (env.GH_REPO) {
    const repository = parseRepository(env.GH_REPO);
    if (!repository) throw new Error("Expected a github.com owner/repository for GH_REPO.");
    return repository;
  }
  const result = Bun.spawnSync([realGit, "config", "--get-regexp", "^remote\\..*\\.(url|gh-resolved)$"], {
    cwd, env, stdout: "pipe", stderr: "pipe",
  });
  if (result.exitCode !== 0) return undefined;
  const entries = result.stdout.toString().trim().split("\n").map((line) => line.split(/\s+/, 2));
  const base = entries.find(([key, value]) => key.endsWith(".gh-resolved") && value === "base");
  const urls = entries.filter(([key]) => key.endsWith(".url"));
  const selected = base ? urls.find(([key]) => key === base[0].replace(/gh-resolved$/, "url")) : undefined;
  if (selected) return parseRepository(selected[1]);
  const repositories = [...new Set(urls.map(([, value]) => parseRepository(value)).filter((value) => value !== undefined))];
  if (repositories.length > 1) throw new Error("Multiple GitHub repositories: use --repo or GH_REPO to select authentication.");
  return repositories[0];
}

export function commandRepository(args: string[], env: Environment): string | undefined {
  return argumentRepository(args) ?? localRepository(env);
}

export function gitInvocation(args: string[]): { options: string[]; operation: string | undefined } {
  const paired = new Set(["-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"]);
  let index = 0;
  while (index < args.length && args[index].startsWith("-")) {
    index += paired.has(args[index]) ? 2 : 1;
  }
  return { options: args.slice(0, index), operation: args[index] };
}

export function gitRepository(options: string[], env: Environment, cwd: string): string | undefined {
  const result = Bun.spawnSync([realGit, ...options, "config", "--get", "remote.origin.url"], {
    cwd, env, stdout: "pipe", stderr: "pipe",
  });
  return result.exitCode === 0 ? parseRepository(result.stdout.toString().trim()) : undefined;
}
