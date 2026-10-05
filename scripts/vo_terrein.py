"""BGT-groen: hoofdtype nooit zonder het plustype beoordelen."""
def vegetation_class(properties):
 main=str(properties.get('fysiek_voorkomen','') or '').lower().strip()
 plus=str(properties.get('plus_fysiek_voorkomen','') or '').lower().strip()
 combined=main+' '+plus
 if any(word in combined for word in ['boom','bomen','bos','heester','struik','houtwal','houtopstand']):return 'woody'
 if any(word in combined for word in ['gras','gazon','akker','bouwland','weide','riet']):return 'open_green'
 if 'groenvoorziening' in combined or 'beplanting' in combined:return 'green_unknown'
 return 'other'

def unused_parts(existing_parts, used_by_direction, external_used_parts):
 """Een deel onder een andere richting of externe voeding blijft beschermd."""
 from shapely.ops import unary_union
 used=unary_union([g for values in used_by_direction.values() for g in values]+list(external_used_parts))
 return [g.difference(used) for g in existing_parts]
