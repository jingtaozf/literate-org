# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a comprehensive literate programming system with two interconnected projects:

- **`literate_python`**: A Python package that enables importing Python modules from Org files. The project implements a custom module loader that allows developers to write Python code in Org files with proper documentation and structure, then import these modules directly into Python.

- **`literate_org`**: An Emacs Lisp package that enables bi-directional sync between Python files and a master Org file, converting a local directory/file layout of Python modules to related hierarchical Org sections. The module name is specified in the Org property `LITERATE_ORG_MODULE` and the Python file path is specified in the Org property `header-args` with keyword `tangle`.

## Master Org File Structure

The main source file is `literate-org.org`, which contains both Python and Emacs Lisp code using literate programming principles:

### Key Header Properties
- `#+PROPERTY: literate-lang python` - Sets default language for literate programming
- `#+PROPERTY: literate-load yes` - Enables automatic loading of literate modules
- `#+PROPERTY: LITERATE_ORG_EXPORT_DIRECTORY: ./literate_python` - Sets export directory
- `#+PROPERTY: header-args :results silent :session :tangle no` - Default code block settings

### Module Organization
- Each Org section corresponds to a Python module using the `LITERATE_ORG_MODULE` property
- Code blocks use `:tangle` property to specify output file paths
- Hierarchical structure maps directly to Python package layout
- Examples: `literate_python.loader`, `literate_python.server`, `literate_python.tests.test_server`

### Dual Language Support
- **Python code blocks**: Use `:tangle ./literate_python/filename.py` to generate source files
- **Emacs Lisp code blocks**: Use `:literate-lang: elisp` and typically `:tangle no`
- Both languages share the same document structure and can reference each other

## Key Architecture

### Core Components

- **`literate_python/loader.py`**: Custom module finder and loader implementing Python's import system hooks
- **`literate_python/server.py`**: Flask-based server providing HTTP endpoints for code execution and module registration
- **`literate_python/sections.py`**: Clustering utilities for organizing code sections using sentence transformers and scikit-learn
- **`literate_python/inspector.py`**: Code inspection utilities with multimethod dispatch for different Python object types

### Emacs Integration Layer
- **Minor mode `literate-org-mode`**: Provides hooks for auto-formatting and tangling on save
- **Xref backend**: Enables navigation between Org files and tangled source files
- **Server communication**: HTTP client for interacting with the Python server
- **Module execution**: Support for running Python code in specified module contexts

### Module System
- `LiterateModuleFinder` and `LiterateImporter` classes implement Python's import hooks
- Modules are registered in memory via `register_literate_modules()` using JSON data
- Dynamic module creation and execution in isolated namespaces
- Support for both `import` and `create` module methods

### Server Architecture
The Flask server runs on localhost:7330 by default and provides:
- `/lpy/register` - Register literate modules from Org files
- `/lpy/execute` - Execute Python code in specific module contexts with stdout/stderr capture
- `/lpy/status` - Health check endpoint

## Literate Programming Conventions

### Code Block Patterns
1. **Property-based Configuration**: Each section can override `literate-lang` property
2. **Hierarchical Structure**: Org heading levels organize code into logical modules
3. **Module-to-File Mapping**: Direct relationship between `LITERATE_ORG_MODULE` and file paths
4. **Header Arguments**: Consistent use of `:tangle`, `:results`, `:session` for behavior control

### Tangling Process
- Code blocks with `:tangle filename.py` generate source files
- Auto-formatting applied before tangling (Black for Python, Prettier for JS/TS)
- Hooks triggered on save to maintain sync between Org and source files
- Support for noweb references and code block composition

## Common Commands

### Development
```bash
# Start development server with marimo
make dev

# Run the literate Python server
make server
# or
env PYTHONPATH=$(PWD) poetry run python -m literate_python
```

### Build and Quality
```bash
# Build package
make build
# or
poetry build

# Run linting
make lint
# or
poetry run black .
poetry run flake8
```

### Publishing
```bash
# Publish to PyPI (requires token setup)
make publish
# or
poetry publish --build
```

### Testing
```bash
# Run tests
poetry run python -m pytest literate_python/tests/
```

## Environment Variables

- `LITERATE_PYTHON_HOST`: Server host (default: 127.0.0.1)
- `LITERATE_PYTHON_PORT`: Server port (default: 7330)

## Development Notes

### Org File Structure
- Python modules are organized as Org sections
- Module names defined via `LITERATE_PYTHON_MODULE_NAME` property
- Code blocks within sections define module functions and classes
- The system parses Org files using the `orgparse` library

