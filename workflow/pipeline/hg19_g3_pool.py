import os
from multiprocessing.dummy import Pool as ThreadPool

samplePath="./v3-g3/"
ref_path="./ref/hg19_centromere.fa"
alignedPath="./results/hg19_align/"
pbsvcallPath="./results/hg19_sv/"

if not os.path.exists(alignedPath):
    os.mkdir(alignedPath)
    
if not os.path.exists(pbsvcallPath):
    os.mkdir(pbsvcallPath)

def bamPath(rootPath):
    filelist=[]
    for root, dirs, files in os.walk(rootPath):                     
        for file in files:                                      
            (filename, extension) = os.path.splitext(file)  
            if (extension == '.bam'):
                alignOutput=os.path.join(alignedPath,"newref_"+file)
                subreadsPath=os.path.join(root, file)
                filelist.append(" ".join([subreadsPath, ref_path, alignOutput]))
    return filelist


def pbmmAlign(filelist):
    os.system(" ".join(['pbmm2 align ', filelist, ' --sort -j 10 -J 5']))


pool=ThreadPool(processes=4)
pool.map(pbmmAlign, bamPath(samplePath))
pool.close()
pool.join()


alignedfiles=os.listdir(alignedPath)
def svdiscover(file):
    filename=os.path.basename(file)
    svPath=os.path.join(pbsvcallPath, filename+".svsig.gz")
    filePath=os.path.join(alignedPath, file)
    os.system(" ".join(["pbsv discover", filePath, svPath]))

pool=ThreadPool()
pool.map(svdiscover, alignedfiles)
pool.close()
pool.join()

svfiles=[os.path.join(pbsvcallPath, svfile) for svfile in os.listdir(pbsvcallPath)]
os.system(" ".join(["pbsv call -j 10", ] + svfiles + [os.path.join(pbsvcallPath, "merge.vcf"),]))
