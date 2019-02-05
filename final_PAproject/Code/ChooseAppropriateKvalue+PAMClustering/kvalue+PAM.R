library(factoextra)
library(NbClust)

new_data <- read.csv("new_data.csv")
df <- scale(new_data)
head(df)

new_data

set.seed(20)
irisCluster <- kmeans(new_data, 3, nstart = 20)
irisCluster
irisCluster$cluster <- as.factor(irisCluster$cluster)
ggplot(new_data, aes(index , close, color = irisCluster$cluster)) + geom_point()
fviz_cluster(pam.res, stand = FALSE, geom = "point",
             frame.type = "norm")

library(ggplot2)


# Elbow method
fviz_nbclust(df, kmeans, method = "wss") +
  geom_vline(xintercept = 4, linetype = 2)+
  labs(subtitle = "Elbow method")

# Silhouette method
fviz_nbclust(df, kmeans, method = "silhouette")+
  labs(subtitle = "Silhouette method")

# Gap statistic
# nboot = 50 to keep the function speedy. 
# recommended value: nboot= 500 for your analysis.
# Use verbose = FALSE to hide computing progression.
set.seed(123)
fviz_nbclust(df, kmeans, nstart = 25,  method = "gap_stat", nboot = 50)+
  labs(subtitle = "Gap statistic method")

library("cluster")
pam.res <- pam(df, 4)
plot(pam.res$cluster)
plot(pam(df, 4), ask = TRUE)

pam.res$cluster <- as.factor(pam.res$cluster)
ggplot(new_data, aes(index , close, color = pam.res$cluster)) + geom_point()

fviz_cluster(pam.res, stand = FALSE, geom = "point",
             frame.type = "norm")

fviz_nbclust(df, pam, method = "wss") +
  geom_vline(xintercept = 3, linetype = 2)

fviz_nbclust(df, hcut, method = "wss") +
  geom_vline(xintercept = 3, linetype = 2)

require(cluster)
fviz_nbclust(df, pam, method = "silhouette")

require(cluster)
fviz_nbclust(df, hcut, method = "silhouette",
             hc_method = "complete")


set.seed(123)
gap_stat <- clusGap(df, FUN = pam, K.max = 10, B = 50)
# Plot gap statistic
fviz_gap_stat(gap_stat)

# Compute gap statistic
set.seed(123)
gap_stat <- clusGap(df, FUN = hcut, K.max = 10, B = 50)
# Plot gap statistic
fviz_gap_stat(gap_stat)



nb <- NbClust(df, distance = "euclidean", min.nc = 2,
              max.nc = 10, method = "complete", index ="all")
nb



dv <- diana(df, metric = "eucledian", stand = TRUE)
print(dv)
plot(dv)

agn1 <- agnes(df, metric = "eucledian", stand = TRUE)
agn1
plot(agn1)

df

library("ggpubr")
ggscatter(new_data, x = 'close', y = 'close', 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "X", ylab = "Y")

distance <- get_dist(df)
fviz_dist(distance, gradient = list(low = "#00AFBB", mid = "white", high = "#FC4E07"))
