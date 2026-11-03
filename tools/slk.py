"""Minimal SYLK (.slk) table reader/writer used by WC3 optimized maps."""
import re


class Slk:
    def __init__(self, text):
        self.header_lines = []
        self.cols = {}      # col index -> name
        self.rows = []      # list of dict col_index -> raw value string
        self._parse(text)

    def _parse(self, text):
        cur_y = 0
        cells = {}
        for line in text.splitlines():
            if not line.startswith('C;'):
                if line.startswith(('ID', 'B;')):
                    self.header_lines.append(line)
                continue
            parts = line.split(';')
            x = None
            val = None
            for p in parts[1:]:
                if p.startswith('X'):
                    x = int(p[1:])
                elif p.startswith('Y'):
                    cur_y = int(p[1:])
                elif p.startswith('K'):
                    val = p[1:]
            if x is None:
                x = cur_x
            cur_x = x
            cells.setdefault(cur_y, {})[x] = val
        for y in sorted(cells):
            if y == 1:
                for x, v in cells[y].items():
                    self.cols[x] = v.strip('"')
            else:
                self.rows.append(cells[y])
        self.name_to_x = {v: k for k, v in self.cols.items()}

    @staticmethod
    def unquote(v):
        if v is None:
            return None
        if v.startswith('"') and v.endswith('"'):
            return v[1:-1]
        return v

    def get(self, row, col):
        x = self.name_to_x.get(col)
        return self.unquote(row.get(x)) if x is not None else None

    def find(self, key):
        for r in self.rows:
            if self.unquote(r.get(1)) == key:
                return r
        return None

    def to_text(self):
        ncols = max(self.cols)
        out = ['ID;PWXL;N;E', 'B;X%d;Y%d;D0' % (ncols, len(self.rows) + 1)]
        first = True
        for x in sorted(self.cols):
            out.append('C;%sX%d;K"%s"' % ('Y1;' if first else '', x, self.cols[x]))
            first = False
        for i, r in enumerate(self.rows):
            y = i + 2
            first = True
            for x in sorted(r):
                v = r[x]
                if v is None:
                    continue
                out.append('C;%sX%d;K%s' % ('Y%d;' % y if first else '', x, v))
                first = False
        out.append('E')
        return '\r\n'.join(out) + '\r\n'
