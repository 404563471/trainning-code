library(GEOquery)
ls("package:GEOquery")
#[1] "Accession"        "Columns"          "dataTable"        "GDS2eSet"         "GDS2MA"          
#[6] "getGEO"           "getGEOfile"       "getGEOSuppFiles"  "getGSEDataTables" "GPLList"         
#[11] "GSMList"          "gunzip"           "Meta"             "parseGDS"         "parseGEO"        
#[16] "parseGPL"         "parseGSE"         "parseGSM"         "show"             "Table"           

getGEOSuppFiles("GSE49232", makeDirectory = F, baseDir = "~/liver_cancer/download/")
getGEOfile("GSE49232", destdir = "~/liver_cancer/download/", amount = "full")
GSE49232 <- getGEO("GSE49232", filename = "~/liver_cancer/download/GSE49232.soft.gz", destdir = "~/liver_cancer/download/")






###################################################
library(biomaRt)
Genebank <- useMart("ENSEMBL_MART_ENSEMBL")
Genebank <- useDataset("hsapiens_gene_ensembl", mart = Genebank)
#listFilters(Genebank), affy_hg_u133_plus_2
#listAttributes(Genebank), hgnc_symbol, refseq_ncrna, wikigene_name, wikigene_description, description, refseq_mrna, ensembl_transcript_id, transcript_biotype
attributes <- listAttributes(Genebank)
getBM(attributes = c("hgnc_symbol", "refseq_mrna", "description"), filters = "affy_hg_u133_plus_2", values = c("224945_at", "226178_at", "225643_at", "202128_at", "209654_at"), mart = Genebank)
#description <- getBM(attributes = c("hgnc_symbol", "refseq_mrna", "description"), filters = "affy_hg_u133_plus_2", values = rownames(GSE84044_cor)[GSE84044_cor$`224945_at_cor` > 0.8], mart = Genebank)
write.table(description, "~/description.txt")

GSE84044_description <- getBM(attributes = c("ensembl_transcript_id", "transcript_biotype"), filters = "affy_hg_u133_plus_2", values = rownames(GSE84044_expression_rma_filter), mart = Genebank)


attributes$name[grep("affy", attributes$name)]

getBM(attributes = "hgnc_symbol", filters = "affy_hta_2_0", values = rownames(GSE76250_foldchange), mart = Genebank)
getBM(attributes = "hgnc_symbol", filters = "affy_hg_u133a", values = TCGA_down_probe, mart = Genebank)
test <- getBM(attributes = c("hgnc_symbol", "affy_primeview", "affy_hg_u133a"), filters = "affy_primeview", values = rownames(GSE69106_50_fold_change), mart = Genebank, bmHeader = T)
getBM(attributes = c("hgnc_symbol", "affy_primeview", "affy_hg_u133a"), filters = "affy_primeview", values ="11761514_at", mart = Genebank, bmHeader = T)

########################################################
##
##stringr
##
#########################################################
library(stringr)
txt <- c("The", "licenses", "for", "most", "software", "are",
         "designed", "to", "take", "away", "your", "freedom",
         "to", "share", "and", "change", "it.",
         "", "By", "contrast,", "the", "GNU", "General", "Public", "License",
         "is", "intended", "to", "guarantee", "your", "freedom", "to",
         "share", "and", "change", "free", "software", "--",
         "to", "make", "sure", "the", "software", "is",
         "free", "for", "all", "its", "users")
help(package="stringr")





#####################################
##
##formatR
#####################################
library(formatR)

tidy_source("~/liver_cancer/test.R", file = "~/liver_cancer/test_format.R", width.cutoff = 20)



####################################
##
## UCSC.hg19
####################################

library(TxDb.Hsapiens.UCSC.hg19.knownGene)
# Db type: TxDb
# Supporting package: GenomicFeatures
# Data source: UCSC
# Genome: hg19
# Organism: Homo sapiens
# Taxonomy ID: 9606
# UCSC Table: knownGene
# Resource URL: http://genome.ucsc.edu/
# Type of Gene ID: Entrez Gene ID
# Full dataset: yes
# miRBase build ID: GRCh37
# transcript_nrow: 82960
# exon_nrow: 289969
# cds_nrow: 237533
# Db created by: GenomicFeatures package from Bioconductor
# Creation time: 2015-10-07 18:11:28 +0000 (Wed, 07 Oct 2015)
# GenomicFeatures version at creation time: 1.21.30
# RSQLite version at creation time: 1.0.0
# DBSCHEMAVERSION: 1.1

genes(TxDb.Hsapiens.UCSC.hg19.knownGene)

###############################################
#
#org.hs.eg.db, just like hgu133plus.db, to transformed symbol ID
#
###############################################
library(org.Hs.eg.db)


################################################
##
##progress bar, for loop and apply loop(parallel)
##
##################################################
library(progress)
pb <- progress_bar$new(format = "survival ploting: (:spin) [:bar] :percent", total = 100, clear = FALSE, width = 100)

for (i in 1:100) {
  Sys.sleep(1 / 10)
  pb$tick()
}


library(pbapply)

