# AppPerformance

getPerformanceData.py脚本说明：

1. 获取指定app的cpu、内存数据，并生成趋势图

2. 获取内存数据PSS值的命令： adb shell dunmpsys meminfo pkgname
   可以设定间隔多长时间取一次数据，获取多少次；获取的数据会保存到本地txt文件中
   
3. 获取CPU数据命令： adb shell top | findstr pkgname
   因 adb shell dumpsys cpuinfo 在获取数据的过程中，出现有时取不到指定pkgname的cpu值的情况，故使用了top命令
   
4. 使用pylab库将获取到的数据，绘制成折线图，并保存到本地

5. 本脚本需要安装第三方库matplotlib
