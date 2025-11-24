export interface GitHubBranch {
  name: string;
  commit: {
    sha: string;
    url: string;
  };
  protected: boolean;
  lastUpdated?: string;
}

export enum AppView {
  MENU = 'MENU',
  UPDATES = 'UPDATES',
  INSTALL = 'INSTALL',
  SETTINGS = 'SETTINGS'
}

export interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export const REPO_OWNER = 'siegelh';
export const REPO_NAME = 'DowagerMod';

// Electron API Definition
export interface ElectronAPI {
  runInstaller: (driveLetter: string) => Promise<{ success: boolean; error?: string }>;
  checkoutBranch: (branchName: string) => Promise<{ success: boolean; error?: string; output?: string }>;
  launchGame: (driveLetter: string) => Promise<{ success: boolean; error?: string }>;
  onInstallerLog: (callback: (log: { message: string; type: string }) => void) => () => void;
}

// Extend global Window interface
declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}