set.seed(1234)
n <- 200
x <- rnorm(n)
y <- rnorm(n, crossprod(t(model.matrix(~ x)), c(0, 1)), sd = 0.5)
d <- data.frame(y, x)
## model fitting and bootstrap
mod <- lm(y ~ x, d)
ndat <- model.frame(mod)
B <- 100
bid <- sapply(1:B, function(i) sample(nrow(ndat), nrow(ndat), TRUE))
fun <- function(z) {
  if (missing(z))
    z <- sample(nrow(ndat), nrow(ndat), TRUE)
  coef(lm(mod$call$formula, data=ndat[z,]))
}

system.time(res1 <- lapply(1:B, function(i) fun(bid[,i])))

op <- pboptions(type = "timer") # default
system.time(res1pb <- pblapply(1:B, function(i) fun(bid[,i])))
pboptions(op)

pboptions(type = "txt", style = 1, char = "=")
system.time(res3pb <- pbapply(bid, 2, fun))
pboptions(op)

library(parallel)
cl <- makeCluster(2L)
clusterExport(cl, c("fun", "mod", "ndat", "bid"))
system.time(res1pbcl <- pblapply(1:B, function(i) fun(bid[,i]), cl = cl))
stopCluster(cl)

####################################################
##
## logical symbol
##
####################################################
a <- c(TRUE, FALSE, TRUE)
b <- c(FALSE, FALSE, TRUE)

a | b
a || b
a & b
a && b

##################################################
##
## R color
##
##################################################

library(RColorBrewer)
display.brewer.all()
display.brewer.pal()
display.brewer.pal(4, "Paired")

library(gridExtra)
library(ggsci)
# ggplot + scale_**********

#library(devtools)
library(githubinstall)
#install_github("ggtech")
githubinstall("ggtech")
githubinstall("ggthmer")

library(ggthemr)
library(ggthemes)

help(package = "ggthemr")



################################################
##
##  plyr
##
##################################################
# Summarize a dataset by two variables
dfx <- data.frame(
  group = c(rep('A', 8), rep('B', 15), rep('C', 6)),
  sex = sample(c("M", "F"), size = 29, replace = TRUE),
  age = runif(n = 29, min = 18, max = 54)
)

# Note the use of the '.' function to allow
# group and sex to be used without quoting
ddply(dfx, .(group, sex), summarize,
      mean = round(mean(age), 2),
      sd = round(sd(age), 2))

# An example using a formula for .variables
ddply(baseball[1:100,], ~ year, nrow)
# Applying two functions; nrow and ncol
ddply(baseball, .(lg), c("nrow", "ncol"))

# Calculate mean runs batted in for each year
rbi <- ddply(baseball, .(year), summarise,
             mean_rbi = mean(rbi, na.rm = TRUE))
# Plot a line chart of the result
plot(mean_rbi ~ year, type = "l", data = rbi)

# make new variable career_year based on the
# start year for each player (id)
base2 <- ddply(baseball, .(id), mutate,
               career_year = year - min(year) + 1
)


test <- scan()


#####################################################
##
## data.table
##
#######################################################
library(data.table)
library(stringr)
dt <- data.table(a = rep(c("A", "B"), c(3,3)), b = rnorm(6))
df <- data.frame(a = rep(c("A", "B"), c(3,3)), b = rnorm(6))

setkey(dt, a) # if change the "a" col of dt, the key(dt) will be null !!!!!
dt[,c := b+2]
dt[,c("d1", "d2") := sample(LETTERS, 12, replace = T)]
dt[,c("d1", "d2") := list(sample(LETTERS, 6, replace = T), rep("C", 6))]
dt[, d1 := NULL]
dt[, c("c", "d2") := NULL]
dt[, c := rnorm(6)]

dt[a == "A"]
dt[a == "A" & c > 0, b:=100]

setnames(dt, "c", "3")
dt[2:3, sum(b)]

setkeyv(dt, c("a", "b"))
dt[.("A",30)]
dt[!.("A",30)]

transpose(dt)

# It is different that dt[,1] with dt$a !!!!!!!!!!!!

##################################################
##
## plotly
##
###################################################
library(plotly)
ggplotly(p = data1_P)


################################################
##
## ggimage
##
################################################
#compilation failed for package ‘fftwtools’
#sudo yum install fftw-devel.x86_64




####################################################
##
##swirls, DataScienceR 
##
###################################################
library(swirl)
swirl()


###############################################
##
## handle Na with VIM and mice
##
###############################################
library(VIM)
library(mice)
data(sleep)

md.pattern(sleep)
aggr(sleep)
aggr(sleep, prop = F, number = T)
matrixplot(sleep)

x <- data.table(abs(is.na(sleep)))
cor(x)
cor(sleep, x)

imp <- mice(sleep, seed = 1234)
fit <- with(imp, lm(Dream ~ Span + Gest))
pooled <- pool(fit)
summary(pooled)

complete(imp, action = 2)


##############################################
##
## ggalt and ggedit
##
##############################################
#befor install package ggalt, yum install proj-dev.x86_64 !!!
help(package = "ggalt")

help(package = "ggedit")



############################################
##
##https://cran.r-project.org/web/views/ 
##I can find views in the URL
##
##############################################
library(ctv)
#install.views("Econometrics")


###########################################
##
##quantmod for stock
##
##########################################
library(quantmod)
setSymbolLookup(WK = list(name = "000002.sz", src = "yahoo"))
getSymbols("WK")
chart_Series(WK)

####################################
##
## ggmap
##
####################################
library(ggmap)
get_map()
