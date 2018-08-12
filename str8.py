from collections.abc import ByteString
import functools
import sys

# TODO __getnewargs__ or whatever pickle uses

class Str8(bytes):
    """Str8(object='') -> Str8
    Str8(bytes_or_buffer[, encoding[, errors]]) -> Str8

    Create a new UTF-8 string object from the given object. If encoding or 
    errors is specified, then the object must expose a data buffer that will
    be decoded using the given encoding and error handler. Unlike str, a
    Str8 can also be created directly from a bytes-like object that's in
    UTF-8, without specifying an encoding. Otherwise, returns the result of
    object.__str__() (if defined) or repr(object).

    encoding defaults to 'utf-8'.
    errors defaults to 'strict'.

    A Str8 can mostly be used anywhere a str can be used, and also anywhere
    a bytes can be used. If needed, it will cache both representations.
    Notice that this means it is possible to produce Python 2-style errors
    or mojibake from mixing UTF-8 strings with non-UTF-8 bytes.

    Because str and bytes have mostly the same interface, it's sometimes
    necessary to specify which one you intend, by using the s or b property
    (although the default is always s). For example:

    >>> abc = Str8('áβç')
    >>> abc.find('β') # returns the character index
    1
    >>> abc[1:]
    'βç'
    >>> abc.s[1:]
    'βç'
    >>> abc.find(b'\xce\xb2') # returns the byte index
    2
    >>> abc.b[2:]
    'βç'
    """    
    def __new__(cls, object='', encoding=None, errors=None, *, _str=None):
        if isinstance(object, cls) and encoding is None and errors is None:
            return object
        elif _str is not None:
            self = super().__new__(cls, object)
            self._str = _str
            return self
        if isinstance(object, ByteString):
            recode = encoding or errors
            if not encoding: encoding = 'utf-8'
            if not errors: errors = 'strict'
            s = object.decode(encoding, errors)
            if recode:
                object = s.encode()
        else:
            s = str(object)
            object = s.encode()        
        self = super().__new__(cls, object)
        self._str = s
        return self
    def __repr__(self):
        return repr(self._str)
    def __str__(self):
        return self._str
    def __bytes__(self):
        # TODO: bytes(self)?
        return self
    def __getitem__(self, index):
        return type(self)(self._str[index])
    def __iter__(self):
        return iter(self._str)
    def __len__(self):
        return len(self._str)
    def __hash__(self):
        return hash(self._str)
    def __sizeof__(self):
        return super().__sizeof__() + sys.getsizeof(self._str)
    def __add__(self, other):
        if isinstance(other, ByteString):
            return type(self)(super().__add__(other))
        return type(self)(self._str + other)
    def __radd__(self, other):
        if isinstance(other, ByteString):
            return type(self)(other.__add__(self))
        return type(self)(other + self._str)
    def __mul__(self, n):
        return type(self)(self._str * n)
    __rmul__ = __mul__

    @property
    def b(self):
        return super().__getitem__(slice(None))
    @property
    def s(self):
        return self._str

    def encode(self, encoding='utf-8', errors='strict'):
        if encoding in {'utf-8', 'utf8', 'UTF-8', 'UTF8'}:
            return self
        return self._str.encode(encoding, errors)
    def decode(self, encoding='utf-8', errors='strict'):
        if encoding in {'utf-8', 'utf8', 'UTF-8', 'UTF8'}:
            return self
        t = type(self).__name__
        raise TypeError(f"Cannot decode UTF-8 '{t}' as '{encoding}'") 
    def hex(self):
        return type(self)(super().hex())
    @classmethod
    def fromhex(cls, string):
        return cls(bytes.fromhex(string))

    # TODO: Maybe __mod__ and maybe format should handle all bytes?
    @classmethod
    def _convert(cls, arg):
        if isinstance(arg, cls):
            return arg.s
        elif isinstance(arg, ByteString):
            return arg.decode()
        return arg
    def __format__(self, spec):
        return self._str.__format__(spec)
    # TODO: Should __mod__ handle %b and %s separately?
    def __mod__(self, args):
        args = tuple(map(self._convert, args))
        return type(self)(self._str % args)
    def __rmod__(self, arg):
        if isinstance(arg, ByteString):
            return bytes.__mod__(arg, self)
        elif isinstance(arg, str):
            return str.__mod__(arg, self._str)
        return NotImplemented
    def format(self, *args, **kwargs):
        args = tuple(map(self._convert, args))
        kwargs = {key: self._convert(value) for key, value in kwargs.items()}
        return type(self)(self._str.format(*args, **kwargs))
    def format_map(self, mapping):
        mapping = {key: self._convert(value) for key, value in mapping.items()}
        return type(self)(self.format_map(mapping))

    def join(self, iterable):
        iterable = [self._convert(arg) for arg in iterable]
        return type(self)(self._str.join(iterable))

    @staticmethod
    def maketrans(frm, to=None, delete=None):
        if to is None:
            frm = {Str8._convert(key): Str8._convert(value)
                   for key, value in frm.items()}
            return str.maketrans(frm)
        if delete is not None:
            if isinstance(frm, Str8): frm = frm.s
            if isinstance(to, Str8): to = to.s
            if isinstance(delete, Str8): delete = delete.s
            return str.maketrans(frm, to, delete)
        if isinstance(frm, ByteString) or isinstance(to, ByteString):
            return bytes.maketrans(frm, to)
        return str.maketrans(frm, to)
    
    def translate(self, table, *, delete=b''):
        if delete or isinstance(table, ByteString):
            return type(self)(bytes.translate(self, table, delete=delete))
        return type(self)(self._str.translate(table))
    
