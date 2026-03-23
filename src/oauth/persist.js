/**
 * Persist OAuth session in Apify key-value store (survives Actor restarts).
 */

import { Actor } from "apify";

const KV_KEY = "FIGMA_OAUTH_SESSION";

/**
 * @param {import('../figma/auth.js').FigmaAuth} auth
 */
export async function loadOAuthSessionFromKv(auth) {
  try {
    const raw = await Actor.getValue(KV_KEY);
    if (!raw) return;
    const data =
      typeof raw === "object" && raw !== null && !Buffer.isBuffer(raw)
        ? raw
        : JSON.parse(Buffer.isBuffer(raw) ? raw.toString("utf8") : String(raw));
    auth.restoreOAuthSession({
      accessToken: data.accessToken,
      refreshToken: data.refreshToken,
      expiresAt: data.expiresAt,
    });
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn("[OAuth] Could not load session from KV:", e.message);
  }
}

/**
 * @param {import('../figma/auth.js').FigmaAuth} auth
 */
export async function saveOAuthSessionToKv(auth) {
  const session = auth.getOAuthSessionForStorage();
  if (!session?.accessToken) return;
  await Actor.setValue(KV_KEY, {
    accessToken: session.accessToken,
    refreshToken: session.refreshToken,
    expiresAt: session.expiresAt,
  });
}

export { KV_KEY };
