import marimo

__generated_with = "0.8.7"
app = marimo.App(app_title="Literate Python Development notebook")


@app.cell
def __():
    import marimo as mo
    import os
    import sys

    mo.md('# Prepareation\n ## setup marimo & logger \n')
    return mo, os, sys


@app.cell
def __(mo, os):
    mo.md('## Prepare a server for literate python')
    from lpy.server import run_server as run_lpy_server
    from threading import Thread
    os.environ['LITERATE_PYTHON_HOST'] = '127.0.0.1'
    os.environ['LITERATE_PYTHON_PORT'] = '7332'
    lpy_server_thread = Thread(target=run_lpy_server)
    lpy_server_thread.start()
    return Thread, lpy_server_thread, run_lpy_server


@app.cell
def __():
    from lpy.loader import inMemoryModules
    inMemoryModules['example3'] = {'content': '''
    def hello():
        print("Hello from the in-memory module!")
    '''}
    inMemoryModules
    return inMemoryModules,


@app.cell
def __():
    import importlib
    from lpy.loader import register_literate_module_finder

    register_literate_module_finder()
    return importlib, register_literate_module_finder


@app.cell
def __():
    import example3
    return example3,


@app.cell
def __(example3):
    example3
    return


@app.cell
def __(inMemoryModules):
    inMemoryModules['example4.__init__'] = {'content': "\n"}
    inMemoryModules['example4.test'] = {'content': "\ndef hello():\n    print(\"Hello from the in-memory module!\")\n"}
    return


@app.cell
def __(sys):
    sys.meta_path
    return


@app.cell
def __():
    print('abc')
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
