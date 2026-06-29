const { spawn } = require("child_process");
const path = require("path");

const FRONTEND_DIR = __dirname;

console.log("==========================================================");
console.log("STARTING NEXT.JS FRONTEND DEVELOPMENT SERVER");
console.log("==========================================================\n");

// Spawn next dev process using cmd.exe wrapper on Windows, or direct shell on other platforms
const isWindows = process.platform === "win32";
const command = isWindows ? "cmd" : "npm";
const args = isWindows ? ["/c", "npm run dev"] : ["run", "dev"];

const devServer = spawn(command, args, {
  cwd: FRONTEND_DIR,
  stdio: "inherit",
  shell: true
});

devServer.on("error", (error) => {
  console.error("\n[ERROR] Failed to start frontend dev server:", error);
});

devServer.on("close", (code) => {
  console.log(`\nFrontend dev server stopped with code: ${code}`);
});