### Key Dependencies
- `flask`: Web server framework for HTTP endpoints
- `orgparse`: Org file parsing and manipulation
- `sentence-transformers`: Semantic code clustering and analysis
- `scikit-learn`: Machine learning utilities for clustering
- `multimethod`: Multiple dispatch for object inspection

### Module Registration
Modules are registered via JSON data containing:
- `name`: Module name (e.g., "literate_python.loader")
- `content`: Python code content extracted from Org blocks
- `filepath`: Optional file path reference for debugging

## Advanced Features

### AI-Powered Code Analysis
- **Semantic Clustering**: Uses sentence transformers to group related code sections
- **Optimal Clustering**: Implements silhouette analysis to determine optimal number of clusters
- **Code Embedding**: Converts code definitions to vector embeddings for similarity analysis

### Emacs Integration
- **Navigation**: Xref backend for jumping between Org files and tangled source files
- **Auto-formatting**: Automatic code formatting on save (Black for Python, Prettier for JS/TS)
- **Live Execution**: Execute code blocks in specified module contexts via HTTP server
- **Module Awareness**: Track and display current module context in mode line

### Development Workflow
1. Edit code in `literate-org.org` using Org mode
2. Code blocks are automatically formatted and tangled on save
3. Python server provides live execution and module loading
4. Emacs integration enables seamless navigation and development
5. AI features help organize and analyze code structure

## Editing Python Code in Org File

### Primary Development Workflow
The main development workflow involves editing Python code directly in `literate-org.org` rather than in the generated Python files:

1. **Edit Python code in `literate-org.org`** using Org mode
2. **Run Emacs tangling commands** to generate Python files from code blocks
3. **Generated Python files** in `literate_python/` directory are auto-generated and should not be edited directly

### Locating Python Modules in Org File

To find and edit Python code for a specific module:

1. **Search for the module using `LITERATE_ORG_MODULE` property**:
   ```
   Use Grep tool to search for: ":LITERATE_ORG_MODULE: module_name"
   ```
   
2. **Module examples to search for**:
   - `literate_python.loader` - Module loader implementation
   - `literate_python.server` - Flask server implementation  
   - `literate_python.sections` - Code clustering utilities
   - `literate_python.inspector` - Code inspection utilities
   - `literate_python.__init__` - Package initialization
   - `literate_python.__main__` - Main module entry point
   - `literate_python.tests.test_server` - Server tests

3. **Once found, edit the code blocks following that section**

### Code Block Organization Patterns

Within each module section, Python code is organized into separate code blocks by logical grouping:

#### Top-Level Code Blocks
- **Imports block**: All `import` and `from` statements in a single code block
- **Variables block**: Top-level variables, constants, and global configurations
- **Functions**: Each function in its own separate code block
- **Classes**: Each class definition in its own separate code block

#### Example Structure
```org
** Module Name
:PROPERTIES:
:LITERATE_ORG_MODULE: literate_python.example
:header-args: :tangle ./literate_python/example.py
:END:

*** Import dependencies
#+BEGIN_SRC python
import sys
import os
from typing import List, Dict
#+END_SRC

*** Module-level variables
#+BEGIN_SRC python
DEFAULT_CONFIG = {"host": "localhost", "port": 8080}
CACHE_SIZE = 1000
#+END_SRC

*** Helper function
#+BEGIN_SRC python
def helper_function(param):
    """Helper function documentation."""
    return param.upper()
#+END_SRC

*** Main class
#+BEGIN_SRC python
class MainClass:
    """Main class documentation."""
    def __init__(self):
        self.config = DEFAULT_CONFIG
#+END_SRC
```

### Editing Guidelines

1. **Always locate the correct module section** using the `LITERATE_ORG_MODULE` property
2. **Identify the appropriate code block** based on what you're editing (imports, variables, functions, classes)
3. **Edit only the code block content**, not the surrounding Org markup
4. **Maintain code block separation** - don't combine different logical units
5. **Preserve the `:tangle` header arguments** that specify output file paths

### Common Module Locations

- **Core functionality**: Look for modules like `literate_python.loader`, `literate_python.server`
- **Utilities**: Check `literate_python.sections`, `literate_python.inspector`
- **Tests**: Find test modules under `literate_python.tests.*`
- **Package setup**: Look for `literate_python.__init__` and `literate_python.__main__`

### Important Notes

- **Do not edit generated Python files** in the `literate_python/` directory directly
- **All changes must be made in `literate-org.org`** 
- **The user will run tangling commands** to generate the actual Python files
- **Code blocks are automatically formatted** (Black for Python) when tangled

