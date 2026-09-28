import { z } from "zod";

import { accessToken, api, appJwt, installation } from "./auth.ts";
import { botLogin, loadConfig } from "./config.ts";

const reposSchema = z.object({
  total_count: z.number(),
  repositories: z.array(z.object({ full_name: z.string() })),
});

export async function doctor(force = false): Promise<void> {
  const config = await loadConfig();
  const installed = await installation(config, await appJwt(config));
  const issued = await accessToken(force);
  const repositories = reposSchema.parse(await api("/installation/repositories?per_page=100", issued.token));
  process.stdout.write(`${JSON.stringify({
    login: botLogin,
    app_id: installed.app_id,
    installation_id: installed.id,
    account: installed.account.login,
    repository_selection: installed.repository_selection,
    permissions: installed.permissions,
    token_expires_at: issued.expires_at,
    repository_count: repositories.total_count,
    repositories: repositories.repositories.map((repo) => repo.full_name),
  }, null, 2)}\n`);
}
