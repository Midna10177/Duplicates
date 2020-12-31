import pickle
from duplicates import * #my custom made dupe file finder
import os,sys

objfile=os.path.abspath('Downloads\\duplicatefilespyPickleObject')
args=sys.argv
args.pop(0)
if len(args)>=1:
	args=os.path.abspath(os.path.join(' '.join(args)))
	objfile=args
print(args)

data=pickle.load(open(objfile,'rb'))
size=0
old = data.duplicates[0]
for x in data.duplicates:
    
    if old.md5 != x.md5 and not os.path.islink(x.name):
        old=x
    oldn=old.name
    xn=x.name
    if old != x and old.md5 == x.md5 and not os.path.islink(xn) and not os.path.samefile(xn,oldn):
        print(old,'=>',x)
        size += os.stat(x.name).st_size
        os.remove(x.name)
        try: os.link(old.name,x.name)
        except:
                print('link from',old.name,'to',x.name,'failed, copying instead')
                from shutil import copyfile
                copyfile(old.name,x.name)
print('cleared',round(size/(1024*1024),2),'mb')
