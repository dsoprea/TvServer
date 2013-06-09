import importlib
import imp
import json
import inspect

from inspect import isclass, getmembers
from types import ListType
from os import listdir

from logging import getLogger
logging = getLogger(__name__)


def load_class(full_class_name):
    """We expect a class-name completely qualified with any module names."""

    last_dot = full_class_name.rfind('.')

    if last_dot == -1:
        message = ("We require at least two dot-separated components in the "
                   "class-name [%s]." % (full_class_name))

        logging.exception(message)
        raise Exception(message)
    
    module_name = full_class_name[:last_dot]
    class_name = full_class_name[last_dot + 1:]

    logging.debug("Loading class [%s] from module [%s]." % (class_name, 
                                                            module_name))

    try:
        module = importlib.import_module(module_name)
    except:
        logging.exception("Could not import module [%s]." % (module_name))
        raise

    try:
        return module.__dict__[class_name]
    except:
        logging.exception("Class [%s] does not exist in module [%s]." % 
                          (class_name, module_name))
        raise

def load_module(module_name, file_path):
    """We expect a module-name to store with, and the file-path to load from.
    """

    logging.debug("Loading module from file-path [%s]." % (file_path))

    try:
        module = imp.load_source(module_name, file_path)
    except:
        logging.exception("Could not import module [%s] from file-path "
                          "[%s]." % (module_name, file_path))
        raise

    return module

def filter_modules(modules_prefix, path, map_function=None):
    """Returns a list of class types. Map each through an optional function to
    determine what's chosen and returned.
    """

    logging.debug("Finding modules like [%s.*] in path [%s].  MAP= [%s]" % 
                  (modules_prefix, path, '<present>' if map_function 
                                                     else '<none>'))

    try:
        files = [ filename for filename 
                           in listdir(path) 
                           if filename[0:1] != '_' and 
                              filename[-3:] == '.py' ]
    except:
        logging.exception("Could not list path [%s]." % (path))
        raise

    logging.debug("Found (%d) candidate files." % (len(files)))

    results = []
    for module_filename in files:
        logging.debug("Module file [%s] discovered." % (module_filename))
    
        full_module_name = ('%s.%s' % (modules_prefix, module_filename[:-3]))
        file_path = ('%s/%s' % (path, module_filename))

        try:
            module = load_module(full_module_name, file_path)
        except:
            logging.exception("Could not load module from [%s]." % (file_path))
            continue

        # Append the module.
        if not map_function:
            results.append(module)

        # Call the map_function to determine what we'll actually remember.
        else:
            result = map_function(module)
            if result:
                # If we get a list back, append the individual elements.
                if issubclass(result.__class__, ListType):
                    for obj in result:
                        results.append(obj)

                # Else, append what we get back.
                else:
                    results.append(result)

    return results

def filter_modules_by_class(modules_prefix, path, class_type):
    """A helper function to look for classes of a specific type among the 
    modules in a given directory (non-recursively).
    """

    def map_function(module):
        logging.debug("Checking types of classes in module [%s]." % 
                      (module.__name__))
    
        classes = []
        for name, obj in getmembers(module):
            # If it inherits from the class but is not the class itself. This 
            # will happen when the latter is brought into scope to be inherited 
            # by the former.
            if isclass(obj) and issubclass(obj, class_type) and \
               obj != class_type:
                logging.debug("Class [%s] does inherit from [%s]." % 
                              (obj.__name__, class_type.__name__))
                classes.append(obj)
        
        return classes

    return filter_modules(modules_prefix, path, map_function)

def list_dictify(l, cb_key_translate=None):
    d = {}
    for val in l:
        key = cb_key_translate(val) if cb_key_translate else val
        d[key] = val
        
    return d

def get_pp_json(data):
    """Serialize the given data to JSON, pretty-like."""

    try:
        return json.dumps(data, indent=2) + "\n"
    except:
        logging.exception("Could not JSONize data.")
        raise

def get_backtrace():
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)

    return [(frame[1], frame[2], frame[3]) for frame in calframe[1:]]

def get_caller():
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)

    # Each frame looks like:
    #   (frame, filepath, lineno, method_name, context_string, index)

    # Return information on the invocation preceding the last.
    return calframe[2]

