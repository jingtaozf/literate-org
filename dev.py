import marimo

__generated_with = "0.8.7"
app = marimo.App(app_title="Literate Python Development notebook")


@app.cell
def __():
    import marimo as mo
    import os
    import sys
    sys.path
    mo.md('# Prepareation\n ## setup marimo')
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
    return


if __name__ == "__main__":
    app.run()
