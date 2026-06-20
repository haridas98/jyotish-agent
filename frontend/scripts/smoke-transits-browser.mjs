import { mkdtemp, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";

const explicitTargetUrl = process.env.TRANSITS_BROWSER_SMOKE_URL || "";
const browserPath = process.env.BROWSER_EXECUTABLE_PATH || findBrowserExecutable();
const forbiddenMarkers = ["source.pending", "rawEvidence", "Missing calculations", "sourceRuleIds", "movable_to_fixed", "fixed_to_movable", "dual_to_dual"];
const forbiddenGrahaRowMarkers = ["transit:", "natal:", "special_", "general_", "sourceRuleIds", "rawEvidence"];

if (!browserPath) {
  console.error("No Chrome/Edge/Chromium executable found. Set BROWSER_EXECUTABLE_PATH to run this browser smoke.");
  process.exit(1);
}

const profile = {
  id: 1,
  display_name: "Smoke Transit Chart",
  birth_date: "1998-04-30",
  birth_time: "13:45:00",
  birth_time_accuracy: "exact",
  place: { label: "Sterlitamak, Bashkortostan, RU", latitude: 53.6304, longitude: 55.9308, timezone: "+06:00" },
};

const transitWorkbench = buildTransitWorkbenchFixture();

const userDataDir = await mkdtemp(path.join(tmpdir(), "jyotish-transits-smoke-"));
const debugPort = 9300 + Math.floor(Math.random() * 500);
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

let apiTransitRequests = 0;
let ws;
let asyncEventError;
let nextServer;

const targetUrl = explicitTargetUrl || await startLocalNextServer();

try {
  const version = await waitForJson(`http://127.0.0.1:${debugPort}/json/version`);
  ws = await connectCdp(version.webSocketDebuggerUrl);
  const { targetId } = await ws.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await ws.send("Target.attachToTarget", { targetId, flatten: true });
  const pageCdp = { send: (method, params = {}) => ws.send(method, params, sessionId) };
  await delay(200);

  ws.onEvent(async (message) => {
    if (message.method !== "Fetch.requestPaused") return;
    const params = message.params;
    try {
      const requestUrl = new URL(params.request.url);
      const requestPath = requestUrl.pathname.replace(/\/$/, "");
      await delay(1);
      console.log(`request ${requestPath}`);
      if (requestPath === "/api/auth/me") {
        await delay(50);
        await fulfillJson(pageCdp, params.requestId, { user: { id: "admin", username: "admin", role: "staff" } });
        return;
      }
      if (requestPath === "/api/charts") {
        await delay(50);
        await fulfillJson(pageCdp, params.requestId, { profiles: [profile] });
        return;
      }
      if (requestPath === "/api/charts/1/transit-workbench") {
        apiTransitRequests += 1;
        await delay(50);
        await fulfillJson(pageCdp, params.requestId, transitWorkbench);
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
  await delay(500);
  console.log(`page ${await evaluate(pageCdp, "location.href")}`);

  await waitForPageCondition(pageCdp, "Boolean(document.querySelector('[aria-label=\"Режим отображения\"]'))", "display mode switch");
  await waitFor(async () => apiTransitRequests > 0, "transit workbench API request");

  const defaultState = await evaluate(pageCdp, `(() => {
    const bodyText = document.body.innerText;
    return {
      hasGrahaLayer: Boolean(document.querySelector('[aria-label="Graha Drishti aspect layer"]')),
      hasRashiLayer: Boolean(document.querySelector('[aria-label="Rashi Drishti aspect layer"]')),
      forbiddenHits: ${JSON.stringify(forbiddenMarkers)}.filter((marker) => bodyText.includes(marker)),
    };
  })()`);
  assert(defaultState.hasGrahaLayer === false, "Graha Drishti must be hidden in default novice mode.");
  assert(defaultState.hasRashiLayer === false, "Rashi Drishti must be hidden in default novice mode.");
  assert(defaultState.forbiddenHits.length === 0, `Default novice UI leaked forbidden markers: ${defaultState.forbiddenHits.join(", ")}`);

  await evaluate(pageCdp, `document.querySelector('[aria-label="Режим отображения"] button:nth-of-type(2)').click()`);
  await waitForPageCondition(pageCdp, "Boolean(document.querySelector('[aria-label=\"Graha Drishti aspect layer\"]')) && Boolean(document.querySelector('[aria-label=\"Rashi Drishti aspect layer\"]'))", "expert aspect layer controls");

  const expertState = await evaluate(pageCdp, `(() => ({
    hasGrahaLayer: Boolean(document.querySelector('[aria-label="Graha Drishti aspect layer"]')),
    hasRashiLayer: Boolean(document.querySelector('[aria-label="Rashi Drishti aspect layer"]')),
    linesVisibleByDefault: Boolean(document.querySelector('.transit-aspect-lines')),
  }))()`);
  assert(expertState.hasGrahaLayer === true, "Graha Drishti control must appear in astrologer mode.");
  assert(expertState.hasRashiLayer === true, "Rashi Drishti control must appear in astrologer mode.");
  assert(expertState.linesVisibleByDefault === false, "Aspect layers must stay collapsed by default in astrologer mode.");

  await evaluate(pageCdp, `document.querySelector('[aria-label="Graha Drishti aspect layer"] button').click()`);
  await waitForPageCondition(pageCdp, "Boolean(document.querySelector('[aria-label=\"Graha Drishti aspect layer\"] .transit-aspect-lines'))", "expanded Graha Drishti lines");

  const grahaExpanded = await evaluate(pageCdp, `(() => {
    const lines = document.querySelector('[aria-label="Graha Drishti aspect layer"] .transit-aspect-lines');
    const text = lines?.innerText || "";
    return {
      rowCount: lines?.querySelectorAll("span").length || 0,
      forbiddenHits: ${JSON.stringify(forbiddenGrahaRowMarkers)}.filter((marker) => text.includes(marker)),
    };
  })()`);
  assert(grahaExpanded.rowCount > 0, "Expanded Graha Drishti layer must render aspect rows.");
  assert(grahaExpanded.forbiddenHits.length === 0, `Expanded Graha Drishti leaked raw markers: ${grahaExpanded.forbiddenHits.join(", ")}`);

  await evaluate(pageCdp, `document.querySelector('[aria-label="Rashi Drishti aspect layer"] button').click()`);
  await waitForPageCondition(pageCdp, "Boolean(document.querySelector('[aria-label=\"Rashi Drishti aspect layer\"] .transit-aspect-lines'))", "expanded Rashi Drishti lines");

  const rashiExpanded = await evaluate(pageCdp, `(() => {
    const text = document.querySelector('[aria-label="Rashi Drishti aspect layer"]')?.innerText || "";
    return {
      textLength: text.length,
      forbiddenHits: ${JSON.stringify(forbiddenMarkers)}.filter((marker) => text.includes(marker)),
    };
  })()`);
  assert(rashiExpanded.textLength > 0, "Expanded Rashi Drishti layer must render aspect rows.");
  assert(rashiExpanded.forbiddenHits.length === 0, `Expanded Rashi Drishti leaked raw markers: ${rashiExpanded.forbiddenHits.join(", ")}`);

  console.log("Transits browser smoke passed.");
} finally {
  if (ws) ws.close();
  browser.kill();
  await waitForBrowserExit(browser);
  if (nextServer) {
    nextServer.kill();
    await waitForBrowserExit(nextServer);
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
  socket.addEventListener("error", () => {
    if (intentionalClose) return;
    asyncEventError = asyncEventError || new Error("CDP WebSocket error.");
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

async function messageDataToText(data) {
  if (typeof data === "string") return data;
  if (data instanceof ArrayBuffer) return Buffer.from(data).toString("utf8");
  if (ArrayBuffer.isView(data)) return Buffer.from(data.buffer, data.byteOffset, data.byteLength).toString("utf8");
  if (data && typeof data.text === "function") return data.text();
  return String(data);
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

async function createPageTarget(debugPort) {
  const response = await fetch(`http://127.0.0.1:${debugPort}/json/new?about:blank`, { method: "PUT" });
  if (!response.ok) throw new Error(`Could not create page target: HTTP ${response.status}`);
  return response.json();
}

async function startLocalNextServer() {
  const port = 3300 + Math.floor(Math.random() * 500);
  const nextBin = path.join(process.cwd(), "node_modules", "next", "dist", "bin", "next");
  nextServer = spawn(process.execPath, [nextBin, "dev", "--hostname", "127.0.0.1", "--port", String(port)], {
    cwd: process.cwd(),
    env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" },
    stdio: "ignore",
  });
  const url = `http://127.0.0.1:${port}/transits`;
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

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function waitForBrowserExit(processHandle) {
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

function buildTransitWorkbenchFixture() {
  const houses = Array.from({ length: 12 }, (_, index) => ({ house: index + 1, rashi: rashiName(index), rashi_index: index }));
  const grahaBodies = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"];
  const grahas = grahaBodies.map((body, index) => ({
    body,
    longitude: 10 + index * 12,
    rashi: rashiName(index),
    rashi_index: index,
    nakshatra: "Ashwini",
    pada: 1,
  }));
  const specialPoints = [{ body: "Lagna", longitude: 90, rashi: "Cancer", rashi_index: 3, nakshatra: "Pushya", pada: 1 }];
  return {
    schemaVersion: "transit-workbench.v3",
    chartId: 1,
    hasCalculation: true,
    transitMoment: { isoDateTime: "2026-06-20T12:30:00", timezone: "UTC" },
    location: { label: "Sterlitamak", latitude: 53.6304, longitude: 55.9308, timezone: "+06:00" },
    scopeId: "D1",
    grahas,
    specialPoints,
    houses,
    rashis: houses,
    natal: { hasCalculation: true, grahas, specialPoints, houses, rashis: houses },
    overlay: {
      supportsNatalOverlay: true,
      supportedViews: ["transit_only", "overlay", "side_by_side"],
      defaultView: "transit_only",
      housesRelativeTo: "natal",
      legendRequired: true,
      natalObjectCount: 10,
      transitObjectCount: 10,
      aspects: true,
      orbs: false,
      ai: false,
      rawEvidence: false,
    },
    aspectLayer: {
      methodId: "aspect.graha_drishti.parashara.v1",
      sourceStatus: "verified",
      enabledByDefault: false,
      availableInModes: ["astrologer"],
      aspectCount: 2,
      sampleRefs: [
        { sourceEntityRef: "transit:graha.SA", targetEntityRef: "natal:house.10", aspectKind: "special_10th", signDistance: 10 },
        { sourceEntityRef: "transit:graha.JU", targetEntityRef: "natal:graha.MO", aspectKind: "special_5th", signDistance: 5 },
      ],
    },
    rashiAspectLayer: {
      methodId: "aspect.rashi_drishti.parashara.v1",
      sourceStatus: "verified",
      enabledByDefault: false,
      availableInModes: ["astrologer"],
      aspectCount: 2,
      sampleRefs: [
        { sourceEntityRef: "transit:rashi.Aries", targetEntityRef: "natal:house.5", aspectKind: "movable_to_fixed", sourceRashiIndex: 0, targetRashiIndex: 4 },
        { sourceEntityRef: "transit:rashi.Gemini", targetEntityRef: "natal:graha.JU", aspectKind: "dual_to_dual", sourceRashiIndex: 2, targetRashiIndex: 8 },
      ],
    },
    entityInspectorCount: 1,
    method: { methodId: "transit.d1.drik.v1", methodVersion: 1, positionContext: "transit" },
    capabilities: { natalOverlay: true, aspects: true, ashtakavarga: false, sadeSati: false, ai: false, rawEvidence: false },
    warnings: [],
  };
}

function rashiName(index) {
  return ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"][index % 12];
}
