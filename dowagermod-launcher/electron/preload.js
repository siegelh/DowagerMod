const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  runInstaller: (driveLetter) => ipcRenderer.invoke('run-installer', driveLetter),
  checkoutBranch: (branchName) => ipcRenderer.invoke('git-checkout', branchName),
  launchGame: (driveLetter) => ipcRenderer.invoke('launch-game', driveLetter),
  onInstallerLog: (callback) => {
    const subscription = (event, data) => callback(data);
    ipcRenderer.on('installer-log', subscription);
    // Return cleanup function
    return () => ipcRenderer.removeListener('installer-log', subscription);
  }
});