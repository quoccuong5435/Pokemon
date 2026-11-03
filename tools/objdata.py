"""Read/write WC3 object-data files (w3u/w3t/w3b/w3h = simple, w3a/w3d/w3q = leveled)."""
import struct

T_INT, T_REAL, T_UNREAL, T_STRING = 0, 1, 2, 3


class Reader:
    def __init__(self, data):
        self.d = data
        self.p = 0

    def i(self):
        v = struct.unpack_from('<i', self.d, self.p)[0]
        self.p += 4
        return v

    def f(self):
        v = struct.unpack_from('<f', self.d, self.p)[0]
        self.p += 4
        return v

    def id4(self):
        v = self.d[self.p:self.p + 4].decode('latin-1')
        self.p += 4
        return v

    def s(self):
        e = self.d.index(b'\x00', self.p)
        v = self.d[self.p:e].decode('utf-8', 'replace')
        self.p = e + 1
        return v


class Mod:
    __slots__ = ('field', 'type', 'level', 'data', 'value', 'end')

    def __init__(self, field, typ, value, level=0, data=0, end=0):
        self.field, self.type, self.value, self.level, self.data, self.end = field, typ, value, level, data, end

    def __repr__(self):
        lv = '[%d/%d]' % (self.level, self.data) if self.level or self.data else ''
        return '%s%s=%r' % (self.field, lv, self.value)


class Obj:
    def __init__(self, orig, new, mods):
        self.orig, self.new, self.mods = orig, new, mods

    @property
    def id(self):
        return self.new if self.new != '\x00\x00\x00\x00' else self.orig

    def get(self, field, level=None):
        for m in self.mods:
            if m.field == field and (level is None or m.level == level):
                return m.value
        return None

    def set(self, field, typ, value, level=0, data=0):
        for m in self.mods:
            if m.field == field and m.level == level:
                m.type, m.value, m.data = typ, value, data
                return
        self.mods.append(Mod(field, typ, value, level, data))

    def remove(self, field):
        self.mods = [m for m in self.mods if m.field != field]


class ObjFile:
    def __init__(self, data=None, leveled=False):
        self.leveled = leveled
        self.version = 2
        self.original = []
        self.custom = []
        if data:
            self._parse(data)

    def _parse(self, data):
        r = Reader(data)
        self.version = r.i()
        self.original = self._table(r)
        self.custom = self._table(r)

    def _table(self, r):
        n = r.i()
        objs = []
        for _ in range(n):
            orig = r.id4()
            new = r.id4()
            if self.version >= 3:
                # v3 (Reforged): sets of modifications; flatten them
                nsets = r.i()
                mods = []
                for _ in range(nsets):
                    r.i()  # set flag
                    mods += self._mods(r, r.i())
                objs.append(Obj(orig, new, mods))
                continue
            mods = self._mods(r, r.i())
            objs.append(Obj(orig, new, mods))
        return objs

    def _mods(self, r, cnt):
        mods = []
        for _ in range(cnt):
            field = r.id4()
            typ = r.i()
            level = data = 0
            if self.leveled:
                level = r.i()
                data = r.i()
            if typ == T_INT:
                val = r.i()
            elif typ in (T_REAL, T_UNREAL):
                val = r.f()
            else:
                val = r.s()
            end = r.i()
            mods.append(Mod(field, typ, val, level, data, end))
        return mods

    def all(self):
        return self.original + self.custom

    def find(self, oid):
        for o in self.custom + self.original:
            if o.id == oid:
                return o
        return None

    def to_bytes(self):
        out = bytearray(struct.pack('<i', self.version))
        for table in (self.original, self.custom):
            out += struct.pack('<i', len(table))
            for o in table:
                out += o.orig.encode('latin-1') + o.new.encode('latin-1')
                out += struct.pack('<i', len(o.mods))
                for m in o.mods:
                    out += m.field.encode('latin-1') + struct.pack('<i', m.type)
                    if self.leveled:
                        out += struct.pack('<ii', m.level, m.data)
                    if m.type == T_INT:
                        out += struct.pack('<i', int(m.value))
                    elif m.type in (T_REAL, T_UNREAL):
                        out += struct.pack('<f', float(m.value))
                    else:
                        out += str(m.value).encode('utf-8') + b'\x00'
                    end = m.end if m.end else 0
                    out += struct.pack('<i', end)
        return bytes(out)
