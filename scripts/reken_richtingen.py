"""2024-padberekening. Leest een expliciet ontwerp; maakt geen kabelverbindingen op basis van nabijheid."""
import argparse
import json
import math
from pathlib import Path

# Gecontroleerde 2024-catalogus, Kabelchecker 4009601e15fa4b1b6926380395132b0c1630ce21.
CATALOGUE = {
    '150Al': {'R': .206, 'X': .079, 'Imax': 260.2125},
    '95Al': {'R': .320, 'X': .082, 'Imax': 203.6016},
    '50Al': {'R': .641, 'X': .085, 'Imax': 137.3436},
    '50Cu': {'R': .387, 'X': .085, 'Imax': 179.9739},
}
STEPS = [
    (63, 57, .250, .215), (80, 72, .250, .170),
    (100, 90, .204, .136), (125, 113, .163, .109),
    (160, 144, .128, .085), (200, 180, .092, .068),
    (250, 225, .062, .055),
]

def number(value):
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError('Een lengte of stroom moet eindig en niet-negatief zijn.')
    return result

def cable_type(text):
    raw = text.replace(' ', '').replace('4*', '').replace('mm2', '').lower()
    if raw in ['150al+', '150al']: return '150Al'
    if raw in ['50+6', '50cu+6cu', '50cu+']: return '50Cu'
    if raw.endswith('al'): return raw[:-2] + 'Al'
    if raw.endswith('cu'): return raw[:-2] + 'Cu'
    if raw.isdigit(): return raw + 'Cu'
    raise ValueError('Onbekende kabelnotatie: ' + text)

def calculate_path(path, profile, catalogue):
    if profile not in ['evenredig', 'laatste_helft']:
        raise ValueError('Een onderbouwd belastingsprofiel is vereist.')
    segments = path['segments']
    if not segments: raise ValueError('Een volledig pad mag niet leeg zijn.')
    ids = [s['id'] for s in segments if s.get('id')]
    if len(ids) != len(set(ids)):
        raise ValueError('Een gemeenschappelijk kabeldeel staat dubbel in hetzelfde pad.')
    R = X = length = 0.0
    ampacity = math.inf
    for segment in segments:
        kind = cable_type(segment['type'])
        if kind not in catalogue:
            raise ValueError('Kabeltype ontbreekt in de gevalideerde catalogus: ' + kind)
        L = number(segment['length_m']); cable = catalogue[kind]
        R += number(cable['R']) * L / 1000
        X += number(cable['X']) * L / 1000
        length += L
        if L > 0: ampacity = min(ampacity, number(cable['Imax']))
    if length == 0: raise ValueError('Een volledig pad moet een positieve lengte hebben.')
    Z = math.hypot(R, X)
    allowed = [s for s in STEPS if Z <= s[2 if profile == 'evenredig' else 3] + 1e-12 and ampacity + 1e-12 >= s[1]]
    step = allowed[-1] if allowed else None
    return {'id': path['id'], 'length_m': length, 'R_ohm': R, 'X_ohm': X,
            'Z_ohm': Z, 'ampacity_A': ampacity,
            'max_fuse_A': step[0] if step else 0,
            'max_design_A': step[1] if step else 0}

def assess_paths(direction, paths, catalogue, endpoint_mode):
    if not paths: raise ValueError('Alle hoofd- en aftakeindpaden zijn vereist.')
    checks = [calculate_path(p, direction['profile'], catalogue) for p in paths]
    limiting = min(checks, key=lambda c: (c['max_fuse_A'], -c['Z_ohm']))
    load = max(number(direction['verbruik_A']), number(direction['opwek_A']))
    requested = direction.get('desired_fuse_A')
    fuse = requested if requested is not None else limiting['max_fuse_A']
    step = next((s for s in STEPS if s[0] == fuse), None)
    fits = bool(step and fuse <= limiting['max_fuse_A'] and load <= step[1] + 1e-9)
    return {'id': direction['id'], 'endpoint_mode': endpoint_mode,
            'profile': direction['profile'], 'verbruik_A': number(direction['verbruik_A']),
            'opwek_A': number(direction['opwek_A']), 'design_load_A': load,
            'chosen_fuse_A': fuse, 'direction_max_fuse_A': limiting['max_fuse_A'],
            'capacity_A': step[1] if step else 0,
            'remaining_A': (step[1] if step else 0) - load,
            'limiting_path': limiting['id'], 'passes': fits, 'path_checks': checks}

def calculate_direction(direction, catalogue=CATALOGUE):
    full = assess_paths(direction, direction['end_paths'], catalogue,
                        direction.get('endpoint_mode', 'physical_end'))
    if full['passes'] or not direction.get('last_connection_paths'):
        return full
    # The endpoint may change; the assigned connections and their load may not.
    required = direction.get('connection_ids')
    covered = direction.get('last_connection_coverage')
    if (not required or set(required) != set(covered or [])
            or len(required) != len(set(required)) or len(covered or []) != len(set(covered or []))):
        raise ValueError('Laatste-aansluitingvariant moet dezelfde volledige aansluitingstoewijzing dekken.')
    alternative = assess_paths(direction, direction['last_connection_paths'], catalogue,
                               'last_connection')
    alternative['physical_end_assessment'] = full
    alternative['physical_tail_changed'] = False
    return alternative

def calculate_station(station, catalogue=CATALOGUE):
    if station.get('kader', 2024) != 2024:
        raise ValueError('Deze catalogus geldt voor kader 2024; laad en toets het juiste kader.')
    groups = station['categories']
    consumed = sum(number(g['count']) * number(g['trafo_verbruik_A']) for g in groups)
    generated = sum(number(g['count']) * number(g['trafo_opwek_A']) for g in groups)
    kva = number(station['kva'])
    if kva == 0: raise ValueError('De trafocapaciteit moet positief zijn.')
    maximum = kva / .23 / 3
    directions = [calculate_direction(d, catalogue) for d in station['directions']]
    return {'station': station['id'], 'kader': 2024,
            'trafo_verbruik_A': consumed, 'trafo_opwek_A': generated,
            'trafo_limit_A': maximum, 'trafo_remaining_A': maximum - max(consumed, generated),
            'trafo_passes': max(consumed, generated) <= maximum + 1e-9,
            'directions': directions, 'all_directions_pass': all(d['passes'] for d in directions)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    result = calculate_station(data['station'], data.get('catalogue', CATALOGUE))
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    else: print(text)

if __name__ == '__main__': main()
