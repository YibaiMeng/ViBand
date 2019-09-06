import random

from libsvm import svmutil
import training_data

label = ["clap", "flick", "rubb", "nothing"]


def load_data(label_num):
    data = training_data.data
    yes = data[label_num]
    no = []
    for i in range(len(data)-1):
        if i != label_num:
            no += data[i]
    no += data[-1][:int(len(data[-1]) * 1.0)]  # Too much nothing...
    y = [1 for i in range(len(yes))] + [-1 for i in range(len(no))]
    x = yes + no
    c = list(zip(x, y))
    random.shuffle(c)
    x, y = zip(*c)
    return y, x


def train(y, x):
    train_len = int(1.0 * len(y))
    prob = svmutil.svm_problem(y[:train_len], x[:train_len])
    param = svmutil.svm_parameter('-t 2 -c 4 -b 1 -e 1e-12')
    m = svmutil.svm_train(prob, param)
    return m
    # ans = svmutil.svm_predict(y[train_len:], x[train_len:], m)
    # return ans
    # print(m)

for i in range(len(label)):
    y, x = load_data(i)
    ans = train(y, x)
    svmutil.svm_save_model("model"+str(i), ans)
    print(ans)
