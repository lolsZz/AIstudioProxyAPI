# AI Studio Proxy Server (Python/Camoufox Version)

**⚠️ Important notice: No longer necessary to manually install and trust root certificates**

Version 3.2.4 and later have eliminated the need for manual installation and trust of root certificates. The certificate configuration process has been optimized and no longer relies on the system certificate manager; instead, certificate errors are directly ignored in the browser.

**This is the currently maintained Python version. For the deprecated JavaScript version, please refer to [`deprecated_javascript_version/README.md`](deprecated_javascript_version/README.md).**

## Table of Contents

- [Project Overview](#project-overview)
- [How it works](#how-it-works)
- [Project Structure Description](#project-structure-description)
  - [Module responsibilities](#module-responsibilities)
- [Disclaimer](#disclaimer)
- [Core Features (Python Version)](#core-features-python-version)
- [Important notes (Python version)](#important-notes-python-version)
- [Project workflow diagram](#project-workflow-diagram)
- [Tutorial](#tutorial)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [First run and authentication](#first-run-and-authentication)
  - [Daily operation](#daily-operation)
  - [API usage](#api-usage)
  - [Web UI (service testing)](#web-ui-service-testing)
  - [Configure the client (using Open WebUI as an example)](#configure-the-client-using-open-webui-as-an-example)
- [Docker Deployment](#docker-deployment)
- [Multi-platform Guide (Python version)](#multi-platform-guide-python-version)
- [Troubleshooting (Python version)](#troubleshooting-python-version)
  - [Streaming proxy service: how it works](#streaming-proxy-service-how-it-works)
- [About Camoufox](#about-camoufox)
- [About fetch_camoufox_data.py](#about-fetch_camoufox_datapy)
- [Control Log Output (Python Version)](#control-log-output-python-version)

## Project Overview

This is a proxy server based on Python + FastAPI + Playwright + Camoufox, which aims to indirectly access the Google AI Studio web version by simulating the OpenAI API.

The project adopts a modular architecture design with clear separation of responsibilities:

- **FastAPI**: Provides high-performance API interfaces compatible with OpenAI standards, which now supports model parameter passing and dynamic model switching.
- **Playwright**: A powerful browser automation library for interacting with AI Studio pages.
- **Camoufox**: A modified and optimised Firefox browser focused on fingerprint detection and robot detection. It disguises browser fingerprints through underlying modifications rather than JS injection, aiming to simulate real user traffic and improve the stealth and success rate of automated operations.
- **Request queue**: Ensures requests are processed in order to improve stability.
- **Modular design**: The project adopts a clear module separation, including independent modules for configuration management, API handling, browser operations, and logging systems.

Through this proxy, various clients that support the OpenAI API (such as Open WebUI, LobeChat, NextChat, etc.) can connect to and use Google AI Studio models.

## How it works

This project serves as an intelligent proxy layer with the core goal of allowing users to interact with Google AI Studio using the standard OpenAI API format. Its workflow and key components are as follows:

1. **API compatibility layer (modular architecture)**:
   - **Main server** ([`server.py`](server.py)): Coordinates all modules and manages global state and lifecycle.
   - **API Routing Module** ([`api_utils/routes.py`](api_utils/routes.py)): Handles all API endpoints, including `/v1/chat/completions`, `/v1/models`, `/health`, etc.
   - **Request processing module** ([`api_utils/request_processor.py`](api_utils/request_processor.py)): Responsible for request validation, processing, and response generation.
   - **Queue worker** ([`api_utils/queue_worker.py`](api_utils/queue_worker.py)): Manages the request queue and ensures that requests are processed in order.

2. **Browser automation module** ([`browser_utils/`](browser_utils/) and Playwright):
   - **Initialisation module** ([`browser_utils/initialisation.py`](browser_utils/initialisation.py)): Handles browser and page initialisation logic.
   - **Model management module** ([`browser_utils/model_management.py`](browser_utils/model_management.py)): Handles model switching and list retrieval.
   - **Operation module** ([`browser_utils/operations.py`](browser_utils/operations.py)): Handles page interaction, response retrieval, and other operations.

3. **Enhanced Browser (Camoufox)**:
   - [`launch_camoufox.py`](launch_camoufox.py) is responsible for launching and managing Camoufox instances.
   - Camoufox is a modified version of the Firefox browser that focuses on disguising browser fingerprints through underlying modifications, rather than relying on JavaScript injection.

4. **Integrated streaming proxy service** ([`stream/`](stream/) module):
   - **Main proxy service** ([`stream/main.py`](stream/main.py)): This is the recommended and more efficient response retrieval method for the project, which listens on port `3120` by default.
   - **Proxy server** ([`stream/proxy_server.py`](stream/proxy_server.py)): Implements HTTP proxy server functionality.
   - **Certificate Manager** ([`stream/cert_manager.py`](stream/cert_manager.py)): Manages SSL certificate generation and verification.

## Project Structure Description

The project adopts a modular architecture design, with the main directory structure as follows:

```
freegoogleapi/
├── server.py                    # Main server file, coordinates all modules
├── launch_camoufox.py          # Launcher script
├── gui_launcher.py             # Graphical user interface launcher
├── llm.py                      # Local LLM simulation service
├── requirements.txt            # Python dependency list
├── excluded_models.txt         # List of excluded models
├── index.html                  # Web UI main page
├── webui.css                   # Web UI styles
├── webui.js                    # Web UI scripts
├── config/                     # Configuration management module
│   ├── __init__.py
│   ├── settings.py            # Runtime settings configuration
│   ├── constants.py           # Project constant definitions
│   ├── selectors.py           # CSS selector management
│   └── timeouts.py            # Timeout configuration
├── models/                     # Data model module
│   ├── __init__.py
│   ├── chat.py                # Chat-related data structures
│   ├── exceptions.py          # Exception class definitions
│   └── logging.py             # Logging-related models
├── api_utils/                  # API processing module
│   ├── __init__.py
│   ├── app.py                 # FastAPI application creation
│   ├── routes.py              # API route handling
│   ├── request_processor.py   # Request processing logic
│   ├── queue_worker.py        # Queue worker
│   └── utils.py               # API utility functions
├── browser_utils/              # Browser operation module
│   ├── __init__.py
│   ├── initialisation.py      # Browser initialisation
│   ├── model_management.py    # Model management
│   └── operations.py          # Page operations
├── logging_utils/              # Logging system module
│   ├── __init__.py
│   └── setup.py               # Logging configuration
├── stream/                     # Stream proxy module
│   ├── __init__.py
│   ├── main.py                # Main proxy service
│   ├── proxy_server.py        # Proxy server
│   ├── proxy_connector.py     # Proxy connector
│   ├── interceptors.py        # Request interceptors
│   ├── cert_manager.py        # Certificate management
│   └── utils.py               # Utility functions
├── auth_profiles/              # Authentication file directory
│   ├── active/                # Currently used authentication files
│   └── saved/                 # Saved authentication files
├── certs/                      # SSL certificate directory
├── logs/                       # Log file directory
└── errors_py/                  # Error snapshot directory
```

### Module responsibilities

- **config/**: Unify project configuration management, including environment variables, constants, CSS selectors, timeout settings, etc.
- **models/**: Define data structures, exception classes, and log models used in the project
- **api_utils/**: Handles all API-related functions, including routing, request handling, queue management, etc.
- **browser_utils/**: Encapsulates all browser operations, including initialisation, model management, page interaction, etc.
- **logging_utils/**: Provides unified log configuration and management functions
- **stream/**: Implements high-performance streaming proxy services, including certificate management, request interception, etc.

## Disclaimer

By using this project, you acknowledge that you have read, understood, and agreed to all of the terms of this disclaimer.

This project interacts with the Google AI Studio web version through automated scripts (Playwright + Camoufox). This method of automated web access may violate the user agreement or terms of service (Terms of Service) of Google AI Studio or related Google services. Improper use of this project may result in your Google account being warned, restricted, temporarily or permanently banned, or other penalties. The project author and contributors are not responsible for any such consequences.

Since this project relies on the structure and front-end code of the Google AI Studio web page, Google may update or modify its web page at any time, which may cause this project to become inoperable, unstable, or contain unknown errors. The project author and contributors cannot guarantee the continued availability or stability of this project.

This project is not an official project or collaboration with Google or OpenAI. It is a completely independent third-party tool. The project author has no affiliation with Google or OpenAI.

This project is provided 'as is' without any express or implied warranties, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement. You understand and agree to assume all risks associated with using this project.

Under no circumstances shall the project authors or contributors be liable for any direct, indirect, incidental, special, punitive, or consequential damages arising out of the use or inability to use this project.

By using this project, you acknowledge that you have fully understood and accepted all the terms of this disclaimer. If you do not agree with any part of this statement, please immediately stop using this project.

## Core Features (Python Version)

- **OpenAI API Compatibility**: Provides the following endpoints: `/v1/chat/completions`, `/v1/models`, `/api/info`, `/health`, `/v1/queue`, `/v1/cancel/{req_id}` (default port `2048`).
- **Model switching**: The `model` field in API requests is now used to dynamically switch models on the AI Studio page.
- **Streaming/non-streaming responses**: Supports `stream=true` and `stream=false`.
- **Response retrieval priority**:
  1. **Integrated streaming proxy service (Stream Proxy Service)**: Enabled by default (listening on port `3120`)
  2. **External Helper Service (optional)**: If configured and available
  3. **Playwright Page Interaction (Fallback)**: If both of the above methods are unavailable
- **Request queue**: Uses `asyncio.Queue` to process requests sequentially for improved stability.
- **Camoufox integration**: Uses the `camoufox` library to launch a modified Firefox instance, utilising its anti-fingerprinting and anti-detection capabilities.
- **Multiple startup modes**:
  - **Debug mode (`--debug`)**: Start a browser with a user interface for initial authentication, debugging, and updating authentication files.
  - **Headless mode (`--headless`)**: Run in the background without a user interface. Requires a valid authentication file to be saved in advance.
  - **Virtual display headless mode (`--virtual-display`)**: Linux only, runs a headless browser using the Xvfb virtual display to enhance anti-fingerprinting detection.
- **Web UI**: Provides access to a modern chat interface based on `index.html` via the `/` path
- **Modular architecture design**: Clear separation of responsibilities across different modules
- **Graphical Interface Launcher (`gui_launcher.py`)**: Provides a Tkinter GUI to simplify the launch and management of services
- **Error snapshot**: Automatically saves screenshots and HTML in the `errors_py/` directory when an error occurs
- **Logging control**: Control the logging level and `print` output redirection behaviour via environment variables

## Important notes (Python version)

- **Unofficial project**: Depends on the AI Studio web interface, which may become invalid due to page updates.
- **Authentication files are critical**: Headless mode heavily relies on valid `.json` authentication files in `auth_profiles/active/`. Files may expire and need to be replaced.
- **CSS selector dependency**: Page interactions depend on the CSS selectors defined in [`config/selectors.py`](config/selectors.py). AI Studio page updates may cause these selectors to become invalid.
- **Stability**: Browser automation is inherently less stable than native APIs and may need to be restarted after running for a long time.
- **AI Studio limitations**: Cannot bypass AI Studio's own rate, content, and other restrictions.
- **Port numbers**: The default port for FastAPI service is `2048`. The default port for the integrated streaming proxy service is `3120`.

## Project workflow diagram

```mermaid
graph TD
    subgraph 'User Side'
        User['User']
    end

    subgraph 'Launch Methods'
        CLI_Launch['launch_camoufox.py (CLI)']
        GUI_Launch['gui_launcher.py (GUI)']
    end

    subgraph 'Core Services'
        ServerPY['server.py (FastAPI + Playwright)']
        StreamProxy['stream.py (Integrated Stream Proxy)']
        CamoufoxInstance['Camoufox Browser Instance']
    end

    subgraph 'External Dependencies & Services'
        AI_Studio['Target AI Service (e.g., Google AI Studio)']
        OptionalHelper['(Optional) External Helper Service']
    end

    subgraph 'API Clients'
        API_Client['API Client (e.g., Open WebUI, cURL)']
    end

    User --> CLI_Launch
    User --> GUI_Launch
    GUI_Launch --> CLI_Launch
    CLI_Launch --> ServerPY
    CLI_Launch --> StreamProxy
    ServerPY --> CamoufoxInstance
    ServerPY --> StreamProxy
    StreamProxy --> AI_Studio
    StreamProxy --> ServerPY
    ServerPY --> OptionalHelper
    OptionalHelper --> ServerPY
    ServerPY --> CamoufoxInstance
    CamoufoxInstance --> AI_Studio
    API_Client --> ServerPY
    ServerPY --> API_Client
```

## Tutorial

We recommend using [`gui_launcher.py`](gui_launcher.py) (graphical interface) or directly using [`launch_camoufox.py`](launch_camoufox.py) (command line) for daily operation.

### Prerequisites

- **Python**: 3.8 or higher (3.9+ recommended).
- **pip**: Python package manager.
- **(Optional but recommended) Git**: For cloning the repository.
- **Google AI Studio account**: With normal access and usage.
- **xvfb** (only required when using the `--virtual-display` mode on Linux): X virtual frame buffer.

### Installation

1. **Clone the repository**:

```bash
git clone https://github.com/CJackHwang/AIstudioProxyAPI
cd AIstudioProxyAPI
```

2. **(Recommended) Create and activate a virtual environment**:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\\Scripts\\activate  # Windows
```

3. **Install Camoufox and dependencies**:

```bash
# Install the Camoufox library (recommended to include geoip data, especially when using a proxy)
pip install -U camoufox[geoip]
# Install other Python libraries required for the project
pip install -r requirements.txt
```

4. **Download Camoufox browser**:

```bash
# Camoufox needs to download its modified version of Firefox
camoufox fetch
```

5. **Install Playwright browser dependencies (if needed)**:

```bash
# Ensure that the Playwright library can find the necessary system dependencies
playwright install-deps firefox
```

### First run and authentication

To avoid manually logging into AI Studio each time you start, you need to run once in [`launch_camoufox.py --debug`](launch_camoufox.py) mode or [`gui_launcher.py`](gui_launcher.py) head mode to generate the authentication file.

1. **Run Debug mode via the command line**:

```bash
python launch_camoufox.py --debug --server-port 2048 --stream-port 3120 --helper "" --internal-camoufox-proxy ""
```

2. **Complete Google login** in the pop-up browser window until you see the AI Studio chat interface.

3. **Save the authentication** when prompted and move the newly generated `.json` file from `auth_profiles/saved/` to the `auth_profiles/active/` directory.

**Important**: Authentication files will expire! When headless mode fails to start and reports an authentication error, you need to delete the old file in the `active` directory and re-execute the debug mode steps to generate new authentication files.

### Daily operation

After completing the initial authentication setup, it is recommended to use the headless mode:

```bash
python launch_camoufox.py --headless --server-port 2048 --stream-port 3120 --helper "" --internal-camoufox-proxy ""
```

### API usage

The proxy server listens on `http://127.0.0.1:2048` by default.

- **Chat interface**: [`POST /v1/chat/completions`](api_utils/routes.py)
- **Model list**: [`GET /v1/models`](api_utils/routes.py)
- **API Information**: [`GET /api/info`](api_utils/routes.py)
- **Health check**: [`GET /health`](api_utils/routes.py)

Example request:

```bash
curl -X POST http://127.0.0.1:2048/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gemini-1.5-pro-latest",
    "messages": [
      {"role": "system", "content": "Be concise."},
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "stream": false,
    "temperature": 0.7,
    "max_output_tokens": 150,
    "top_p": 0.9
  }'
```

### Web UI (service testing)

This project provides a simple web user interface (`index.html`) for quickly testing the basic functions of the proxy and viewing its status.

- **Access**: Open the root address of the server in your browser, which is `http://127.0.0.1:2048/` by default.
- **Features**:
  - **Chat Interface**: A basic chat window where you can send messages and receive replies from AI Studio
  - **Server Information**: View API call information and detailed status of the service health check
  - **Model Settings**: Configure and save model parameters to local browser storage
  - **System Log**: Real-time backend logs via WebSocket
  - **Theme Switching**: Light/dark theme switching with local storage

### Configure the client (using Open WebUI as an example)

1. Open Open WebUI.
2. Go to 'Settings' -> 'Connection'.
3. In the "Model" section, click 'Add Model'.
4. **Model Name**: Enter the name you want, for example `aistudio-gemini-py`.
5. **API Base URL**: Enter the proxy server address, e.g., `http://127.0.0.1:2048/v1`.
6. **API Key**: Leave blank or enter any characters (the server does not verify this).
7. Save the settings.

## Docker Deployment

This project supports deployment via Docker. For detailed build and run instructions, please refer to:

- [Docker Deployment Guide (README-Docker.md)](README-Docker.md)

Please note that the first run to obtain the authentication file cannot be completed in the Docker environment. It must be completed on the host first.

## Multi-platform Guide (Python version)

### macOS / Linux

- The installation process is usually smooth. Ensure that Python and pip are correctly installed and configured in the system PATH.
- Activate the virtual environment using `source venv/bin/activate`.
- `playwright install-deps firefox` may require the system package manager to install some dependencies.
- For Linux users, consider starting with the `--virtual-display` flag (requires `xvfb` to be installed beforehand).

### Windows

#### Native Windows

- Ensure that the 'Add Python to PATH' option is selected when installing Python.
- Activate the virtual environment using `venv\\Scripts\\activate`.
- The Windows firewall may block Uvicorn/FastAPI from listening on the port.
- We recommend using [`gui_launcher.py`](gui_launcher.py) to start, as it automatically handles background processes and user interaction.

#### WSL (Windows Subsystem for Linux)

- For users who are accustomed to the Linux environment, WSL (especially WSL2) provides a better experience.
- In the WSL environment, follow the steps for macOS / Linux to install and handle dependencies.
- All commands should be executed within the WSL terminal.

## Troubleshooting (Python version)

### Common Issues

- **`pip install camoufox[geoip]` failed**: This may be due to network issues or a missing compilation environment. Try installing without `[geoip]`.
- **`camoufox fetch` failed**: Common causes are network issues or SSL certificate verification failure. You can try running the [`fetch_camoufox_data.py`](fetch_camoufox_data.py) script.
- **`playwright install-deps` failed**: This is usually caused by missing libraries on Linux systems. Read the error message carefully and install the missing system packages.
- **Authentication failed (especially in headless mode)**: The `.json` file under `auth_profiles/active/` has expired or is invalid. Delete the files under `active` and re-run debug mode.
- **Port conflict**: Use system tools to find and terminate the process occupying the port, or modify the port parameters.

### Model parameter settings not taking effect

This may be because `isAdvancedOpen` in `localStorage` on the AI Studio page is not set to `true` correctly, or `areToolsOpen` is interfering with the parameter panel. The proxy service attempts to automatically correct these `localStorage` settings and reload the page when it starts.

### Streaming proxy service: how it works

#### Features

- Creates an HTTP proxy server (default port: 3120)
- Intercepts HTTPS requests to Google domains (can also be configured)
- Dynamically generates server certificates using a self-signed CA certificate
- Parses AIStudio responses into OpenAI-compatible format

#### Certificate Generation

The project includes pre-generated CA certificates and keys. If you need to regenerate them, use the following commands:

```bash
openssl genrsa -out certs/ca.key 2048
openssl req -new -x509 -days 3650 -key certs/ca.key -out certs/ca.crt -subj '/C=CN/ST=Shanghai/L=Shanghai/O=AiStudioProxyHelper/OU=CA/CN=AiStudioProxyHelper CA/emailAddress=ca@example.com'
openssl rsa -in certs/ca.key -out certs/ca.key
```

## About Camoufox

This project uses [Camoufox](https://camoufox.com/) to provide browser instances with enhanced anti-fingerprinting capabilities.

- **Core objective**: Simulate real user traffic to avoid being identified as an automated script or bot by websites.
- **Implementation Method**: Camoufox is based on Firefox and modifies the underlying C++ implementation of the browser to spoof device fingerprints rather than using JavaScript injection.
- **Playwright Compatibility**: Camoufox provides an interface compatible with Playwright.

The primary purpose of using Camoufox is to improve stealth when interacting with the AI Studio web page, reducing the likelihood of detection or restriction.

## About fetch_camoufox_data.py

The project root directory contains a helper script named [`fetch_camoufox_data.py`](fetch_camoufox_data.py).

- **Purpose**: This script attempts to disable SSL certificate verification and force download the browser files and data required by Camoufox when the `camoufox fetch` command fails.
- **Risk**: Disabling SSL verification poses a security risk! Please only run this script if you fully understand the risks and are certain that your network environment is trustworthy.
- **Usage**: If `camoufox fetch` fails, try running `python fetch_camoufox_data.py` in the project root directory.

## Control Log Output (Python Version)

You can control the level of detail and behaviour of logs in several ways:

1. **Main server logs**: The main server has its own independent logging system, which is recorded in `logs/app.log` and controlled by environment variables:
   - **`SERVER_LOG_LEVEL`**: Controls the level of the main logger (default is `INFO`)
   - **`SERVER_REDIRECT_PRINT`**: Controls the behaviour of `print()` and `input()` inside the server
   - **`DEBUG_LOGS_ENABLED`**: Controls whether detailed debug log points are enabled
   - **`TRACE_LOGS_ENABLED`**: Controls whether deeper tracing logs are enabled

2. **Environment variable examples**:

```bash
# Linux/macOS
export SERVER_LOG_LEVEL=DEBUG
python launch_camoufox.py

# Windows (PowerShell)
$env:SERVER_LOG_LEVEL='DEBUG'
python launch_camoufox.py
```

3. **Log files**:
   - `logs/app.log`: Detailed logs of the FastAPI server
   - `logs/launch_app.log`: Logs of the launcher

4. **Web UI Logs**: The right sidebar of the Web UI displays real-time logs from the server via WebSocket.