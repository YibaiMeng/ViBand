from libsvm import svmutil

import config

models = []
def load_trained_models():
    global models
    for i in range(len(config.MODEL_LABEL)):
        models.append(svmutil.svm_load_model("model"+str(i)))
    return models

def eval(dat):
    ans = []
    for i in range(len(config.MODEL_LABEL) - 1):
        res = svmutil.svm_predict([], [dat], models[i], options="-q -b 1")
        #print(res[0][0])
        prob = res[2][0][0]
        #print(config.MODEL_LABEL[i], res)
        if res[0][0] >0 and prob > 0.9:
            ans.append([i, prob,res])
        elif i == 2 and res[0][0] >0 and prob > 0.6:
            ans.append([i,prob,res])
    ans.sort(key=lambda x: x[1])
    if ans:
        print(ans)
        return (ans[0][0], ans[0][1])
    else:
        return (-1, 0)
