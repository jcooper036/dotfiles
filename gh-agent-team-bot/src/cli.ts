import { accessToken } from "./auth.ts";
import { realGh, realGit } from "./config.ts";
import { credential } from "./credential.ts";
import { doctor } from "./doctor.ts";
import { gitEnvironment, type Environment } from "./environment.ts";
import { launchCommand } from "./launch.ts";

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
  const issued = await accessToken();
  await execute([realGh, ...args], {
    ...gitEnvironment(process.env), GH_TOKEN: issued.token, GITHUB_TOKEN: "", GH_DEBUG: "", GH_HOST: "github.com",
  });
}

async function main(): Promise<void> {
  const [command, ...args] = process.argv.slice(2);
  const commands: Record<string, () => Promise<void>> = {
    gh: () => gh(args),
    git: () => execute([realGit, ...args], gitEnvironment(process.env)),
    credential: () => credential(args[0]),
    doctor: () => doctor(args.includes("--refresh")),
    run: () => execute(launchCommand(args, process.env), gitEnvironment(process.env)),
  };
  if (!commands[command]) throw new Error("Usage: bun src/cli.ts <doctor [--refresh]|gh ...|git ...|credential ...|run COMMAND ...>");
  await commands[command]();
}

await main().catch((error: unknown) => {
  process.stderr.write(`gh-agent-team-bot: ${error instanceof Error ? error.message : "Operation failed"}\n`);
  process.exitCode = 1;
});
