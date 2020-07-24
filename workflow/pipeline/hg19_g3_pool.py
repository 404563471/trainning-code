import os
from multiprocessing.dummy import Pool as ThreadPool



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

def svdiscover(file):
    filename=os.path.basename(file)
    svPath=os.path.join(pbsvcallPath, filename+".svsig.gz")
    filePath=os.path.join(alignedPath, file)
    os.system(" ".join(["pbsv discover", filePath, svPath]))


allSamplePath = "./data/human/rawdata/"
ref_path="./data/human/ref/hg19_fix.fa"
resultPath="./results"

for sample in os.listdir(allSamplePath):
    samplePath=os.path.join(allSamplePath, sample)
    alignedPath=os.path.join("./results/hg19_align/", sample)
    pbsvcallPath=os.path.join("./results/hg19_sv/", sample)

    if not os.path.exists(alignedPath):
        os.makedirs(alignedPath)
        
    if not os.path.exists(pbsvcallPath):
        os.makedirs(pbsvcallPath)

    pool=ThreadPool(processes=6)
    pool.map(pbmmAlign, bamPath(samplePath))
    pool.close()
    pool.join()

    alignedfiles=[ bam for bam in os.listdir(alignedPath) if os.path.splitext(bam)[1] == "bam" ]

    pool=ThreadPool()
    pool.map(svdiscover, alignedfiles)
    pool.close()
    pool.join()

    svfiles=[os.path.join(pbsvcallPath, svfile) for svfile in os.listdir(pbsvcallPath)]
    os.system(" ".join(["pbsv call -j 20", ref_path] + svfiles + [os.path.join(pbsvcallPath, "merge.vcf"),]))
