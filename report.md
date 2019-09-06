# 基于加速度计的手势检测

孟逸白 1600012994

整个系统的基本设想如下：人的手在做动作时会产生高频的振动。通过测量加速度计的频率特性，可以判断人的手势。

## 系统组成

系统主要分为以下3个部分：
- 传感装置：由MPU6050加速度计和ESP32单片机构成
- 数据分析：串口UART传输数据，进行特征提取，使用SVM分类 
- 上层应用：可能性多种多样，我做了一个识别手势控制PPT的demo。
我将依次介绍。

## 传感装置

传感装置需要测量加速度，主要解决2个问题：传输速率够不够，传来的数据时序对不对。利用MPU6050加速度计的FIFO，可以确保时序是正确的。为了实现较快的速度，把数据通过串口直接以二进制传输。要注意，ESP32是小端系统。

我还设置了开机自启动，进行校准。

## 数据分析

对于数据传输部分，我写了一个UART服务程序，接收数据，维护一个传输队列。要注意的是，esp32会自动加换行符，需要在menuconfig中进行修改。我利用了多线程，以维持逻辑的清晰。

对于特征分析部分，我的目的是分析频率特征，摆脱绝对位置和绝对运动的影响。因此我进行了信号预处理：
 - Hamming加窗谱分析，避免泄漏。
 - X, Y, Z三个能量谱取大值
 - 取10个周期的平均
之后进行了特征提取：
 - 平均，方差，最大的5个峰的值。使用sigmoid函数进行了归一化
 - 每个频段的和，band ratio

我使用了libsvm对特征构成的特征向量进行分类。几个核心参数是：kernel，多项式的系数，loss function的系数

对训练数据的采集，我分别做各种动作，采集数据。数据经过了我的手动删改，毕竟有些动作是没法连续做的。比如拍手，两次拍手之间的那些时刻，没有特别的特征。同时，我还不做动作地走路，写字，采集0结果的数据。

# 演示项目

我演示了一个利用reveal.js实现的ppt，通过手势可以对ppt进行控制。我把ppt放在了服务器上，并且通过websocket与之通信。

# 问题和改进

1. 采集数据费时费力，希望能有更好的办法
2. 争取能有更好的特征，尤其是能体现频率特性的特征
3. 想办法解决振动和手耦合不紧密的问题，或者处理耦合不紧密造成的问题。

# 文件说明
```
demo/ 展示
documents/ 参考文档
readings/ 有关论文资料和手册
esp32/ esp32的工程
server/ 数据分析部分，包括传输，特征提取和分类
```