## Editing Emacs Lisp Code in Org File

### Primary Development Workflow for Emacs Lisp
Similar to Python, Emacs Lisp code is also edited directly in `literate-org.org` rather than in separate `.el` files:

1. **Edit Emacs Lisp code in `literate-org.org`** using Org mode
2. **All Emacs Lisp routines are stored in the master org file**
3. **No separate `.el` files are maintained** - everything is in the org file

### Locating Emacs Lisp Code in Org File

To find and edit Emacs Lisp code:

1. **Search for Emacs Lisp sections using language property**:
   ```
   Use Grep tool to search for: ":literate-lang: elisp"
   ```

2. **Look for Emacs Lisp code blocks**:
   ```
   Use Grep tool to search for: "#+BEGIN_SRC elisp"
   ```

3. **Common Emacs Lisp sections to look for**:
   - "A minor mode for literate org" - Core minor mode functionality
   - "Source Code Execution" - Code execution utilities
   - "Utilities" - Helper functions and utilities
   - "Emacs library for python literate server" - Server integration

### Emacs Lisp Code Organization Patterns

Within Emacs Lisp sections, code is organized by logical features and sub-features:

#### Feature-Based Organization
- **Main features**: Top-level org sections (e.g., "Source Code Execution")
- **Sub-features**: Sub-sections within main features (e.g., "execute source code in current code block")
- **Individual routines**: Each function, macro, or variable group in its own code block

#### Code Block Granularity
- **One routine per code block**: Each function or macro in its own separate code block
- **One variable group per code block**: Related variables grouped together
- **One feature per code block**: Small, focused functionality units

#### Example Structure
```org
** Source Code Execution
:PROPERTIES:
:literate-lang: elisp
:header-args: :results silent :session :tangle no
:END:

*** execute source code in current code block
#+BEGIN_SRC elisp
(defun literate-org-execute-current-code-block ()
  (interactive)
  (let* ((element (org-element-at-point))
         (info (second element)))
    ;; function implementation
    ))
#+END_SRC

*** customized variables for server host and port
#+BEGIN_SRC elisp
(defcustom literate-org-server-host "127.0.0.1"
  "Host for the literate server."
  :type 'string
  :group 'literate-org)

(defcustom literate-org-server-port 7330
  "Port for the literate server."
  :type 'integer
  :group 'literate-org)
#+END_SRC

*** helper function for server communication
#+BEGIN_SRC elisp
(defun literate-org-send-request (data)
  "Send request to literate server."
  (let ((url (format "http://%s:%d/lpy/execute" 
                     literate-org-server-host 
                     literate-org-server-port)))
    ;; implementation
    ))
#+END_SRC
```

### Editing Guidelines for Emacs Lisp

1. **Navigate by feature sections**: Use org headings to find the relevant feature area
2. **Look for sub-features**: Drill down to specific functionality using sub-sections
3. **Edit individual code blocks**: Each routine/macro/variable group is in its own block
4. **Maintain section hierarchy**: Preserve the org section structure that groups related functionality
5. **Preserve code block properties**: Keep `:literate-lang: elisp` and other header arguments

### Common Emacs Lisp Feature Areas

- **Minor Mode**: Core `literate-org-mode` functionality and keymaps
- **Code Execution**: Functions for executing Python code in modules
- **Server Communication**: HTTP client functions for talking to Python server
- **Xref Backend**: Navigation between org files and tangled files
- **Formatting**: Auto-formatting functions for code blocks
- **Utilities**: Helper functions for file operations, module management
- **Customization**: User-customizable variables and settings

### Emacs Lisp Code Block Properties

Most Emacs Lisp code blocks use these properties:
- `:literate-lang: elisp` - Specifies Emacs Lisp language
- `:results silent` - Suppresses output during evaluation
- `:session` - Uses persistent session for evaluation
- `:tangle no` - Prevents tangling to separate files (code stays in org file)

### Important Notes for Emacs Lisp

- **All Emacs Lisp code lives in `literate-org.org`** - no separate `.el` files
- **Code is organized by features and sub-features** using org sections
- **Each function/macro/variable group gets its own code block**
- **Search by feature name or function name** to locate specific code
- **Preserve the hierarchical section structure** when editing

## Testing
- Test files are organized within the literate structure
- Example: `literate_python.tests.test_server` section contains server tests
- Tests can be run using standard pytest: `poetry run python -m pytest literate_python/tests/`
- never use relative import in python code