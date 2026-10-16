import json,re,sys
from pythainlp.tokenize import syllable_tokenize
def spoken(s):
  out=[]
  for l in s.split('\n'):
    l=l.strip()
    if not l or re.match(r'^\[.*\]$',l): continue
    l=re.sub(r'^[^:“"\[]{1,40}:\s*','',l)
    out.append(l)
  return ' '.join(out)
def syl(text):
  n=0
  for chunk in re.findall(r'[฀-๿]+|[A-Za-z]+|\d+',text):
    if re.match(r'[฀-๿]',chunk): n+=len([x for x in syllable_tokenize(chunk) if x.strip()])
    elif chunk.isdigit(): n+=max(1,len(chunk))
    else: n+=max(1,len(re.findall(r'[aeiouy]+',chunk.lower())))
  return n
RATE=4.0  # syllables per second, clear training narration
if __name__=='__main__':
  rows=json.load(open(sys.argv[1]))
  res=[]
  for i,x in enumerate(rows):
    if x['fmt'].startswith('CGR'): continue
    s=syl(spoken(x['script'])); lines=len([l for l in x['script'].split('\n') if l.strip() and not l.startswith('[')])
    sec=s/RATE+ lines*0.6  # pauses between lines
    res.append((i,x['m'],x['fmt'][:5],s,round(sec),x['topic'][:45]))
  for k in ('Main ','Micro'):
    v=[r for r in res if r[2]==k]; secs=[r[4] for r in v]
    print(k,'avg',sum(secs)//len(secs),'min',min(secs),'max',max(secs))
    for r in sorted(v,key=lambda r:-r[4])[:6]: print('  hi',r)
    for r in sorted(v,key=lambda r:r[4])[:4]: print('  lo',r)
  json.dump(res,open(sys.argv[2],'w'),ensure_ascii=False)
