import { accessToken } from "./auth.ts";
import { realGh, realGit } from "./config.ts";
import { credential } from "./credential.ts";
import { doctor } from "./doctor.ts";
import { gitEnvironment, type Environment } from "./environment.ts";
import { launchCommand } from "./launch.ts";
import { repositoryToken } from "./identity.ts";
import { commandRepository, gitInvocation, gitRepository } from "./repository.ts";

async function execute(command: string[], env: Environment): Promise<void> {
  const child = Bun.spawn(command, { env, stdin: "inherit", stdout: "inherit", stderr: "inherit" });
  const interrupt = (): void => { child.kill("SIGINT"); };
  const terminate = (): void => { child.kill("SIGTERM"); };
  process.on("SIGINT", interrupt);
  process.on("SIGTERM", terminate);
  const status = await child.exited;
  process.off("SIGINT", interrupt);
  process.off("SIGTERM", terminate);
  process.exitCode = status;
}

async function gh(args: string[]): Promise<void> {
  if (args[0] === "auth" && args[1] === "status") return doctor();
  const mutations = ["login", "logout", "switch", "refresh", "setup-git"];
  if (args[0] === "auth" && mutations.includes(args[1])) {
    throw new Error("Agent authentication is managed by gh-agent-team-bot. Use your ordinary terminal for personal gh authentication.");
  }
  const repository = commandRepository(args, process.env);
  const issued = repository ? await repositoryToken(repository) : await accessToken();
  if (repository && "login" in issued) process.stderr.write(`gh-agent-team-bot: ${repository} using ${issued.login}\n`);
  await execute([realGh, ...args], {
    ...gitEnvironment(process.env), GH_TOKEN: issued.token, GITHUB_TOKEN: "", GH_DEBUG: "", GH_HOST: "github.com",
  });
}

export async function gitCommandEnvironment(args: string[], source: Environment, select = repositoryToken, directory = process.cwd()): Promise<Environment> {
  const env = gitEnvironment(source);
  const { operation, options } = gitInvocation(args);
  if (!operation || !["commit", "merge", "cherry-pick", "rebase", "am", "tag"].includes(operation)) return env;
  const repository = gitRepository(options, source, directory);
  if (!repository) return env;
  const identity = await select(repository);
  process.stderr.write(`gh-agent-team-bot: ${repository} using ${identity.login}\n`);
  if (identity.login === "jcooper036") {
    for (const key of ["GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL"]) delete env[key];
  }
  return env;
}

async function main(): Promise<void> {
  const [command, ...args] = process.argv.slice(2);
  const commands: Record<string, () => Promise<void>> = {
    gh: () => gh(args),
    git: async () => execute([realGit, ...args], await gitCommandEnvironment(args, process.env)),
    credential: () => credential(args[0]),
    doctor: () => doctor(args.includes("--refresh")),
    run: () => execute(launchCommand(args, process.env), gitEnvironment(process.env)),
  };
  if (!commands[command]) throw new Error("Usage: bun src/cli.ts <doctor [--refresh]|gh ...|git ...|credential ...|run COMMAND ...>");
  await commands[command]();
}

if (import.meta.main) await main().catch((error: unknown) => {
  process.stderr.write(`gh-agent-team-bot: ${error instanceof Error ? error.message : "Operation failed"}\n`);
  process.exitCode = 1;
});
