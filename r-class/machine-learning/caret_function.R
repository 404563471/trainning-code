## little function

### trans selected colnames(index) to factor
to_factor <- function(data, index){
  factor_index <- colnames(data) %in% index
  data[, factor_index] <- lapply(data[factor_index], as.factor)
  return(data)
}

### total variable number is x
check_delete_ID_col <- function(data, x){
  if (ncol(data) == x) {
    return(data)
  }
  else{
    message("the first column is ID and delete")
    return(data[-1,])
  }
}

### select the variable which no na
select_no_na_from_rawdata <- function(total_data){
    complete_index <- sapply(total_data, function(x) all(!is.na(x)))
    complete_data <- total_data[,complete_index]
    print(names(complete_index))
    return(complete_data)
}

###  Multivariate Imputation (variables without y)
get_complete_data <- function(imputation_total_data, factor_index=NULL, imputation_methods="rf"){
      require(mice)
      if (!is.null(factor_index)) {
        imputation_total_data <- to_factor(imputation_total_data, factor_index)
      }
      total_rf_methods <- mice(imputation_total_data, method = imputation_methods)
      imputation_output_data <- complete(total_rf_methods)
      complete_index <- sapply(imputation_total_data, function(x) all(!is.na(x)))
      
      for (i in colnames(total_data)[!complete_index]) {
        par(mfrow=c(1,2))
        hist(as.numeric(imputation_total_data[,i]), freq=F, main=paste0(i,': Original Data'), col='darkgreen')
        hist(as.numeric(imputation_output_data[,i]), freq=F, main=paste0(i,': MICE Output'), col='lightgreen')
      }
      return(imputation_output_data)
}

### filiter the variable
filiter_variable <- function(complete_data){
      # get the var which almost one number
      zerovar_index <- nearZeroVar(complete_data)
      filite_data <- complete_data[,-zerovar_index]
      # high cor
      descrCorr <- cor(filite_data)
      highcor_index <- findCorrelation(descrCorr)
      filite_data <- filite_data[, -highcor_index]
      
      # Determine linear combinations
      comboInfo <- findLinearCombos(filite_data)
      if(!is.null(comboInfo$remove)){
        filite_data <- filite_data[, -comboInfo$remove]
      } 
      
      return(filite_data)
}

### check if all packages installed
check_packages_install <- function(method_list, if_install=FALSE){
  need_packages <- sapply(method_list, function(x) getModelInfo(x)[[x]]$library)
  need_packages <- unique(unlist(need_packages))
  suppressPackageStartupMessages(ll <-lapply(need_packages, require, character.only = TRUE))
  if (all(unlist(ll))) {
    print("all packages installed")
  }
  else{
    if(if_install){
      checkInstall(need_packages)
    }
    print("packages need check again")
  }
}

### try every single model to training
# selected_m <- c("C5.0", "C5.0Cost", "C5.0Rules", "C5.0Tree", "dnn", "knn", "ORFlog", "ranger", "rf")

trainCall <- function(model_name, train_data, predict_var, trainControl, metric) 
{
  cat("----------------------------------------------------","\n");
  set.seed(7); cat(model_name," <- loaded\n");
  model_formula <- as.formula(paste0(predict_var, " ~ ."))
  return(tryCatch(
    fit <- train(model_formula ,
                data = train_data, 
                method = model_name, 
                trControl = trainControl,
                metric = metric),
#                trControl = trainControl(method="cv", number = 5, 
#                                         allowParallel = TRUE, verbose = TRUE, savePredictions = T)),
    error=function(e) NULL))
}

parallel_train <- function(selected_m, train_data, predict_var, trainControl, metric, ncore=4)
  {
        require(doParallel)
        cl <- makeCluster(4)
        registerDoParallel(cl) 
        train_result_list <- lapply(selected_m, function(x){trainCall(x, train_data, predict_var, trainControl, metric)})
        stopCluster(cl)
        registerDoSEQ()
        names(train_result_list) <- selected_m
        return(train_result_list)
}

## just print the result
printCall <- function(i, method_list, model_result) 
{
  return(tryCatch(
    {
      cat(sprintf("%-22s",(method_list[i])))
      cat(round(getTrainPerf(model_result[[i]])$TrainAccuracy,4),"\t")
      cat(round(getTrainPerf(model_result[[i]])$TrainKappa,4),"\t")
      cat(model_result[[i]]$times$everything[3],"\n")},
    error=function(e) NULL))
}

## return every methods result
get_Call <- function(i, method_list, model_result) 
{
  return(tryCatch(
    {
      restult <- c(method_list[i], 
                       round(getTrainPerf(model_result[[i]])$TrainAccuracy,4),
                       round(getTrainPerf(model_result[[i]])$TrainKappa,4),
                       round(model_result[[i]]$times$everything[3],4))},
      error=function(e) NULL))
}

### just use under function, I forget this and rebuild one
chose_best_model <- function(selected_model_result, selected_models)
{
  model_result <- sapply(1:length(selected_model_result), 
                         function(x){printCall(x, selected_models, selected_model_result)})
  model_result <- as.data.frame(t(model_result))
  colnames(model_result) <- c("methods", "Accuracy", "Kappa", "times")
  return(model_result)
}

### get many model results for select model
get_model_summary <- function(model_result){
  model_summary <- data.frame()
  #model_summary <- as.data.frame(matrix(NA,length(model_result), 5))
  #colnames(model_summary) <- c("name", "accuracy", "kappa", "time", "modelname")
  # fill data and check indexes and NA with loop/lapply 
  for (i in 1:length(model_result)) {
    model_summary[i, "name"] <- model_result[[i]]$method
    model_summary[i, "accuracy"] <- as.numeric(round(getTrainPerf(model_result[[i]])$TrainAccuracy,4))
    model_summary[i, "kappa"] <- as.numeric(round(getTrainPerf(model_result[[i]])$TrainKappa,4))
    model_summary[i, "time"] <- as.numeric(model_result[[i]]$times$everything[3])
    model_summary[i, "modelname"] <- model_result[[i]]$modelInfo$label
  }
  return(model_summary)
}

### do loop train for every single model methods and get every methods summary
train_summary <- function(selected_method, train_data, call=FALSE){
  # use parallel_train maybe faster
  fit <- lapply(selected_m, trainCall(x, train_data))
  fit <- fit[!sapply(fit, is.null)]
  if (call) {
    r2 <- lapply(1:length(fit), function(x) printCall(x,method_list = selected_m, model_result = fit))
  }
  model_summary <- get_model_summary(fit)
  return(model_summary)
}
