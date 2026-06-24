import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

const explicitTargetUrl = process.env.LAUNCH_STATUS_BROWSER_SMOKE_URL || process.argv[2] || "";
const expectedDeployCommit = process.env.JYOTISH_PUBLIC_EXPECTED_DEPLOY_COMMIT || process.argv[3] || "launch-status-browser-smoke";
const browserPath = process.env.BROWSER_EXECUTABLE_PATH || findBrowserExecutable();

if (!browserPath) {
  console.error("No Chrome/Edge/Chromium executable found. Set BROWSER_EXECUTABLE_PATH to run this browser smoke.");
  process.exit(1);
}

const userDataDir = await mkdtemp(path.join(tmpdir(), "jyotish-launch-status-smoke-"));
const debugPort = 9700 + Math.floor(Math.random() * 500);
const browser = spawn(browserPath, [
  "--headless",
  "--disable-gpu",
  "--no-sandbox",
  "--disable-extensions",
  "--disable-background-networking",
  "--disable-crash-reporter",
  "--ignore-certificate-errors",
  "--disable-dev-shm-usage",
  "--no-first-run",
  "--no-default-browser-check",
  `--remote-debugging-port=${debugPort}`,
  `--user-data-dir=${userDataDir}`,
  "about:blank",
], { stdio: "ignore" });

let ws;
let nextServer;
let asyncEventError;
let healthFetches = 0;

const targetUrl = explicitTargetUrl || await startLocalNextServer();

try {
  const version = await waitForJson(`http://127.0.0.1:${debugPort}/json/version`);
  ws = await connectCdp(version.webSocketDebuggerUrl);
  const { targetId } = await ws.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await ws.send("Target.attachToTarget", { targetId, flatten: true });
  const pageCdp = { send: (method, params = {}) => ws.send(method, params, sessionId) };

  ws.onEvent(async (message) => {
    if (message.method !== "Fetch.requestPaused") return;
    const params = message.params;
    try {
      const requestUrl = new URL(params.request.url);
      const requestPath = requestUrl.pathname.replace(/\/$/, "");
      if (requestPath === "/api/health") {
        healthFetches += 1;
        await fulfillJson(pageCdp, params.requestId, {
          status: "ok",
          service: "jyotish-agent",
          debug: false,
          deploy_commit: expectedDeployCommit,
        });
        return;
      }
      if (requestPath === "/api/auth/me") {
        await fulfillJson(pageCdp, params.requestId, { user: null });
        return;
      }
      await pageCdp.send("Fetch.continueRequest", { requestId: params.requestId });
    } catch (error) {
      await pageCdp.send("Fetch.failRequest", { requestId: params.requestId, errorReason: "Failed" });
      throw error;
    }
  });

  await pageCdp.send("Page.enable");
  await pageCdp.send("Runtime.enable");
  await pageCdp.send("Fetch.enable", { patterns: [{ urlPattern: "*://*/api/*" }] });
  await pageCdp.send("Page.navigate", { url: targetUrl });

  await waitForPageCondition(pageCdp, "Boolean(document.querySelector('[data-launch-live-health-stage=\"E153-A\"]'))", "E153 launch status panel");
  await waitFor(async () => healthFetches > 0, "/api/health browser request");
  await waitForPageCondition(
    pageCdp,
    `document.querySelector('[data-launch-live-health-stage="E153-A"]')?.innerText.includes(${JSON.stringify(expectedDeployCommit)})`,
    "rendered deploy commit",
  );

  const state = await evaluate(pageCdp, `(() => {
    const panel = document.querySelector('[data-launch-live-health-stage="E153-A"]');
    const text = panel?.innerText || "";
    const hidden = document.body.textContent || "";
    return {
      hasPanel: Boolean(panel),
      statusOk: text.includes("ok"),
      serviceRendered: text.includes("jyotish-agent"),
      deployCommitRendered: text.includes(${JSON.stringify(expectedDeployCommit)}),
      healthFetchObservedMarker: hidden.includes("launch_status_live_health_check_enabled=true"),
      deployCommitMarker: hidden.includes("launch_status_live_deploy_commit_visible=true"),
      contractStageMarker: hidden.includes("data-launch-live-health-stage=E153-A"),
    };
  })()`);

  assert(state.hasPanel, "Live health panel must exist.");
  assert(state.statusOk, "Live health panel must render ok status.");
  assert(state.serviceRendered, "Live health panel must render service name.");
  assert(state.deployCommitRendered, "Live health panel must render deploy commit.");
  assert(state.healthFetchObservedMarker, "Launch status hidden marker must expose live health check.");
  assert(state.deployCommitMarker, "Launch status hidden marker must expose deploy commit visibility.");
  assert(state.contractStageMarker, "Launch status hidden marker must expose E153 stage.");

  console.log(JSON.stringify({
    status: "ok",
    checkedUrl: targetUrl,
    expectedDeployCommit,
    healthFetches,
    markers: [
      'data-launch-live-health-stage="E153-A"',
      "launch_status_browser_health_fetch_observed=true",
      "launch_status_browser_deploy_commit_rendered=true",
    ],
  }, null, 2));
} finally {
  if (ws) ws.close();
  browser.kill();
  await waitForProcessExit(browser);
  if (nextServer) {
    nextServer.kill();
    await waitForProcessExit(nextServer);
  }
  await cleanupTempDir(userDataDir);
}

