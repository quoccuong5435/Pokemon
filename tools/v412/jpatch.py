"""Small helpers shared by the script modules (move_tutor, wild_mix, random_gen). Script text uses LF line ends."""
import os

JASS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jass')


def read_jass(name):
    with open(os.path.join(JASS, name), encoding='utf-8') as fh:
        return fh.read().replace('\r\n', '\n')


def once(s, old, new, label, who):
    cnt = s.count(old)
    if cnt != 1:
        raise ValueError('[%s] anchor %r matched %d times (expected 1)' % (who, label, cnt))
    return s.replace(old, new, 1)


def replace_function(s, header, body, label, who):
    """replace the whole function that starts with `header` (from its line to its endfunction line)"""
    start = s.find('\n' + header)
    if start < 0 or s.find('\n' + header, start + 1) >= 0:
        raise ValueError('[%s] function %r not found exactly once' % (who, label))
    start += 1
    end = s.find('\nendfunction\n', start)
    if end < 0:
        raise ValueError('[%s] end of %r not found' % (who, label))
    end += len('\nendfunction\n')
    return s[:start] + body.rstrip('\n') + '\n' + s[end:]


def check_lf(s, mark, who):
    if '\r\n' in s:
        raise ValueError('[%s] give the script with LF line ends' % who)
    if mark in s:
        raise ValueError('[%s] script is already patched' % who)
