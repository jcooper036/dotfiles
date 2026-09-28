import { accessToken, rejectToken } from "./auth.ts";
import { owner } from "./config.ts";

export function parseCredential(input: string): Record<string, string> {
  return Object.fromEntries(input.split("\n").filter((line) => line.includes("=")).map((line) => {
    const separator = line.indexOf("=");
    return [line.slice(0, separator), line.slice(separator + 1)];
  }));
}

export function acceptsCredential(input: Record<string, string>): boolean {
  return input.protocol === "https" && input.host === "github.com"
    && input.path?.split("/")[0]?.toLowerCase() === owner.toLowerCase();
}

export async function credential(operation: string): Promise<void> {
  const input = parseCredential(await Bun.stdin.text());
  if (operation === "store") return;
  if (operation === "erase" && acceptsCredential(input)) return rejectToken();
  if (operation !== "get") return;
  if (!acceptsCredential(input)) {
    process.stdout.write("quit=true\n\n");
    return;
  }
  const issued = await accessToken();
  process.stdout.write(`username=x-access-token\npassword=${issued.token}\n\n`);
}
