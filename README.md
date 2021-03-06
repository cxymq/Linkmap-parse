# Linkmap-parse
## 一、背景
由于工程代码日积月累的增加，并且伴随着需求变更，会有一些类被废弃。但是由于年代久远，无法确认某些类是否被废弃。所以才有此篇文章，来检测工程中的无用类。


## 二、开工
### 2.1 准备工作
#### 1.首先运行工程，得到 XXXApp 二进制和 XXXApp-LinkMap-normal-arm64.txt 文件（即是 linkmap 文件）。(此文基于 6s 真机，最好是真机，因为下面的脚本基于 arm64 架构，不然得自己改下，[旺柴])

XXX-Appp 二进制路径：
`
/Users/xxx_username/Library/Developer/Xcode/DerivedData/XXXApp-xxxxxxx/Build/Products/Debug-iphoneos/XXXApp
`

XXXApp-LinkMap-normal-arm64.txt 路径：
`
/Users/xxx_username/Library/Developer/Xcode/DerivedData/XXXApp-xxxxxxx/Build/Intermediates.noindex/XXXApp.build/Debug-iphoneos/XXXApp.build/XXXApp-LinkMap-normal-arm64.txt
`

注意：xxx_username 是本机用户名，XXXApp-xxxxxxx 是工程编译之后生成的文件名

提示：上述文件可放入同一文件夹，方便后面处理。



#### 2.获取脚本，也可和上述资源放到同一文件夹

该工程，主要是 main、linkmap.py、unuseclass.py 三个文件

### 2.2 运行
进入到上述资源根目录，运行(后面分别是二进制文件路径和 linkmap 文件路径，因为在当前目录，所以省略路径)

```
python3 main XXXApp.app/XXXApp XXXApp-LinkMap-normal-arm64.txt
```


运行结果(搜索“未使用的类如下”)，每列分别代表：内存地址、文件所占内存大小、编译文件（带有文件名）



注意：这里只是分析工程文件有哪些可能是废弃类，会误伤到 protocol 等文件。**所以一定需要人工审核才能删除。**

## 三、界面化
![image](https://user-images.githubusercontent.com/11361490/119323259-14da0d80-bcb1-11eb-830f-fb78659ef25b.png)
1 选择二进制文件，直接选择应用程序即可（.app）

2 选择 linkmap 文件

3 可查看类的内存占用分布，结果在下方区域展示

4 选中之后，表明模块解析，配合 5 使用

5 填写模块名，如 UM 或者 Live 等进行模块解析，再次点击 3 即可

6 过滤，只显示大于输入值的类内存分布，如填入 100，只显示大于 100 的类名，再次点击 3 即可

7 开始分析无用类，结果在下方区域展示

## 四、后续
**需要完成：**
增加文件白名单，防止误伤
