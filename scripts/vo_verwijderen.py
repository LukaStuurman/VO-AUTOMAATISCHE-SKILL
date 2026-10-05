"""Een kabelcode is geen verwijder-eenheid: neem de unie van ALLE gebruikte delen."""
def removal_ledger(sources,directions):
 from shapely.ops import unary_union
 from shapely.geometry import shape
 result=[]
 for code,group in sources['groups'].items():
  used={d['id']:[shape(p['geometry']) if isinstance(p['geometry'],dict) else p['geometry'] for p in d['retained'] if p['code']==code] for d in directions}
  protected=unary_union([g for values in used.values() for g in values]);existing=group['geometry'];unused=existing.difference(protected)
  external=bool(group['outside_taps']);combo=group['combo']
  # The separate OV design has not established whether its conductor is abandoned.
  if external or combo:
   removable=existing.difference(existing);hold=unused;reason='Externe aansluitingen/voeding beschermen' if external else 'Combi: OV-gebruik apart controleren vóór fysieke verwijdering'
  else:
   removable=unused.intersection(sources['region']);hold=unused.difference(sources['region']);reason='Alleen ongebruikte LS-delen binnen eigen gebied; oorspronkelijke voeding isoleren bij de getekende scheidingen'
  result.append({'code':code,'used_by_directions':{k:unary_union(v).__geo_interface__ for k,v in used.items() if v},'used_length_m':protected.length,'unused_length_m':unused.length,'proposed_removal':removable.__geo_interface__,'proposed_removal_m':removable.length,'protected_unused':hold.__geo_interface__,'protected_unused_m':hold.length,'reason':reason,'source_modified':False})
 return result
