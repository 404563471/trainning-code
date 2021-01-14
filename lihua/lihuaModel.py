import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

from sklearn.metrics import accuracy_score
from joblib import dump, load

## clean data
even_otu=pd.read_table("./even_otu_table_taxo_name.txt", skiprows=1)
even_otu=even_otu.drop(columns='taxonomy')
even_otu.set_index('#OTU ID', inplace=True)
even_otu=even_otu.T

group_list=pd.read_table("./mapping.txt", index_col=0)
even_otu_merge=even_otu.merge(group_list["Treatment"], left_index=True, right_index=True)

X=even_otu_merge.iloc[:,:-1]
y=even_otu_merge["Treatment"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

## model
names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
         "Naive Bayes", "QDA"]

classifiers = [
    KNeighborsClassifier(),
    SVC(kernel="linear"),
    SVC(kernel="rbf"),
    GaussianProcessClassifier(),
    DecisionTreeClassifier(),
    RandomForestClassifier(),
    MLPClassifier(),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]

for name, clf in zip(names, classifiers):
    clf.fit(X_train, y_train)
    y_pre=clf.predict(X_test)
    print(name, accuracy_score(y_test, y_pre))

    dump(clf, name+".model")

#Nearest Neighbors 0.5948275862068966
#Linear SVM 0.6206896551724138
#RBF SVM 0.603448275862069
#Gaussian Process 0.5862068965517241
#Decision Tree 0.6896551724137931
#Random Forest 0.6724137931034483
#Neural Net 0.6551724137931034
#AdaBoost 0.6551724137931034
#Naive Bayes 0.6724137931034483
#QDA 0.5344827586206896