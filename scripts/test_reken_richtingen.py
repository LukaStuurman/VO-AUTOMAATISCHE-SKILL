"""Controle van ontwerpbeslissingen; uitsluitend standaardbibliotheek."""
import copy
import json
import math
import unittest
from pathlib import Path
from reken_richtingen import calculate_direction, calculate_station, cable_type

def path(name, *parts):
    return {'id': name, 'segments': [{'id': s, 'type': t, 'length_m': l} for s,t,l in parts]}

class DesignRules(unittest.TestCase):
    def test_user_reference(self):
        case = json.loads((Path(__file__).parents[1]/'references/011601-correct.json').read_text(encoding='utf8'))
        result = calculate_station(case['station'])
        self.assertTrue(result['trafo_passes'] and result['all_directions_pass'])
        self.assertAlmostEqual(result['trafo_verbruik_A'], 886.8)
        self.assertAlmostEqual(result['trafo_opwek_A'], 909.6)
        self.assertEqual([d['chosen_fuse_A'] for d in result['directions']], [250,250,160,160,200,125,200])
        r5 = next(d for d in result['directions'] if d['id']=='R5')
        self.assertEqual(r5['limiting_path'], 'kader-rekenpad')
        self.assertLess(r5['path_checks'][0]['length_m'], r5['path_checks'][1]['length_m'])
        self.assertGreater(r5['path_checks'][0]['Z_ohm'], r5['path_checks'][1]['Z_ohm'])
        self.assertEqual(sum(d['connection_count'] for d in case['station']['directions']), 125)

    def test_branch_controls_entire_direction(self):
        d = {'id':'example','profile':'evenredig','verbruik_A':120,'opwek_A':100,
             'end_paths':[path('main',('shared','150Al',60),('main','95Al',80)),
                          path('branch',('shared','150Al',60),('branch','50Al',120))]}
        r = calculate_direction(d)
        self.assertEqual(r['direction_max_fuse_A'], 125)
        self.assertEqual(r['limiting_path'], 'branch')
        self.assertFalse(r['passes'])
        self.assertEqual([p['length_m'] for p in r['path_checks']], [140,180])

    def test_last_connection_fallback_keeps_load_and_tail(self):
        d = {'id':'example','profile':'laatste_helft','verbruik_A':140.4,'opwek_A':135,
             'desired_fuse_A':160,'connection_ids':['a','b'],'last_connection_coverage':['a','b'],
             'end_paths':[path('physical',('main','150Al',390))],
             'last_connection_paths':[path('last',('main','150Al',373.05))]}
        r = calculate_direction(d)
        self.assertTrue(r['passes']); self.assertFalse(r['physical_end_assessment']['passes'])
        self.assertEqual(r['endpoint_mode'], 'last_connection')
        self.assertEqual(r['design_load_A'], 140.4); self.assertFalse(r['physical_tail_changed'])
        for invalid in [['a'],['a','b','b']]:
            bad = copy.deepcopy(d); bad['last_connection_coverage']=invalid
            with self.assertRaises(ValueError): calculate_direction(bad)

    def test_profile_is_a_material_choice(self):
        d = {'id':'example','profile':'evenredig','verbruik_A':179.4,'opwek_A':172.5,
             'end_paths':[path('main',('main','150Al',257.49))]}
        self.assertEqual(calculate_direction(d)['direction_max_fuse_A'],250)
        d['profile']='laatste_helft'
        self.assertEqual(calculate_direction(d)['direction_max_fuse_A'],200)

    def test_double_counted_shared_segment_rejected(self):
        d = {'id':'example','profile':'evenredig','verbruik_A':10,'opwek_A':0,
             'end_paths':[path('main',('shared','150Al',60),('shared','150Al',60))]}
        with self.assertRaises(ValueError): calculate_direction(d)

    def test_categories_and_variable_trafo(self):
        station = {'id':'test','kva':400,'kader':2024,'categories':[
            {'count':1,'trafo_verbruik_A':3.8,'trafo_opwek_A':0}], 'directions':[]}
        r=calculate_station(station)
        self.assertEqual(r['trafo_verbruik_A'],3.8)
        self.assertAlmostEqual(r['trafo_limit_A'],400/.23/3)
        station['kva']=0
        with self.assertRaises(ValueError): calculate_station(station)
        self.assertEqual(cable_type('50+6'),'50Cu')
        self.assertEqual(cable_type('150Al+'),'150Al')
        self.assertEqual(cable_type('50'),'50Cu')

if __name__=='__main__': unittest.main()
