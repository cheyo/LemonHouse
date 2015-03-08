# LemonHouse

深圳市新房数据分析工具 by cheyo

## 依赖包

- Python 2.6
- BeautifulSoup
- Django
- django_pagination

## 软件结构

- Django项目
- Spider程序

## 安装步骤

下文以安装在/usr/app/house目录为例

+ 创建Python虚拟环境

```bash
mkdir -p /usr/app/house
cd /usr/app/house
virtualenv ENV
```

+ 安装BeautifulSoup

  pip install beautifulsoup4

+ 安装Django

+ 下载工程代码

形成如下目录结构：

```
[root@cheyo house]# pwd
/usr/app/house
[root@cheyo house]# l
total 16
drwxr-xr-x 7 root root 4096 Mar  8 21:35 DjangoHome
drwxr-xr-x 5 root root 4096 Mar  8 21:34 ENV
drwxr-xr-x 3 root root 4096 Mar  8 21:35 spider
drwxr-xr-x 2 root root 4096 Mar  8 21:35 task
[root@cheyo house]#
```

+ 安装包
