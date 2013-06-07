"""Component-factory that looks for the component configuration in an 
accessible module.
"""

import importlib

import components, component_interfaces

from logging import getLogger
logging = getLogger(__name__)

def set_cb(resolver):
    """Receives a function that with parameters (registry, ns, key=None).
    """

    global _resolver

    _resolver = resolver

def _get_cb():
    return _resolver

def load_class(full_class_name):
    """We expect a class-name completely qualified with any module names. We
    were calling this in the 'utility' module, but it got caught-up in a 
    bidirectiional loading error.
    """

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


_cache = { }

def get(name):
    global _cache

    if name in _cache:
        return _cache[name]

    logging.debug("Manufacturing component [%s]." % (name))

    try:
# TODO: Finish implementing this.
        requires = component_interfaces.get(name)
    except:
        logging.exception("Could not find interface requirement for [%s]." % (name))
        raise

    try:
        config = getattr(components, name)
    except:
        logging.exception("Could not find component with name [%s]." % 
                          (name))
        raise LookupError(name)

    if '_binding' not in config:
        message = ("No '_binding' is defined for component [%s]." % (name))
        
        logging.error(message)
        raise Exception(message)

    try:
        cls = load_class(config['_binding'])
    except:
        logging.exception("Could not resolve class entity for component "
                          "with name [%s]." % (name))
        raise

    del config['_binding']

    # We were asked to get argument values from one or more config registries.
    # This is useful, for example, if you have database credentials in a JSON 
    # file and the rest of the configurations in the DB. This will pass the 
    # values from the JSON file into the component config of the DB.
    if '_config_from' in config:
        collected = {}
    
        for ref_tuple in config['_config_from']:
            resolver = _get_cb()

            if resolver is None:
                raise Exception("Resolver is not defined. _config_from can't "
                                "be handled for component [%s]." % (name))

            registry_values = resolver(ref_tuple)
            collected.update(registry_values)

        collected.update(config)
        config = collected
        del config['_config_from']

    try:
        obj = cls(**config)
    except:
        logging.exception("Could not instantiate component [%s]." % (name))
        raise

    _cache[name] = obj

    return obj

