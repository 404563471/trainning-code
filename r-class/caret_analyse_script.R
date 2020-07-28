library(caret)
total_data <- read.csv("all_data_process.csv")
factor_index <- colnames(total_data)[c(2,26:ncol(total_data))]

source("crate_function.R")
pmm_data <- get_complete_data(total_data[,c(-1,-2)], factor_index = factor_index[-1], imputation_methods = "pmm")
pmm_data <- as.data.frame(sapply(pmm_data, as.numeric))
filite_data <- filiter_variable(pmm_data)
filite_data$y <- total_data$y

pro <- rfe(factor(y)~., filite_data, sizes = seq(8,ncol(filite_data)-1, 2),
           rfeControl=rfeControl(functions = rfFuncs, method = "cv"))
train_data <- filite_data[, c("y", pro$optVariables[1:10])]


selected_m <- c("C5.0", "dnn", "knn", "ORFlog", "ranger", "rf")


library(parallel)
library(doParallel)
cl <- makeCluster(4)
registerDoParallel(cl) 

t2 <- lapply(selected_m, function(x){trainCall(x, train_data)})
##clusterExport(cl, varlist = "trainCall")
##t2 <- parLapply(cl, selected_m, function(x){trainCall(x, train_data)})

stopCluster(cl)
registerDoSEQ()

lapply(1:length(t2), function(x){printCall(x, selected_m, t2)})


##########tune the model
library(doParallel)
cl <- makeCluster(8)
registerDoParallel(cl) 
tunegrid <- expand.grid(.mtry=c(1:15))
modellist <- list()

for (ntree in seq(500,2500,500)) {
set.seed(1234)
fit <- train(factor(y) ~ . ,
             data = train_data, 
             method = "rf", 
             tuneGrid=tunegrid,
             trControl = trainControl(method="cv", number = 5, 
                                      allowParallel = TRUE, verbose = TRUE, savePredictions = T))
key <- toString(ntree)
modellist[[key]] <- fit
} 
stopCluster(cl)
registerDoSEQ()             

rf_ml_finalmodel <- fit$finalModel
plot(fit)

saveRDS(rf_ml_finalmodel, "rf_test.rds")



