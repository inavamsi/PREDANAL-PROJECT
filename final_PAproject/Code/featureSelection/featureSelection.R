
# ensure the results are repeatable
set.seed(7)
# load the library
library(mlbench)
library(caret)
# load the data
re <- read.csv("featureSelection.csv")
data(featureSelection)
# calculate correlation matrix
correlationMatrix <- cor(featureSelection[])
# summarize the correlation matrix
print(correlationMatrix)
# find attributes that are highly corrected (ideally >0.75)
highlyCorrelated <- findCorrelation(correlationMatrix, cutoff=0.5)
# print indexes of highly correlated attributes
print(highlyCorrelated)

plot(volume,type="o", col="blue")

m <- nsprcomp(featureSelection, scale.=T, k=5, ncomp=1)
m$rotation[, 1]

control <- trainControl(method="repeatedcv", number=10, repeats=3)
# train the model
install.packages('e1071', dependencies=TRUE)
model <- train(Label~., data=featureSelection, method="lvq", preProcess="scale", trControl=control)
# estimate variable importance
importance <- varImp(model, scale=FALSE)
# summarize importance
print(importance)
# plot importance
plot(importance)