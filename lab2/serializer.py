import dis
import inspect
import opcode
import types
import weakref

GLOBAL_OPS = (opcode.opmap['STORE_GLOBAL'],
              opcode.opmap['DELETE_GLOBAL'], opcode.opmap['LOAD_GLOBAL'])


def global_travel(code):
    for instr in dis.get_instructions(code):
        op = instr.opcode
        if op in GLOBAL_OPS:
            yield op, instr.arg


def get_global_code(co):
    out_names = weakref.WeakKeyDictionary().get(co)
    if out_names is None:
        names = co.co_names
        out_names = {names[oparg] for _, oparg in global_travel(co)}
        if co.co_consts:
            for const in co.co_consts:
                if isinstance(const, types.CodeType):
                    out_names |= get_global_code(const)
        weakref.WeakKeyDictionary()[co] = out_names
    return out_names


class object_serializer:
    def obj_dic(self, obj):
        if inspect.isclass(obj):
            dic = {'__type__': 'class', '__class__': str(obj)}
            for attribute in dir(obj):
                if attribute.startswith('__'):
                    continue
                else:
                    value = getattr(obj, attribute)
                if "<class 'type'>" in str(value.__class__):
                    dic[attribute] = self.obj_dic(value)
                elif "<class '__main__." in str(value.__class__):
                    dic[attribute] = self.obj_dic(obj)
                elif callable(value):
                    dic[attribute] = self.obj_dic(value)
                else:
                    dic[attribute] = value
            return dic
        elif inspect.isfunction(obj) or inspect.ismethod(obj):
            argumets = {}
            dic = {'__type__': 'function'}
            argumets['co_argcount'] = repr(obj.__code__.co_argcount)
            argumets['co_posonlyargcount'] = repr(
                obj.__code__.co_posonlyargcount)
            argumets['co_kwonlyargcount'] = repr(
                obj.__code__.co_kwonlyargcount)
            argumets['co_nlocals'] = repr(obj.__code__.co_nlocals)
            argumets['co_stacksize'] = repr(obj.__code__.co_stacksize)
            argumets['co_flags'] = repr(obj.__code__.co_flags)
            argumets['co_code'] = obj.__code__.co_code.hex()
            argumets['co_consts'] = list(obj.__code__.co_consts)
            argumets['co_names'] = list(obj.__code__.co_names)
            argumets['co_varnames'] = list(obj.__code__.co_varnames)
            argumets['co_filename'] = repr(obj.__code__.co_filename)
            argumets['co_name'] = repr(obj.__code__.co_name)
            argumets['co_firstlineno'] = repr(obj.__code__.co_firstlineno)
            argumets['co_lnotab'] = obj.__code__.co_lnotab.hex()
            dic['args'] = argumets
            gl = get_global_code(obj.__code__)
            gla = {}
            gla['__builtins__'] = '<module \'builtins\' (built-in)>'
            for glob in gl:
                if glob in globals():
                    gla[glob] = repr(globals().get(glob))
            dic['globals'] = gla
            return dic
        else:
            dic = {'__type__': 'object', '__class__': obj.__class__.__name__}
            for attribute in obj.__dir__():
                if attribute.startswith('__'):
                    continue
                else:
                    value = getattr(obj, attribute)
                if callable(value):
                    dic[attribute] = self.obj_dic(value)
                elif "<class '__main__." in str(value.__class__):
                    dic[attribute] = self.obj_dic(value)
                else:
                    dic[attribute] = value
            return dic

    def dic_type(self, dic):
        if dic["__type__"] == "object":
            class_name = globals()[dic['__class__']]
            init_args = inspect.getfullargspec(class_name).args
            args = {}
            for arg in init_args:
                if arg in dic:
                    args[arg] = dic[arg]
            obj = class_name(**args)
            for attr in obj.__dir__():
                if isinstance(getattr(obj, attr), dict) and not attr.startswith('__'):
                    object_attr = self.dic_type(getattr(obj, attr))
                    setattr(obj, attr, object_attr)
                elif not attr.startswith('__') and attr not in args:
                    object_attr = getattr(obj, attr)

                    if not callable(object_attr):
                        setattr(obj, attr, dic[attr])
            return obj

        elif dic["__type__"] == "function":
            list_of_args = []
            import importlib
            list_of_globals = dic["globals"]
            for glob in list_of_globals:
                if str.isnumeric(list_of_globals[glob]):
                    list_of_globals[glob] = int(list_of_globals[glob])
                else:
                    if list_of_globals[glob].find("module") > 0:
                        if list_of_globals[glob].find("from") > 0:
                            value = list_of_globals[glob][9:list_of_globals[glob].find(
                                "from")-2]
                            list_of_globals[glob] = importlib.import_module(
                                value)
            for arg in dic:
                if arg == "args":
                    for value_args in dic[arg]:
                        list_of_args.append(dic[arg][value_args])
            code = types.CodeType(int(list_of_args[0]), int(list_of_args[1]), int(list_of_args[2]),
                                  int(list_of_args[3]), int(
                                      list_of_args[4]), int(list_of_args[5]),
                                  bytes.fromhex(list_of_args[6]), tuple(
                                      list_of_args[7]), tuple(list_of_args[8]),
                                  tuple(list_of_args[9]), list_of_args[10], list_of_args[11], int(
                                      list_of_args[12]),
                                  bytes.fromhex(list_of_args[13]))
            return types.FunctionType(code, list_of_globals)
        else:
            vars = {}
            name = dic["__class__"][17:-2]
            for attr in dic:
                if not isinstance(dic[attr], dict) and not attr.startswith('__'):
                    vars[attr] = dic[attr]
                elif isinstance(dic[attr], dict) and not attr.startswith('__'):
                    if dic[attr]['__type__'] == 'function':
                        vars[attr] = self.dic_type(dic[attr])
            return type(name, (object, ), vars)
