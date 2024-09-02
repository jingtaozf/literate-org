import sys
import types
import importlib
import importlib.abc
import importlib.machinery
import logging

logger = logging.getLogger(__name__)

if "inMemoryModules" not in globals():
    inMemoryModules = {}

def _get_module_spec(fullname: str) -> bool:
    return inMemoryModules.get(fullname) or inMemoryModules.get(fullname + ".__init__")

class LiterateImporter(object):
    def find_module(self, fullname: str, path=None):
        if _get_module_spec(fullname):
            logger.debug(f"Found literate module {fullname}")
            return self
        else:
            return None

    def load_module(self, fullname: str):
        """Create a new module object."""
        mod_spec = _get_module_spec(fullname)
        mod = types.ModuleType(fullname)
        mod.__loader__ = self
        mod.__file__ = mod_spec.get("filepath", "")
        # Set module path - get filepath and keep only the path until filename
        mod.__path__ = ["/".join(mod.__file__.split("/")[:-1]) + "/"]
        mod.__package__ = fullname
        sys.modules[fullname] = mod
        # Execute the module/package code into the Module object
        logger.debug(f"Load literate module {fullname}")
        exec(mod_spec["content"], mod.__dict__)
        return mod

class LiterateModuleFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if _get_module_spec(fullname):
            logger.debug(f"Found literate module {fullname}")
            return importlib.machinery.ModuleSpec(fullname, LiterateImporter())
        return None

def register_literate_module_finder():
    sys.meta_path = [
        f for f in sys.meta_path if not isinstance(f, LiterateModuleFinder)
    ]
    print("Register literate importer.\n")
    sys.meta_path.append(LiterateModuleFinder())