# lower-style methods: no string arguments, return str8
def _makemethod(_name):
    strmethod = getattr(str, _name)
    @functools.wraps(strmethod)
    def wrapper(self, *args, **kwargs):
        return type(self)(strmethod(self._str, *args, **kwargs))
    setattr(Str8, _name, wrapper)
for _name in ('capitalize', 'casefold', 'lower', 'swapcase', 'title', 'upper',
             'center', 'expandtabs', 'ljust', 'rjust', 'zfill'):
    _makemethod(_name)

# islower-style methods: no string arguments or return
def _makemethod(_name):
    strmethod = getattr(str, _name)
    @functools.wraps(strmethod)
    def wrapper(self, *args, **kwargs):
        return strmethod(self._str, *args, **kwargs)
    setattr(Str8, _name, wrapper)
for _name in ('isalnum', 'isalpha', 'isdecimal', 'isdigit', 'isidentifier',
             'islower', 'isnumeric', 'isprintable', 'isspace', 'istitle',
             'isupper'):
    _makemethod(_name)

# splitlines-style methods: no string arguments, return list of str8
def _makemethod(_name):
    strmethod = getattr(str, _name)
    @functools.wraps(strmethod)
    def wrapper(self, *args, **kwargs):
        results = strmethod(self._str, **kwargs)
        return [type(self)(result) for result in results]
    setattr(Str8, _name, wrapper)
for _name in ('splitlines',):
    _makemethod(_name)

# find-style methods: take str or bytes and treat them differently
# (e.g., find the character index or byte index) and return something else
def _makemethod(_name):
    bytesmethod = getattr(bytes, _name)
    strmethod = getattr(str, _name)
    @functools.wraps(strmethod)
    def wrapper(self, sub, *args, **kwargs):
        if isinstance(sub, ByteString):
            return bytesmethod(self, sub, *args, **kwargs)
        else:
            return strmethod(self._str, sub, *args, **kwargs)
    setattr(Str8, _name, wrapper)
for _name in ('__contains__',
             '__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__',
             'count', 'startswith', 'endswith',
             'find', 'rfind', 'index', 'rindex'):
    _makemethod(_name)

# strip-style methods: take str or bytes and treat them differently
# and return str8
def _makemethod(_name):
    bytesmethod = getattr(bytes, _name)
    strmethod = getattr(str, _name)
    @functools.wraps(strmethod)
    def wrapper(self, chars=None, *args, **kwargs):
        if chars is None:
            return type(self)(strmethod(self._str, **kwargs))
        elif isinstance(chars, ByteString):
            return type(self)(bytesmethod(self, chars, *args, **kwargs))
        else:
            return type(self)(strmethod(self._str, chars, *args, **kwargs))
    setattr(Str8, _name, wrapper)
for _name in ('lstrip', 'strip', 'rstrip'):
    _makemethod(_name)

# split-style methods: take str or bytes and treat them differently
# and return list of str8
def _makemethod(_name):
    bytesmethod = getattr(bytes, _name)
    strmethod = getattr(str, _name)
    @functools.wraps(strmethod)
    def wrapper(self, *args, **kwargs):
        if not args:
            results = strmethod(self._str, **kwargs)
        else:
            arg, *args = args
            if isinstance(arg, ByteString):
                results = bytesmethod(self, arg, *args, **kwargs)
            else:
                results = strmethod(self._str, arg, *args, **kwargs)
        return [type(self)(result) for result in results]
    setattr(Str8, _name, wrapper)
for _name in ('split', 'rsplit', 'partition', 'rpartition'):
    _makemethod(_name)

# replace-style methods: take two str or bytes and treat them differently
# and return str8
def _makemethod(_name):
    bytesmethod = getattr(bytes, _name)
    strmethod = getattr(str, _name)
    @functools.wraps(strmethod)
    def wrapper(self, old, new, *args, **kwargs):
        if isinstance(old, ByteString) and isinstance(new, ByteString):
            return type(self)(bytesmethod(self, old, new, *args, **kwargs))
        # TODO: maybe handle mixed args specially, or reject?
        if isinstance(old, ByteString):
            old = str(old.decode())
        if isinstance(new, ByteString):
            new = str(new.decode())
        return type(self)(strmethod(self._str, old, new, *args, **kwargs))
    setattr(Str8, _name, wrapper)
for _name in ('replace',):
    _makemethod(_name)
