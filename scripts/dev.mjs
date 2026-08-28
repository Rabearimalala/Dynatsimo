import { spawn } from "node:child_process";

const apiCommand = process.env.DYNATSIMO_PYTHON || "python";
const apiArgs = ["scripts/api-server.py"];
const viteCommand =
  process.platform === "win32" ? ".\\node_modules\\.bin\\vite.cmd" : "./node_modules/.bin/vite";
const viteArgs = ["--host", "127.0.0.1"];
const apiHealthUrl = `http://127.0.0.1:${process.env.DYNATSIMO_API_PORT || 8000}/api/health`;

function startProcess(command, args, name) {
  const child = spawn(command, args, {
    stdio: "inherit",
    shell: process.platform === "win32",
  });

  child.on("exit", (code) => {
    if (code && code !== 0) {
      console.error(`${name} stopped with code ${code}`);
      process.exitCode = code;
    }
  });

  return child;
}

async function waitForApi(maxAttempts = 40) {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    try {
      const response = await fetch(apiHealthUrl);
      if (response.ok) {
        return true;
      }
    } catch {
      // keep waiting
    }

    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  return false;
}

const apiProcess = startProcess(apiCommand, apiArgs, "API");
const apiReady = await waitForApi();

if (!apiReady) {
  console.warn("API not ready yet, starting Vite anyway.");
}

const viteProcess = startProcess(viteCommand, viteArgs, "Vite");

const shutdown = () => {
  apiProcess.kill();
  viteProcess.kill();
};

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
