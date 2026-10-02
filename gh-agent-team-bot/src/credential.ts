import { rejectToken } from "./auth.ts";
import { repositoryToken } from "./identity.ts";
import { parseRepository } from "./repository.ts";

export function parseCredential(input: string): Record<string, string> {
  return Object.fromEntries(input.split("\n").filter((line) => line.includes("=")).map((line) => {
    const separator = line.indexOf("=");
    return [line.slice(0, separator), line.slice(separator + 1)];
  }));
}

export function acceptsCredential(input: Record<string, string>): boolean {
  return input.protocol === "https" && input.host === "github.com"
    && parseRepository(input.path ?? "") !== undefined;
}

export async function credential(operation: string, source?: string, select = repositoryToken, output: (value: string) => void = (value) => { process.stdout.write(value); }): Promise<void> {
  const input = parseCredential(source ?? await Bun.stdin.text());
  if (operation === "store") return;
  if (operation === "erase" && acceptsCredential(input)) return rejectToken();
  if (operation !== "get") return;
  if (!acceptsCredential(input)) {
    output("quit=true\n\n");
    return;
  }
  const issued = await select(parseRepository(input.path)!);
  output(`username=x-access-token\npassword=${issued.token}\n\n`);
}
