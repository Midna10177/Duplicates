#file name => duplicates.py


try:
   import cPickle as pickle
except:
   import pickle
import hashlib,io,os,signal,sys
from imohash import hashfile

#define default target here
root='C:\\Users\\Timothy'
if __name__=='__main__':
   tobe=sys.argv
   tobe.pop(0) #remove self path arg
   print(len(sys.argv))
   
   if len(sys.argv) > 0:
      root=os.path.join(' '.join(tobe))
      #concatenate all arguments into one path
   del(tobe) #free up space
   
   root=os.path.abspath(root) #set target's path to be absolute path
   print(root)
#---------------SIGSTOP handler---------------

#SAVE FUNCTION
def DUMPEVERYFUCKINGTHING(secondpass=False):
   total=0
   old = files.duplicates[0] #get first in list
   for x in files.duplicates:
      #if old is not x and md5s are different
      if old!=x and old.md5 ==x.md5:
         try: total += os.stat(x.name).st_size #add to size tally
         except: pass
      if old.md5 != x.md5:
         old=x
         #if we are in a new block of duplicate files, set the first found to be the first in the sequence

   #if this is the first pass, then the filelist
   #was generated using the imosum 
   logfile=root+os.sep+'duplicatefiles.txt'
   pyobjectlogfile=os.path.abspath(os.path.join(root,'duplicatefilespyPickleObject'))
   if not secondpass:
      logfile=os.path.abspath(os.path.join(root,'duplicatefiles-inaccurate.txt'))
      pyobjectlogfile=root+os.sep+'duplicatefilespyPickleObject-inaccurate'
   
   #io is imported to deal with the sometimes weirder special chars
   with io.open(logfile,'w', encoding="utf-8") as f:
       f.write(str(files)+str(len(files.duplicates))+' files listed.\n'+str(round(total/(1024*1024),3))+' mb listed')
   print('wrote to',logfile)

   pickle.dump(files,open(pyobjectlogfile,'wb'))
   print('wrote to',pyobjectlogfile)

signal.signal(signal.SIGTERM, DUMPEVERYFUCKINGTHING)
#---------------end of SIGSTOP handler---------------
def fastmd5(fname):
    return hashfile(fname,hexdigest=True)#, sample_size=2048*4)


def realmd5(fname):
    hash_md5 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65535), b""):
            hash_md5.update(chunk)
    result=hash_md5.hexdigest()
    del(hash_md5)
    return result



class FileList:
    root=root
    debugprintinterval=1
    def __init__(self):
        self.files=[]
        self.duplicates=[]
        
    
    def scan(self,root=None):
        from time import time
        t=time()
        debug=False
        if root==None: root=self.root
        for i in os.walk(root):
            for file in i[2]:
                if time()-t > self.debugprintinterval:
                   debug=True
                   t=time()
                else:
                   debug=False
                name=i[0]+os.sep+file
                if not os.path.islink(name):
                   self.files.append(File(name,fast=True,debug=debug))
                
    
    def sort(self):
        self.duplicates=[]
        self.files.sort(key=lambda x: int(x.md5,16))
        print('pre sort done.\nfinding duplicates...')
        print(self.files)
        while(self.files):
            x=self.files.pop(0)
            for y in self.files:
               if int(y.md5,16) > int(x.md5,16):
                  print('proccessed quickly',x.name)
                  break
               if x!=y and x.md5==y.md5:
                  if x not in self.duplicates:
                        self.duplicates.append(x)
                  if y not in self.duplicates:
                        self.duplicates.append(y)
                        
            print(len(self.files),'left, proccessed',x.name)
                
        print('finished sorting.')

        
    def sort_secondpass(self): #reruns through dupes but checks md5 of entire file
        self.files=[]
        for x in self.duplicates:
            self.files.append(File(x.name,fast=False))
        self.sort()
        
        
    def __repr__(self):
        o=''
        if len(self.duplicates) <=0:
            raise ValueError('no duplicates stored in filelist')
        #for x in self.files: o+= str(x)+'\n\n'
        o+='\n\n\n---DUPLICATES---\n\n\n'
        old=None
        try: old=self.duplicates[0]
        except: pass
        for y in self.duplicates:
            if y.md5 != old.md5:
                o+='-'*45
                o+='\n'
            old=y
            o+=str(y)+'\n\n'
        return o
    
        
class File:
    def __init__(self,name,fast=True,debug=True):
        self.name=name
        self.md5='0'
        if debug: print('doing',name,'...')
        if fast:
            try: self.md5=fastmd5(self.name)
            except: self.md5='0'
        else:
            try: self.md5=realmd5(self.name)
            except: self.md5='0'
            
        #print(self)
        
    def getsize(self):
        try: return(os.stat(self.name).st_size)
        except: return 0
        
        
    def __repr__(self):
        return(self.name+' '+str(round(self.getsize()/1024))+'kb\n'+str(self.md5))
if __name__=='__main__':        
   import time

   t=time.time()
   files=FileList()

   print('scanning...')
   files.scan()

   print(time.time()-t,'seconds')
   t=time.time()

   print('now sorting...',str(len(files.files)),'files')
   files.sort()

   print(files)
   print(len(files.duplicates),'files listed.')
   DUMPEVERYFUCKINGTHING(secondpass=False)
   ##------------second pass------------
   print('doing SECOND PASS (checksumming entire files)')
   files.sort_secondpass()
   ##------------second pass------------
   print(files)

   print(len(files.duplicates),'files listed.')
   print(time.time()-t,'seconds')
   total=0
   old = files.duplicates[0]
   for x in files.duplicates:
      if old!=x and old.md5 ==x.md5:
         total += os.stat(x.name).st_size
      if old.md5 != x.md5:
         old=x
   print(round(total/(1024*1024),3),'mb listed')
   DUMPEVERYFUCKINGTHING(secondpass=True)
   i=input('press any key to exit')
