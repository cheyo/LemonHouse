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

整套程序都在这个虚拟环境中运行.

```bash
mkdir -p /usr/app/house
cd /usr/app/house
virtualenv ENV
```

+ 安装Django

Django指定使用1.6版本,更高的版本需要Python 2.7因此使用Django1.6版本。

```bash
source ENV/bin/activate
pip install -v django==1.6
```

测试是否安装成功：

```python
(ENV)[root@cheyo house]# python
Python 2.6.6 (r266:84292, Jan 22 2014, 09:42:36)
[GCC 4.4.7 20120313 (Red Hat 4.4.7-4)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import django
>>> print(django.get_version())
1.6
>>>
```

+ 配置MySQL

为LemonHouse创建一个数据库。LemonHouse使用了事务，要求MySQL使用InnoDB作为存储引擎。

+ 安装相关Python库

```bash
pip install beautifulsoup4
pip install html5lib                 # this is for beautifulsoup4
pip install django-pagination
pip install MySQL-python
```

+ 配置Django

修改DjangoHome/django_house/settings.py文件中的数据库连接信息。建议创建一个独立的数据库给此程序。

+ 同步Django数据表

```bash
cd /usr/app/house/DjangoHome
python manage.py syncdb
```

+ 修改spider
修改/usr/app/house/spider/LemonHouseSpider.py第12行的数据库连接信息：

```python
conn = MySQLdb.connect(host="localhost", user='root', passwd='abcabc', db='LemonHouse2', charset='utf8')
```



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
