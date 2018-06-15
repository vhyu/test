from sklearn import svm
from sklearn.externals import joblib

class class_fit:
    the_nu = 0
    the_gamma = 0
    the_trainD = [] #传进来的是一个数组
    the_testD = [] #传进来的是一个数组
    the_pid = ''

    def __init__(self,nu,gamma,trainD,testD,pid):
        self.the_nu = nu
        self.the_gamma = gamma
        self.the_trainD = trainD
        self.the_testD = testD
        self.the_pid = pid

    #只用一次
    def fit(self):
        clf = svm.OneClassSVM(nu = self.the_nu, kernel="rbf", gamma=self.the_gamma)
        clf.fit(self.the_trainD)
        return clf
    def saveM(self,clf):
        module_Name = '../modle/' + self.the_pid + "_model.m"
        joblib.jump(clf,module_Name)

    def loadM(self):
        module_Name = '../modle/' + self.the_pid + "_model.m"
        clf = joblib.load(module_Name)
        return clf

    def pred(self,clf):
        y_pred_test = clf.predict(self.the_testD)
        # 预测结果
        n_error_test = y_pred_test[y_pred_test == -1].size
        pre_res = 1 - (n_error_test / len(self.the_testD))
        return pre_res