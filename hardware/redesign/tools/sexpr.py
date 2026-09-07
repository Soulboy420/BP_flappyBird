"""Small KiCad s-expression reader/writer; preserves quoted strings."""
import re, json
class Q(str): pass
def parse(text):
 tokens=iter(re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+', text))
 def node(t):
  if t=='(':
   a=[]
   for u in tokens:
    if u==')': return a
    a.append(node(u))
   raise ValueError('unclosed expression')
  return Q(json.loads(t)) if t.startswith('"') else t
 return node(next(tokens))
def dumps(n):
 if isinstance(n,list): return '('+' '.join(map(dumps,n))+')'
 if isinstance(n,Q): return json.dumps(str(n),ensure_ascii=False)
 return str(n)
def get(n,key,default=None):
 return next((x for x in n if isinstance(x,list) and x and x[0]==key),default)
def allof(n,key): return [x for x in n if isinstance(x,list) and x and x[0]==key]
def walk(n,key):
 if isinstance(n,list):
  if n and n[0]==key: yield n
  for x in n: yield from walk(x,key)
