import importlib
import os
import sys
import time
import json
from flask import Flask, request, jsonify

import traceback

# To convert lisp ratio to python
import fractions
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from io import StringIO
from io import StringIO

import logging

logger = logging.getLogger(__name__)
app = Flask(__name__)

def process_a_message (message):
    stdout_stream = StringIO();
    stderr_stream = StringIO();
    error = None
    result = None
    with redirect_stdout(stdout_stream):
        with redirect_stderr(stderr_stream):
            try:
                type = message['type']
                code = message['code']
                dict = globals()
                module_name = message['module'] if 'module' in message else None 
                if module_name:
                    if module_name not in sys.modules:
                        module_create_method = message['module-create-method'] if 'module-create-method' in message else "import"
                        match module_create_method:
                            case "create":
                                spec_module = importlib.util.spec_from_loader(module_name, loader=None)
                                module = importlib.util.module_from_spec(spec_module)
                                sys.modules[module_name] = module
                                dict = module.__dict__
                            case "import":
                                importlib.import_module(module_name)
                                dict = sys.modules[module_name].__dict__
                            case "import_or_create":
                                if importlib.util.find_spec(module_name):
                                    importlib.import_module(module_name)
                                    dict = sys.modules[module_name].__dict__
                                else:
                                    spec_module = importlib.util.spec_from_loader(module_name, loader=None)
                                    module = importlib.util.module_from_spec(spec_module)
                                    sys.modules[module_name] = module
                                    dict = module.__dict__
                            case _:
                                msg = f"Module {module_create_method} doesn't exist"
                                raise ValueError(msg)
                    else:
                        dict = sys.modules[module_name].__dict__
                        
                if error is None:
                    if type == "eval":
                        result = eval(code, dict)
                    elif type == "exec":
                        result = exec(compile(code, 'code', 'exec'), dict)
                        logger.debug("Executed code: %s,result:%s", code, result)
                    elif type == "status":
                        result = {'alive': True}
                    elif type == "quit":
                        result = None
                    else:
                        error = "Unknown type: {}".format(type)
                        raise ValueError(error)
            except Exception as e:
                # printing stack trace
                traceback.print_exc()
                error = str(e)
    if error is None:
        return_value = {'result':result, 'type':'result', 'stdout':stdout_stream.getvalue(), 'stderr':stderr_stream.getvalue()}
    else:
        return_value = {'error':error, 'type':'error', 'stdout':stdout_stream.getvalue(), 'stderr':stderr_stream.getvalue()}

    if type == "quit":
        sys.exit(0)
    else:
        return return_value
        
@app.route('/execute', methods=['POST'])
def execute():
    # Get JSON data
    data = request.get_json()

    # Process the data (example)
    logger.debug("/execute Received:%s", data)
    return_value = process_a_message(data)

    # Return a response
    logger.debug("/execute Returning:%s", return_value)
    return jsonify(return_value)

def run_server():
    host = '127.0.0.1'
    port = 7330
    if 'LITERATE_PYTHON_HOST' in os.environ:
        host = os.environ['LITERATE_PYTHON_HOST']
    if 'LITERATE_PYTHON_PORT' in os.environ:
        port = int(os.environ['LITERATE_PYTHON_PORT'])
    app.run(debug=True, port=port, host=host, use_reloader=False)
