const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    backgroundColor: '#0f172a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    autoHideMenuBar: true,
  });

  // Vite default port is 5173
  const startUrl = process.env.ELECTRON_START_URL || `file://${path.join(__dirname, '../dist/index.html')}`;
  mainWindow.loadURL(startUrl);
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// --- Helper: Find Git Root ---
function findGitRoot() {
  // In portable mode, the exe runs from temp, but PORTABLE_EXECUTABLE_DIR tells us where the exe really is.
  // In dev, we start from __dirname.
  let currentPath = app.isPackaged
    ? (process.env.PORTABLE_EXECUTABLE_DIR || path.dirname(app.getPath('exe')))
    : __dirname;

  const root = path.parse(currentPath).root;

  while (currentPath && currentPath !== root) {
    if (fs.existsSync(path.join(currentPath, '.git'))) {
      return currentPath;
    }
    currentPath = path.dirname(currentPath);
  }
  return null;
}

// --- IPC Handlers ---

ipcMain.handle('run-installer', async (event, driveLetter) => {
  return new Promise((resolve, reject) => {
    const isProd = app.isPackaged;
    const scriptName = 'install_for_gui.py';
    const gitRoot = findGitRoot();

    let scriptPath;

    // Try to find the script in the repo first (CoreFiles)
    if (gitRoot) {
      const repoScriptPath = path.join(gitRoot, 'CoreFiles', scriptName);
      if (fs.existsSync(repoScriptPath)) {
        scriptPath = repoScriptPath;
      }
    }

    // Fallback to resources if not found in repo (or if gitRoot not found)
    if (!scriptPath) {
      scriptPath = isProd
        ? path.join(process.resourcesPath, scriptName)
        : path.join(__dirname, '../../CoreFiles', scriptName);
    }

    const scriptDir = path.dirname(scriptPath);

    if (!fs.existsSync(scriptPath)) {
      event.sender.send('installer-log', { message: `Error: install_for_gui.py not found at ${scriptPath}`, type: 'error' });
      resolve({ success: false });
      return;
    }

    event.sender.send('installer-log', { message: `> python "${scriptPath}" ${driveLetter}`, type: 'info' });

    const pythonProcess = spawn('python', [scriptName, driveLetter], {
      cwd: scriptDir
    });

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        event.sender.send('installer-log', { message: output, type: 'info' });
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        event.sender.send('installer-log', { message: output, type: 'info' });
      }
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        event.sender.send('installer-log', { message: 'Process finished successfully.', type: 'success' });
        resolve({ success: true });
      } else {
        event.sender.send('installer-log', { message: `Process exited with code ${code}`, type: 'error' });
        resolve({ success: false });
      }
    });
  });
});

ipcMain.handle('git-checkout', async (event, branchName) => {
  return new Promise((resolve, reject) => {
    const gitRoot = findGitRoot();

    if (!gitRoot) {
      resolve({ success: false, error: "Could not find .git repository. Make sure the launcher is inside the DowagerMod repository." });
      return;
    }

    const command = `git fetch origin && git checkout ${branchName} && git pull origin ${branchName}`;

    exec(command, { cwd: gitRoot }, (error, stdout, stderr) => {
      if (error) {
        console.error(`exec error: ${error}`);
        resolve({ success: false, error: error.message });
        return;
      }
      resolve({ success: true, output: stdout });
    });
  });
});

ipcMain.handle('launch-game', async (event, driveLetter) => {
  return new Promise((resolve, reject) => {
    const drive = driveLetter || 'C';
    const gamePath = path.join(drive + ':', 'Program Files (x86)', 'Steam', 'steamapps', 'common', "Sid Meier's Civilization IV Beyond the Sword", 'Beyond the Sword', 'Civ4BeyondSword.exe');

    if (!fs.existsSync(gamePath)) {
      resolve({ success: false, error: `Game executable not found at: ${gamePath}` });
      return;
    }

    // Spawn the game process detached so the launcher can close independently
    const gameProcess = spawn(gamePath, [], {
      detached: true,
      stdio: 'ignore'
    });

    gameProcess.unref();
    resolve({ success: true });
  });
});