import os.path as osp
import sys
import os
import platform

BASEDIR = osp.abspath(osp.dirname(__file__))
if platform.system() == "Windows":
    DLLNAME = 'cambdll.dll'
else:
    DLLNAME = 'camblib.so'
CAMBL = osp.join(BASEDIR, DLLNAME)

mock_load = os.environ.get('READTHEDOCS', None)

if not mock_load:
    import ctypes
    from ctypes import Structure
    if not osp.isfile(CAMBL): sys.exit('%s does not exist.\nPlease remove any old installation and install again.'%DLLNAME)
    camblib = ctypes.cdll.LoadLibrary(CAMBL)
else:
    try:
        from unittest.mock import MagicMock
    except ImportError:
        from mock import Mock as MagicMock

    class Mock(MagicMock):
        @classmethod
        def __getattr__(cls, name):
            if name == 'pi':
                return 1
            else:
                return Mock()

        def __mul__(self,other):
            return Mock()

        def __pow__(self,other):
            return 1


    MOCK_MODULES = ['numpy','numpy.ctypeslib', 'ctypes']
    sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
    camblib = Mock()
    Structure = object
    import ctypes


def set_filelocs():
    HighLExtrapTemplate = osp.join(BASEDIR, "HighLExtrapTemplate_lenspotentialCls.dat")
    if not osp.exists(HighLExtrapTemplate):
        HighLExtrapTemplate = osp.abspath(osp.join(BASEDIR, "../..", "HighLExtrapTemplate_lenspotentialCls.dat"))

    func = camblib.__handles_MOD_set_cls_template
    func.argtypes = [ctypes.c_char_p, ctypes.c_long]
    s = ctypes.create_string_buffer(HighLExtrapTemplate)
    func(s, ctypes.c_long(len(HighLExtrapTemplate)))


if not mock_load:
    set_filelocs()


class CAMBError(Exception):
    pass


class CAMB_Structure(Structure):
    def __str__(self):
        s = ''
        for field_name, field_type in self._fields_:
            obj = getattr(self, field_name)
            if isinstance(obj, CAMB_Structure):
                s += field_name + ':\n  ' + str(obj).replace('\n', '\n  ').strip(' ')
            else:
                if isinstance(obj, ctypes.Array):
                    s += field_name + ' = ' + str(obj[:min(7, len(obj))]) + '\n'
                else:
                    s += field_name + ' = ' + str(obj) + '\n'
        return s
