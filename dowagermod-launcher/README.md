# DowagerMod Installer

A desktop installer application for Civilization 4 Beyond the Sword mod.

## Prerequisites

1.  **Node.js**: Install from [nodejs.org](https://nodejs.org/).
2.  **Python**: Install Python and ensure it is added to your PATH.
3.  **Git**: Ensure Git is installed and in your PATH.

## Setup

1.  Open a terminal in this folder.
2.  Install dependencies:
    ```bash
    npm install
    ```

## Development (Run locally)

To run the app in development mode with live reloading:

```bash
npm run electron:dev
```

## Build (Create .exe)

To build the standalone Windows installer:

```bash
npm run electron:build
```

The output file (DowagerMod Installer Setup.exe) will be in the `release` folder.