function findBrowserExecutable() {
  const candidates = process.platform === "win32"
    ? [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        ...findCachedWindowsChromes(),
      ]
    : [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
      ];
  return candidates.find((candidate) => {
    try {
      return Boolean(existsSync(candidate));
    } catch {
      return false;
    }
  });
}

function findCachedWindowsChromes() {
  const localAppData = process.env.LOCALAPPDATA || path.join(process.env.USERPROFILE || "", "AppData", "Local");
  const home = process.env.USERPROFILE || "";
  return [
    path.join(localAppData, "ms-playwright", "chromium-1169", "chrome-win", "chrome.exe"),
    path.join(home, ".cache", "puppeteer", "chrome", "win64-148.0.7778.97", "chrome-win64", "chrome.exe"),
  ];
}

async function startLocalNextServer() {
  const port = 3500 + Math.floor(Math.random() * 500);
  const nextBin = path.join(process.cwd(), "node_modules", "next", "dist", "bin", "next");
  nextServer = spawn(process.execPath, [nextBin, "dev", "--hostname", "127.0.0.1", "--port", String(port)], {
    cwd: process.cwd(),
    env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" },
    stdio: "ignore",
  });
  const url = `http://127.0.0.1:${port}/launch-status`;
  await waitFor(async () => {
    try {
      const response = await fetch(url, { redirect: "manual" });
      return response.status >= 200 && response.status < 500;
    } catch {
      return false;
    }
  }, "local Next dev server");
  return url;
}

async function connectCdp(webSocketUrl) {
  const socket = new WebSocket(webSocketUrl);
  const pending = new Map();
  const eventHandlers = [];
  let nextId = 1;
  let intentionalClose = false;
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });
  socket.addEventListener("message", async (event) => {
    const message = JSON.parse(await messageDataToText(event.data));
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result || {});
      return;
    }
    for (const handler of eventHandlers) {
      Promise.resolve(handler(message)).catch((error) => {
        asyncEventError = error;
      });
    }
  });
  socket.addEventListener("close", () => {
    if (intentionalClose) return;
    asyncEventError = asyncEventError || new Error("CDP WebSocket closed before response.");
    for (const { resolve } of pending.values()) resolve({});
    pending.clear();
  });
  return {
    send(method, params = {}, sessionId = undefined) {
      const id = nextId++;
      socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
      return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
    },
    onEvent(handler) {
      eventHandlers.push(handler);
    },
    close() {
      intentionalClose = true;
      socket.close();
    },
  };
}

async function fulfillJson(cdp, requestId, payload) {
  await cdp.send("Fetch.fulfillRequest", {
    requestId,
    responseCode: 200,
    responseHeaders: [{ name: "Content-Type", value: "application/json" }],
    body: Buffer.from(JSON.stringify(payload), "utf8").toString("base64"),
  });
}

async function waitForJson(url) {
  let lastError;
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return response.json();
    } catch (error) {
      lastError = error;
    }
    await delay(100);
  }
  throw lastError || new Error(`Timed out waiting for ${url}`);
}

async function waitForPageCondition(cdp, expression, label) {
  await waitFor(async () => Boolean(await evaluate(cdp, expression)), label);
}

async function waitFor(predicate, label) {
  for (let attempt = 0; attempt < 300; attempt += 1) {
    if (asyncEventError) throw asyncEventError;
    if (await predicate()) return;
    await delay(100);
  }
  throw new Error(`Timed out waiting for ${label}.`);
}

async function evaluate(cdp, expression) {
  const result = await cdp.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || "Runtime.evaluate failed");
  }
  return result.result?.value;
}

async function messageDataToText(data) {
  if (typeof data === "string") return data;
  if (data instanceof ArrayBuffer) return Buffer.from(data).toString("utf8");
  if (ArrayBuffer.isView(data)) return Buffer.from(data.buffer, data.byteOffset, data.byteLength).toString("utf8");
  if (data && typeof data.text === "function") return data.text();
  return String(data);
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function waitForProcessExit(processHandle) {
  return new Promise((resolve) => {
    if (processHandle.exitCode !== null) {
      resolve();
      return;
    }
    const timer = setTimeout(resolve, 3000);
    processHandle.once("exit", () => {
      clearTimeout(timer);
      resolve();
    });
  });
}

async function cleanupTempDir(dir) {
  for (let attempt = 0; attempt < 5; attempt += 1) {
    try {
      await rm(dir, { recursive: true, force: true });
      return;
    } catch (error) {
      if (attempt === 4) {
        console.warn(`Could not remove browser temp dir ${dir}: ${error.message}`);
        return;
      }
      await delay(250);
    }
  }
}
