import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  MonitorPlay,
  DownloadCloud,
  Settings,
  ArrowLeft,
  CheckCircle,
  Play,
  HardDrive,
  Save,
  FolderOpen,
  Terminal as TerminalIcon
} from 'lucide-react';

import { AppView, GitHubBranch, LogEntry } from './types';
import { fetchBranches } from './services/githubService';
import { Button } from './components/Button';
import { BranchList } from './components/BranchList';
import { Terminal } from './components/Terminal';

// Default path template matching the python script logic
const PATH_SUFFIX = ":\\Program Files (x86)\\Steam\\steamapps\\common\\Sid Meier's Civilization IV Beyond the Sword";

const HARRISON_MOD_BANNER = `
***################***************###*******#*******************************************************
***################*********************************************************************************
... (HarrisonMod ASCII Art) ...
`;

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>(AppView.MENU);
  const [branches, setBranches] = useState<GitHubBranch[]>([]);
  const [selectedBranch, setSelectedBranch] = useState<GitHubBranch | null>(null);
  const [isLoadingBranches, setIsLoadingBranches] = useState(false);
  const [updateProgress, setUpdateProgress] = useState(0);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isReadyToInstall, setIsReadyToInstall] = useState(false);
  const [isInstalling, setIsInstalling] = useState(false);
  const [installComplete, setInstallComplete] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isElectron, setIsElectron] = useState(false);

  // Settings State
  const [installDrive, setInstallDrive] = useState<string>('');
  const [showDriveModal, setShowDriveModal] = useState(false);
  const [tempDrive, setTempDrive] = useState<string>('C');

  // Helper to add logs
  const addLog = useCallback((message: string, type: LogEntry['type'] = 'info') => {
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs(prev => [...prev, { timestamp, message, type }]);
  }, []);

  // Check if running in Electron on mount and setup listeners
  useEffect(() => {
    const electronAvailable = !!window.electronAPI;
    setIsElectron(electronAvailable);

    const savedDrive = localStorage.getItem('dowager_install_drive');
    if (savedDrive) setInstallDrive(savedDrive);

    // Setup listener for Electron logs if available
    if (electronAvailable && window.electronAPI) {
      const cleanup = window.electronAPI.onInstallerLog((log) => {
        addLog(log.message, log.type as LogEntry['type']);
      });
      return () => cleanup();
    }
  }, [addLog]);

  // Load branches when entering UPDATES view
  useEffect(() => {
    if (currentView === AppView.UPDATES && branches.length === 0) {
      setIsLoadingBranches(true);
      fetchBranches()
        .then(data => {
          setBranches(data);
          if (data.length > 0) setSelectedBranch(data[0]);
        })
        .catch(err => console.error(err))
        .finally(() => setIsLoadingBranches(false));
    }
  }, [currentView, branches]);

  const saveSettings = (drive: string) => {
    setInstallDrive(drive);
    localStorage.setItem('dowager_install_drive', drive);
  };

  const handleDriveSelection = () => {
    saveSettings(tempDrive);
    setShowDriveModal(false);

    if (currentView === AppView.UPDATES && selectedBranch) {
      handleUpdateRepo(true);
    }
  };

  const handleUpdateRepo = async (skipCheck = false) => {
    if (!selectedBranch) return;

    if (!skipCheck && !installDrive) {
      setShowDriveModal(true);
      return;
    }

    setIsUpdating(true);
    setUpdateProgress(10); // Start progress

    try {
      if (isElectron && window.electronAPI) {
        // Real Git Operation
        addLog(`Switching to branch: ${selectedBranch.name}...`, 'info');
        const result = await window.electronAPI.checkoutBranch(selectedBranch.name);

        if (result.success) {
          setUpdateProgress(100);
          addLog(`Successfully updated to ${selectedBranch.name}`, 'success');
          setTimeout(() => {
            setIsUpdating(false);
            setIsReadyToInstall(true);
            setCurrentView(AppView.INSTALL);
          }, 800);
        } else {
          setUpdateProgress(0);
          addLog(`Update failed: ${result.error}`, 'error');
          setIsUpdating(false);
          alert(`Update failed: ${result.error}`);
        }
      } else {
        // Simulation for Web Demo
        let progress = 0;
        const interval = setInterval(() => {
          progress += Math.floor(Math.random() * 10) + 5;
          if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            setTimeout(() => {
              setIsUpdating(false);
              setIsReadyToInstall(true);
              setCurrentView(AppView.INSTALL);
            }, 800);
          }
          setUpdateProgress(progress);
        }, 150);
      }
    } catch (e) {
      console.error(e);
      setIsUpdating(false);
    }
  };

  const handleRunInstallScript = useCallback(async () => {
    setIsInstalling(true);
    setLogs([]);
    const driveLetter = installDrive || 'C';

    if (isElectron && window.electronAPI) {
      // Real Python Script Execution via Electron
      try {
        const result = await window.electronAPI.runInstaller(driveLetter);
        setIsInstalling(false);
        if (result.success) {
          setInstallComplete(true);
        }
      } catch (err) {
        addLog("Failed to run installer script", 'error');
        setIsInstalling(false);
      }
    } else {
      // Simulation for Web Demo (Keep existing logic)
      simulateInstall(driveLetter);
    }
  }, [installDrive, isElectron, addLog]);

  const handleLaunchGame = async () => {
    const driveLetter = installDrive || 'C';
    if (isElectron && window.electronAPI) {
      try {
        const result = await window.electronAPI.launchGame(driveLetter);
        if (!result.success) {
          alert(result.error);
        }
      } catch (err) {
        console.error("Failed to launch game:", err);
        alert("Failed to launch game. Check console for details.");
      }
    } else {
      alert(`(Simulation) Launching game from: ${driveLetter}:\\Program Files (x86)\\Steam\\steamapps\\common\\Sid Meier's Civilization IV Beyond the Sword\\Beyond the Sword\\Civ4BeyondSword.exe`);
    }
  };

  const simulateInstall = (driveLetter: string) => {
    const fullPath = `${driveLetter}${PATH_SUFFIX}`;
    const steps = [
      { msg: `> python install_for_gui.py ${driveLetter} (SIMULATION)`, type: 'info', delay: 100 },
      { msg: HARRISON_MOD_BANNER, type: 'info', delay: 300 },
      { msg: "You are installing HarrisonMod version 1.0, please wait...", type: 'info', delay: 800 },
      { msg: `Scanning drive ${driveLetter}:\\ for assets...`, type: 'info', delay: 2000 },
      { msg: `Civ 4 BTS Assets Directory found!`, type: 'success', delay: 3600 },
      { msg: fullPath, type: 'info', delay: 3800 },
      { msg: `Installing HarrisonMod to ${fullPath}`, type: 'info', delay: 5500 },
      { msg: `Installing: Assets/XML/Civilizations/Civ4CivilizationInfos.xml`, type: 'info', delay: 6000 },
      { msg: `... (Copying files)`, type: 'info', delay: 7500 },
      { msg: `Finished installing HarrisonMod version 1.0!`, type: 'success', delay: 9000 },
    ];

    let currentStep = 0;
    const runStep = () => {
      if (currentStep >= steps.length) {
        setIsInstalling(false);
        setInstallComplete(true);
        return;
      }
      const step = steps[currentStep];
      addLog(step.msg, (step.type as any) || 'info');
      currentStep++;
      if (currentStep < steps.length) {
        setTimeout(runStep, steps[currentStep].delay - step.delay);
      } else {
        setTimeout(runStep, 100);
      }
    };
    runStep();
  };

  const resetState = () => {
    setCurrentView(AppView.MENU);
    setUpdateProgress(0);
    setIsUpdating(false);
    setIsReadyToInstall(false);
    setIsInstalling(false);
    setInstallComplete(false);
    setLogs([]);
  };

  // --- Render Methods (unchanged mostly) ---

  const renderMenu = () => (
    <div className="flex flex-col gap-4 w-full max-w-md animate-in fade-in zoom-in duration-300">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-amber-200 bg-clip-text text-transparent">DowagerMod</h1>
        <p className="text-slate-400 mt-2">Launcher & Installer for Civ IV: BTS</p>
        {!isElectron && (
          <div className="mt-2 bg-yellow-900/30 text-yellow-500 text-xs px-2 py-1 rounded border border-yellow-800 inline-block">
            Web Demo Mode (Simulation)
          </div>
        )}
      </div>

      <Button
        variant="primary"
        fullWidth
        icon={<MonitorPlay size={20} />}
        onClick={handleLaunchGame}
      >
        Launch Mod
      </Button>

      <Button
        variant="secondary"
        fullWidth
        icon={<DownloadCloud size={20} />}
        onClick={() => setCurrentView(AppView.UPDATES)}
      >
        Check for Updates
      </Button>

      <Button
        variant="secondary"
        fullWidth
        icon={<Settings size={20} />}
        onClick={() => setCurrentView(AppView.SETTINGS)}
      >
        Settings
      </Button>

      <div className="mt-8 text-center text-xs text-slate-600">
        v1.0 • {isElectron ? 'Desktop App' : 'Web Browser'}
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="w-full max-w-2xl flex flex-col gap-6 animate-in slide-in-from-right duration-300">
      <div className="flex items-center gap-4 border-b border-slate-700 pb-4">
        <button
          onClick={() => setCurrentView(AppView.MENU)}
          className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-white">Settings</h2>
          <p className="text-slate-400 text-sm">Configure installer preferences.</p>
        </div>
      </div>

      <div className="bg-slate-800/30 p-6 rounded-xl border border-slate-700/50 space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Game Install Drive</label>
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-700 text-xl font-bold font-mono text-blue-400 w-16 text-center">
              {installDrive || '?'}
            </div>
            <Button variant="secondary" onClick={() => setShowDriveModal(true)}>
              Change Drive
            </Button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUpdates = () => (
    <div className="w-full max-w-4xl flex flex-col gap-6 animate-in slide-in-from-right duration-300 h-[600px]">
      <div className="flex items-center gap-4 border-b border-slate-700 pb-4 shrink-0">
        <button
          onClick={resetState}
          className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white"
        >
          <ArrowLeft size={24} />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-white">Update Manager</h2>
          <p className="text-slate-400 text-sm">Select a branch to update your local files.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full overflow-hidden">
        <div className="flex flex-col gap-2 h-full overflow-hidden">
          <BranchList
            branches={branches}
            selectedBranch={selectedBranch}
            onSelect={setSelectedBranch}
            isLoading={isLoadingBranches}
          />
        </div>

        <div className="flex flex-col h-full bg-slate-800/30 p-6 rounded-xl border border-slate-700/50">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-4">Update Summary</h3>
            {selectedBranch ? (
              <div className="space-y-6">
                <div className="bg-slate-900 p-4 rounded border border-slate-700">
                  <span className="text-xs text-slate-500 uppercase font-bold block mb-1">Target Branch</span>
                  <div className="text-blue-400 font-mono text-xl">{selectedBranch.name}</div>
                </div>

                <div className="bg-slate-900/50 p-4 rounded border border-slate-800">
                  <span className="text-xs text-slate-500 uppercase font-bold block mb-2">Operation</span>
                  <ul className="text-sm text-slate-300 space-y-2 list-disc list-inside">
                    <li>Switch local repo to <span className="font-mono text-blue-300">{selectedBranch.name}</span></li>
                    <li>Pull latest commits from remote</li>
                  </ul>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 italic">
                Select a branch to view details...
              </div>
            )}
          </div>

          <div className="mt-8 shrink-0">
            {isUpdating ? (
              <div className="space-y-2">
                <div className="flex justify-between text-xs text-slate-300">
                  <span>Running Git Commands...</span>
                  <span>{updateProgress}%</span>
                </div>
                <div className="h-2 w-full bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-200"
                    style={{ width: `${updateProgress}%` }}
                  ></div>
                </div>
              </div>
            ) : (
              <Button
                fullWidth
                disabled={!selectedBranch}
                onClick={() => handleUpdateRepo(false)}
                icon={<DownloadCloud size={18} />}
              >
                Update Local Files
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderInstall = () => (
    <div className="w-full max-w-3xl flex flex-col gap-6 animate-in slide-in-from-right duration-300">
      <div className="flex items-center gap-4 border-b border-slate-700 pb-4">
        {(!isInstalling && !installComplete) && (
          <button
            onClick={() => setCurrentView(AppView.UPDATES)}
            className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-white"
          >
            <ArrowLeft size={24} />
          </button>
        )}
        <div>
          <h2 className="text-2xl font-bold text-white">Installation</h2>
          <p className="text-slate-400 text-sm">Executing python installer script.</p>
        </div>
      </div>

      <div className="bg-slate-800/30 p-6 rounded-xl border border-slate-700/50">
        {!installComplete ? (
          <div className="space-y-6">
            <div className="flex items-start gap-4 p-4 bg-blue-900/20 border border-blue-800/50 rounded-lg">
              <TerminalIcon className="text-blue-400 shrink-0 mt-1" size={24} />
              <div>
                <h4 className="font-semibold text-blue-100">Ready to Install</h4>
                <p className="text-sm text-blue-300/80 mt-1">
                  Branch <span className="font-mono bg-blue-900 px-1 rounded">{selectedBranch?.name}</span> is up to date.
                  Click below to run the installation script.
                </p>
              </div>
            </div>

            <Terminal logs={logs} title={`python install_for_gui.py ${installDrive || 'C'}`} />

            <div className="flex justify-end">
              {!isInstalling ? (
                <Button onClick={handleRunInstallScript} icon={<Play size={18} />}>
                  Install Now
                </Button>
              ) : (
                <Button disabled variant="secondary" className="opacity-75 cursor-wait">
                  Running Script...
                </Button>
              )}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 space-y-6 animate-in zoom-in duration-300">
            <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center border-2 border-green-500">
              <CheckCircle size={40} className="text-green-500" />
            </div>
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-bold text-white">Installation Complete</h3>
              <p className="text-slate-400">HarrisonMod v1.0 has been successfully installed!</p>
            </div>
            <div className="flex gap-4 mt-4">
              <Button variant="secondary" onClick={resetState}>
                Return to Menu
              </Button>
              <Button onClick={handleLaunchGame} icon={<MonitorPlay size={18} />}>
                Launch Game
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen w-full bg-slate-950 text-slate-200 flex items-center justify-center p-6 relative font-sans selection:bg-blue-500/30">

      {currentView === AppView.MENU && renderMenu()}
      {currentView === AppView.UPDATES && renderUpdates()}
      {currentView === AppView.INSTALL && renderInstall()}
      {currentView === AppView.SETTINGS && renderSettings()}

      {/* Drive Selection Modal */}
      {showDriveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-slate-800 border border-slate-700 rounded-xl shadow-2xl p-6 w-full max-w-sm transform scale-100">
            <div className="flex items-center gap-3 mb-4 text-white">
              <HardDrive size={24} className="text-blue-400" />
              <h3 className="text-xl font-bold">Select Game Drive</h3>
            </div>
            <p className="text-slate-300 text-sm mb-6">
              Please select the drive where <strong className="text-white">Civilization IV Beyond the Sword</strong> is installed.
            </p>

            <div className="space-y-6">
              <div className="flex justify-center gap-4">
                {['C', 'D', 'E', 'F'].map(drive => (
                  <button
                    key={drive}
                    onClick={() => setTempDrive(drive)}
                    className={`w-12 h-12 rounded-lg border-2 font-mono font-bold text-lg transition-all flex items-center justify-center
                      ${tempDrive === drive
                        ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-900/50 scale-110'
                        : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500 hover:text-white'
                      }`}
                  >
                    {drive}
                  </button>
                ))}
              </div>

              <div className="text-sm text-slate-400 text-center bg-slate-900/50 p-3 rounded border border-slate-800">
                Target: <span className="text-blue-400 font-mono font-bold">{tempDrive}:\</span>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="secondary"
                  fullWidth
                  onClick={() => setShowDriveModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  fullWidth
                  onClick={handleDriveSelection}
                >
                  Confirm & Continue
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;