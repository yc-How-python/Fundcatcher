# Fundcatcher
#使用说明

在导入参数标签页设定跟踪基金的数目，设定后右侧的表格将提供相应的行。
在右侧表格输入基金编号及本金，提交。所有设定将由程序保存至setup文件。
每次启动程序后，界面初始化__init__函数将自动读取setup文件，并进行抓取。

# 更新
#2020.7.10
在setup文本中输入目标基金代码和本金，格式如下：

基金代码+tab+本金

运行程序后，每隔30秒自动刷新一次

#2020.7.27

更新后可在图形界面添加基金与本金

#2020.7.30

通过emit信号避免了数据刷新时的卡顿




