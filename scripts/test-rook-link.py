#!/usr/bin/env python3
import copy, importlib.util, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rook_validator', ROOT/'scripts'/'validate-rook-link.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
req=json.loads((ROOT/'ops/rook/examples/request-v1.json').read_text())
res=json.loads((ROOT/'ops/rook/examples/result-v1.json').read_text())

def reject(label,obj,kind='request',request=None):
    try:
        (m.validate_request(obj) if kind=='request' else m.validate_result(obj,request))
    except m.ValidationError:
        print('ok - rejects',label); return
    raise SystemExit('negative case unexpectedly passed: '+label)

m.validate_request(req); m.validate_result(res,req); print('ok - canonical request/result')
for label,mut in [
 ('unknown-operation', lambda x:x.__setitem__('operation','shell.exec.v1')),
 ('symbolic-ref', lambda x:x.__setitem__('base_commit','main')),
 ('bad-ack', lambda x:x.__setitem__('acknowledgement','yes')),
 ('mutation', lambda x:x['scope'].__setitem__('allow_mutation',True)),
 ('delegation', lambda x:x['scope'].__setitem__('delegate',True)),
 ('unknown-field', lambda x:x.__setitem__('command','whoami')),
 ('shell-field', lambda x:x.__setitem__('shell','pwsh')),
]:
    q=copy.deepcopy(req); mut(q); reject(label,q)
r=copy.deepcopy(res); r['request_id']='other'; reject('identity-mismatch',r,'result',req)
r=copy.deepcopy(res); r['request_path']='ops/rook/requests/../evil.json'; reject('path-traversal',r,'result',req)
print('all rook-link tests passed')
