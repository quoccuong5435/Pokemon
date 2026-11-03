"""One-off: tiers of the regular templates follow the power (<= 60: 1, <= 100: 2, else 3); the ULT_ templates keep the old
band thresholds (<= 130: 1, <= 140: 2, else 3)."""
import io

NL = chr(10)


def edit(path, old, new):
    s = io.open(path, encoding='utf-8', newline='').read()
    if (chr(13) + NL) in s:
        old = old.replace(NL, chr(13) + NL)
        new = new.replace(NL, chr(13) + NL)
    assert s.count(old) == 1, (path, old[:70], s.count(old))
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new))


edit('tools/learn_data.py',
     "    shape = shape_of(info)" + NL +
     "    if shape == 'area':" + NL +
     "        return ('ULT_STOMP' if p > 115 and not special else ('NOVA' if special else 'STOMP')), tier" + NL +
     "    if shape == 'line':" + NL +
     "        return ('ULT_WAVE' if p > 115 else ('WAVE' if special else 'LINE')), tier" + NL +
     "    if shape == 'cone':" + NL +
     "        return 'CONE', tier" + NL +
     "    if p <= 60:" + NL +
     "        return ('CHAIN' if special else 'DAGGER'), tier" + NL +
     "    return 'BOLT', tier" + NL,
     "    reg = 1 if p <= 60 else 2 if p <= 100 else 3  # tier of the regular templates, from the power" + NL +
     "    shape = shape_of(info)" + NL +
     "    if shape == 'area':" + NL +
     "        if p > 115 and not special:" + NL +
     "            return 'ULT_STOMP', tier" + NL +
     "        return ('NOVA' if special else 'STOMP'), reg" + NL +
     "    if shape == 'line':" + NL +
     "        if p > 115:" + NL +
     "            return 'ULT_WAVE', tier" + NL +
     "        return ('WAVE' if special else 'LINE'), reg" + NL +
     "    if shape == 'cone':" + NL +
     "        return 'CONE', reg" + NL +
     "    if p <= 60:" + NL +
     "        return ('CHAIN' if special else 'DAGGER'), reg" + NL +
     "    return 'BOLT', reg" + NL)
print('ok')
