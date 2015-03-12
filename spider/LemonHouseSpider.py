#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import MySQLdb
import logging
import logging.config
from decimal import Decimal
from bs4 import BeautifulSoup


conn = MySQLdb.connect(host="localhost", user='root', passwd='abcabc', db='LemonHouse', charset='utf8')


class Batch():
    def __init__(self, id):
        self.id = id
        
    def get_project_list(self):
        post_data = self.get_post_data()
        soup = request_html_soup('http://ris.szpl.gov.cn/bol/index.aspx', 'POST', post_data)
        project_list = []
        for trTag in soup.find_all("tr", attrs={"bgcolor": "#F5F9FC"}):
            tdTags = trTag.findChildren(recursive=False)
            
            curr_project = Project()
            curr_project.id = int(tdTags[1].a['href'].split("=")[1])
            curr_project.name = tdTags[2].get_text()
            curr_project.company = tdTags[3].get_text()
            curr_project.region = tdTags[4].get_text()

            import time
            dateStr = tdTags[5].get_text()

            # "深房许字（2009）南山002号 中信红树湾花城三期"特殊处理
            if u""== dateStr:
                logging.error("error Date:%s. set to 2009-02-13", dateStr)
                dateStr = u"2009-02-13"

            t = time.strptime(dateStr, "%Y-%m-%d")
            y,m,d = t[0:3]
            curr_project.approved_date = datetime.date(y,m,d)

            project_list.append(curr_project)

        return project_list

        
    def get_post_data(self):
        post_data = {}
        d1,d2 = Batch.get_prepare_post_data()
        post_data['__EVENTTARGET'] = 'AspNetPager1'
        post_data['__EVENTARGUMENT'] = str(self.id)
        post_data['__VIEWSTATE'] = d1
        post_data['__VIEWSTATEENCRYPTED'] = ''
        post_data['__EVENTVALIDATION'] = d2
        return post_data

        
    @staticmethod
    def get_prepare_post_data():
        soup = request_html_soup('http://ris.szpl.gov.cn/bol/')

        inputTag = soup.find("input", id="__VIEWSTATE")
        inputTag2 = soup.find("input", id="__EVENTVALIDATION")
        return inputTag["value"],inputTag2["value"]


    @staticmethod
    def get_count():
        soup = request_html_soup('http://ris.szpl.gov.cn/bol/')
        divTag = soup.find("div", attrs={"class": "PageInfo"})
        bTags = divTag.findChildren(recursive=False)
        return int(bTags[2].get_text())


class Project():
    def __init__(self):
        self.id = 0
        self.name = ""
        self.company = ""
        self.region = ""
        self.approved_date = datetime.date(2000,01,01)
        self.data_sync_datetime = datetime.date(2000,01,01)

        
    def is_new(self):
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM house_project WHERE id=" + str(self.id))
        data = cursor.fetchone()
        cnt = int(cursor.rowcount)
        cursor.close()
        if 0 == cnt:
            return True
        else:
            return False

        
    def process_new(self):
        # insert into db for current project
        self.save_project()
        
        branch_list = self.get_branch_list()
        for branch in branch_list:
            branch.process_new()

        
    def get_branch_list(self):
        branch_list = []
        
        buildingList = self.get_building_list()
        for curr_building in buildingList:
            request_url = "http://ris.szpl.gov.cn/bol/building.aspx?id=" + str(curr_building.id)
            soup = request_html_soup(request_url)
            divTag = soup.find("div", id="divShowBranch")
            if 1==len(list(divTag.children)):
                logging.error('blank branch(building id:%d)' % curr_building.id)
                continue

            curr_branch = Branch()
            curr_branch.name = divTag.font.get_text()
            curr_branch.url = "building.aspx?id=" + str(curr_building.id)
            curr_branch.building_name = curr_building.name
            curr_branch.project_id = self.id
            branch_list.append(curr_branch)

            for aTag in divTag.find_all("a"):
                curr_branch = Branch()
                curr_branch.name = aTag.get_text()
                branch_url = aTag['href'].split("&")[1].split("=")[1]
                curr_branch.url = "building.aspx?id=" + str(curr_building.id) \
                    + "&Branch=" + branch_url + "&isBlock=ys"
                curr_branch.building_name = curr_building.name
                curr_branch.project_id = self.id
                branch_list.append(curr_branch)

        return branch_list

    def get_building_list(self):
        request_url = "http://ris.szpl.gov.cn/bol/projectdetail.aspx?id=" + str(self.id)
        soup = request_html_soup(request_url)

        building_list = []

        for trTag in soup.find_all("tr", attrs={"bgcolor": "#F5F9FC"}):
            tdTags = trTag.findChildren(recursive=False)
            currBuilding = Building() 
            currBuilding.id = int(tdTags[4].a['href'].split("=")[1])
            currBuilding.name = tdTags[1].get_text()
            building_list.append(currBuilding)

        return building_list
        
    def save_project(self):
        logging.info(self)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO house_project SET 
                          id=%s, 
                          name=%s,
                          company=%s, 
                          region=%s,
                          approved_date=%s""" ,
                          (str(self.id), self.name, self.company, \
                             self.region, \
                             self.approved_date.isoformat()))
        cursor.close()
        
    def process_old(self):
        today = datetime.date.today()
        # 对于已经入库的项目,只对两年内的新房更新房子状态
        DAY_DURATION = datetime.timedelta(days=2*365)
        if today - self.approved_date > DAY_DURATION:
            logging.debug("It's a old project(%s), skip" % str(self.approved_date))
            # 已经出现有超过两年的Project, 需要终止遍历其他Project, 本轮遍历所有Project结束
            return True
            
        branch_list = self.get_db_branch_list()
        for curr_branch in branch_list:
            md5, list_id_status = curr_branch.get_house_list()
            if md5==curr_branch.md5:
                logging.debug("house status of branch (%d) is not changed." % curr_branch.id)
                continue
            # MD5变了,说明有House状态有变化
            logging.debug("house status of branch (%d) is changed." % curr_branch.id)
            iCnt = House.update_house_status(list_id_status)
            if 0 != iCnt:
                logging.info("Update total %d house status for branch(%d)" % (iCnt, curr_branch.id))
            curr_branch.update_db_md5(md5)
        return False
                
    def get_db_branch_list(self):
        data = []
        cursor = conn.cursor()
        cursor.execute("SELECT id,url,md5 FROM house_branch WHERE project_id = " + str(self.id))

        branch_list = []
        for row in cursor.fetchall():
            curr_branch = Branch(row[0], row[1], row[2], self.id)
            branch_list.append(curr_branch)

        cursor.close()

        return branch_list
        
    def __str__(self):
        return u"[Project:%d|%s|%s|%s]" % (self.id, self.name, self.company, self.region)


class Building():
    def __init__(self):
        self.id = 0
        self.name = ""

    def __str__(self):
        return u"[Building:%d|%s]" % (self.id, self.name)

class Branch():
    def __init__(self, id=0, url="", md5="", project_id=0):
        self.id = id              # generate automatically
        self.name = ""
        self.url = url
        self.md5 = md5
        self.building_name = ""
        self.project_id = project_id
        
    def process_new(self):
        md5, list_id_status = self.get_house_list()
        self.md5 = md5
        self.id = self.save_branch()
        # insert into db for current branch
        for id,status in list_id_status:
            house = House(id, status, self.id)
            house.build_house()

        
    def get_house_list(self):
        request_url = "http://ris.szpl.gov.cn/bol/" + self.url
        soup = request_html_soup(request_url)

        list_id_status = []

        divTag = soup.find("div", id="divShowList")
        for trTag in divTag.findChildren(recursive=False):
            for tdTag in trTag.findChildren(recursive=False):
                currHouse = House()
                subDivTags = tdTag.findChildren("div", recursive=False)
                if 2==len(subDivTags):
                    id = int(subDivTags[1].a["href"].split("=")[1])
                    status = House.get_house_status(subDivTags[1].a.img["src"])
                    list_id_status.append((id, status,))

        return md5_hash(soup.get_text()),list_id_status
        
    def update_db_md5(self, md5):
        self.md5 = md5
        cursor = conn.cursor()
        cursor.execute("""
                        UPDATE house_branch 
                        SET md5=%s 
                        WHERE id=%s
                        """, (self.md5, str(self.id)))
        if 0 == int(cursor.rowcount):
            logging.error("update branch md5 error in database. branch id:%d" % (self.id))
        cursor.close()

    def save_branch(self):
        logging.debug(self)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO house_branch SET 
                          name=%s, 
                          url=%s, 
                          md5=%s, 
                          building_name=%s,
                          project_id=%s""" ,
                          (self.name, self.url, self.md5, self.building_name, str(self.project_id)))
        cursor.close()
        return conn.insert_id()

    def __str__(self):
        return u"[Branch:%d|%s|%s|%s]" % (self.id, self.name, self.url, self.building_name)

class House():
    def __init__(self, id=0, status=999, branch_id=1):
        self.id = id
        self.name = ""
        self.floor = ""
        self.size1 = 0
        self.size2 = 0
        self.size3 = 0
        self.price = None  # insert NULL in DB if neccessary
        self.type  = ""
        self.status = status
        self.branch_id = branch_id
        
    def build_house(self):
        self.fetch_house_detail()

        # write database
        self.save_house()
    
    def fetch_house_detail(self):
        request_url = "http://ris.szpl.gov.cn/bol/housedetail.aspx?id=" + str(self.id)
        soup = request_html_soup(request_url)

        trTags = soup.find_all("tr", attrs={"class": "a1"})
        tdTags = trTags[1].findChildren(recursive=False)
        s = tdTags[3].get_text(strip=True)
        s = u''.join(s.split())
        s = s[:len(s)-13]
        if s == u'--':
            self.price = None 
        else:
            self.price = Decimal(s)
        
        tdTags = trTags[2].findChildren(recursive=False)
        s = tdTags[1].get_text()
        self.floor = s[:len(s)-1]
        s = tdTags[3].get_text()
        self.name = s[:len(s)-1]

        # 类型
        s = tdTags[5].get_text()
        s = s[:len(s)-1]
        self.type = s
        
        tdTags = trTags[4].findChildren(recursive=False)
        
        s = tdTags[1].get_text()
        self.size1 = Decimal(s[:len(s)-3])
        s = tdTags[3].get_text()
        self.size2 = Decimal(s[:len(s)-3])
        s = tdTags[5].get_text()
        self.size3 = Decimal(s[:len(s)-3])
        
    def save_house(self):
        logging.debug(self)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO house_house SET 
                      id=%s, 
                      name=%s, 
                      floor=%s, 
                      size1=%s, 
                      size2=%s, 
                      size3=%s, 
                      price=%s,
                      type=%s, 
                      status=%s, 
                      branch_id=%s""" ,
                      (self.id, self.name, self.floor, \
                       self.size1, self.size2, self.size3, \
                       self.price, self.type, self.status, self.branch_id,))
        cursor.close()

    def __str__(self):
        return u"[House:%d|%s|%s|%s|%s|%s|%s|%s|%d|%d]" % (self.id, self.name, self.floor, \
                    str(self.size1), str(self.size2), str(self.size3), \
                    str(self.price), self.type, self.status, self.branch_id)

    @staticmethod
    def get_house_status(img_filename):
        status = 999
        if img_filename == "imc/b1_2.gif":
            status = 1
        elif img_filename == "imc/b3.gif":
            status = 2
        elif img_filename == "imc/b10.gif":
            status = 3
        elif img_filename == "imc/b2.gif":
            status = 4
        elif img_filename == "imc/b123.gif":
            status = 5
        elif img_filename == "imc/bz3_n.gif":
            status = 6
        elif img_filename == "imc/bz1.gif":
            status = 7
        else:
            logging.error("invalid status:%s" % img_filename)

        return status
        
    @staticmethod
    def update_house_status(list_id_status):
        cursor = conn.cursor()

        iCnt = 0
        for house_id,status in list_id_status:
            cursor.execute("""
                            UPDATE house_house 
                            SET status=%s 
                            WHERE id=%s""" 
                            % (str(status),  str(house_id)))
            iCurrCnt = int(cursor.rowcount)
            if 0 != iCurrCnt:
                logging.debug("update house(id:%d) status to (%d)" % (house_id, status))
            iCnt = iCnt + iCurrCnt
        cursor.close()

        return iCnt


def md5_hash(s):
    import hashlib
    m = hashlib.md5()   
    m.update(s)   
    return m.hexdigest()

def request_html_soup(url, method="GET", post_data={}):
    import urllib2
    import urllib

    tryCount = 0
    soup = None

    while tryCount <= 5:
        try:
            tryCount = tryCount + 1
            if method=="POST":
                response = urllib2.urlopen(url, urllib.urlencode(post_data))
            else:   # "GET"
                response = urllib2.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html, from_encoding="gbk")
        except urllib2.HTTPError,e:     # HTTPError must be before URLError
            logging.error("The server couldn't fulfill the request")
            logging.error("Error code: %s", e.code)
            logging.error("Return content:%s", e.read())
            if tryCount <= 5:
                logging.error("sleep 3 seconds, ant then try again.")
                import time
                time.sleep(3)
        except urllib2.URLError,e:
            logging.error("Failed to reach the server")
            logging.error("The reason:%s", e.reason)
            if tryCount <= 5:
                logging.error("sleep 3 seconds, ant then try again.")
                import time
                time.sleep(3)
        else:
            return soup
    else:
        logging.error("equest the url(%s) fail." % url)



class ProjectSummary():
    def __init__(self):
        self.type = ""
        self.min_size = 0
        self.max_size = 0
        self.min_price = None
        self.max_price = None
        self.avg_price = None
        self.sample_count = 0
        self.total_count = 0
        self.project_id = 0
        
    def __str__(self):
        return u"[ProjectSummary:%s|%s|%s|%s|%s|%s|%d|%d|%d]" % (self.type, str(self.min_size), \
            str(self.max_size), str(self.min_price), str(self.max_price), str(self.avg_price), \
            self.sample_count, self.total_count, self.project_id)
        
class BranchSummary():
    def __init__(self):
        self.type = ""
        self.min_size = 0
        self.max_size = 0
        self.min_price = None
        self.max_price = None
        self.avg_price = None
        self.sample_count = 0
        self.total_count = 0
        self.branch_id = 0
        
    def __str__(self):
        return u"[BranchSummary:%s|%s|%s|%s|%s|%s|%d|%d|%d]" % (self.type, str(self.min_size), \
            str(self.max_size), str(self.min_price), str(self.max_price), str(self.avg_price), \
            self.sample_count, self.total_count, self.branch_id)


def analyse_data(project_id):
    analyse_project_summary(project_id)
    analyse_branch_summary(project_id)

def analyse_project_summary(project_id):
    dict_project_summary = {}
    cursor = conn.cursor()
    sql = """SELECT type,MIN(size1),MAX(size1),COUNT(1)
             FROM house_house
             WHERE branch_id IN(SELECT id FROM house_branch WHERE project_id = '%d') 
             GROUP BY type""" % (project_id)
    cursor.execute(sql)
    results = cursor.fetchall()
    # 获取所有记录列表 results = cursor.fetchall()
    for row in results:
        project_summary = ProjectSummary()
        project_summary.type = row[0]
        project_summary.min_size = row[1]
        project_summary.max_size = row[2]
        project_summary.total_count = row[3]
        project_summary.project_id = project_id
        dict_project_summary[row[0]] = project_summary

    cursor.close()
        
    sql = """SELECT type,MIN(price),MAX(price),ROUND(AVG(price)),COUNT(1)
             FROM house_house
             WHERE branch_id IN(SELECT id FROM house_branch WHERE project_id = '%d') 
                AND price IS NOT NULL 
             GROUP BY type""" % (project_id)
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        project_summary = dict_project_summary[row[0]]
        project_summary.min_price = row[1]
        project_summary.max_price = row[2]
        project_summary.avg_price = row[3]
        project_summary.sample_count = row[4]
    
    cursor.close()
    save_project_summary(dict_project_summary)

def analyse_branch_summary(project_id):
    branch_id_list = get_branch_id_list(project_id)
    for branch_id in branch_id_list:
        dict_branch_summary = {}
        cursor = conn.cursor()
        sql = """SELECT type,MIN(size1),MAX(size1),COUNT(1)
                 FROM house_house
                 WHERE branch_id = '%d' 
                 GROUP BY type""" % (branch_id)
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            branch_summary = BranchSummary()
            branch_summary.type = row[0]
            branch_summary.min_size = row[1]
            branch_summary.max_size = row[2]
            branch_summary.total_count = row[3]
            branch_summary.branch_id = branch_id
            dict_branch_summary[row[0]] = branch_summary
            
        cursor.close()

        sql = """SELECT type,MIN(price),MAX(price),ROUND(AVG(price)),COUNT(1)
                 FROM house_house
                 WHERE branch_id = '%d' AND price IS NOT NULL 
                 GROUP BY type""" % (branch_id)
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            branch_summary = dict_branch_summary[row[0]]
            branch_summary.min_price = row[1]
            branch_summary.max_price = row[2]
            branch_summary.avg_price = row[3]
            branch_summary.sample_count = row[4]
        
        cursor.close()
        save_branch_summary(dict_branch_summary)

def save_project_summary(dict_project_summary):
    for i in dict_project_summary:
        project_summary = dict_project_summary[i]
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO house_projectsummary SET 
                  type=%s, 
                  min_size=%s, 
                  max_size=%s, 
                  min_price=%s, 
                  max_price=%s, 
                  avg_price=%s, 
                  sample_count=%s,
                  total_count=%s, 
                  project_id=%s""",
                  (project_summary.type, project_summary.min_size, \
                   project_summary.max_size, project_summary.min_price,  \
                   project_summary.max_price, project_summary.avg_price, \
                   project_summary.sample_count, project_summary.total_count, \
                   project_summary.project_id,))

        cursor.close()
        logging.info("[project_summary]:%s" % project_summary)

def save_branch_summary(dict_branch_summary):
    for i in dict_branch_summary:
        branch_summary = dict_branch_summary[i]
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO house_branchsummary SET 
                  type=%s, 
                  min_size=%s, 
                  max_size=%s, 
                  min_price=%s, 
                  max_price=%s, 
                  avg_price=%s, 
                  sample_count=%s,
                  total_count=%s, 
                  branch_id=%s""" ,
                  (branch_summary.type, branch_summary.min_size, \
                   branch_summary.max_size, branch_summary.min_price,  \
                   branch_summary.max_price, branch_summary.avg_price, \
                   branch_summary.sample_count, branch_summary.total_count, \
                   branch_summary.branch_id,))
        cursor.close()
        logging.info("[branch_summary]:%s" % branch_summary)
            
def get_branch_id_list(project_id):
    branch_id_list = []
    cursor = conn.cursor()
    sql = "SELECT id FROM house_branch \
       WHERE project_id = '%d'" % (project_id)
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        branch_id = row[0]
        branch_id_list.append(branch_id)
    cursor.close()
    return branch_id_list

def update_system_status():
    cursor = conn.cursor()
    cursor.execute("""
                    UPDATE house_systemstatus 
                    SET last_update=CURDATE()
                    """)
    if 1 == int(cursor.rowcount):
        logging.debug("Update system status successfully")
    cursor.close()


def init_sys():

    # 设置默认编码格式
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')  # 如gb2312,gbk
    #print sys.getdefaultencoding() # 输出当前编码

    # 初始化loggin
    logging.config.fileConfig('LemonHouseSpiderLogging.conf')
    logging.debug("=====================================================================================");
    logging.debug("=====================================================================================");
    logging.debug("Start program.................... ");

def loop_run():
    BATCH_COUNT = Batch.get_count()
    is_reach_history_project = False

    for i in range(1, BATCH_COUNT):
        currBatch = Batch(i)
        logging.debug("start project batch [%d/%d]" % (currBatch.id, BATCH_COUNT))
        project_list = currBatch.get_project_list()
        for currProject in project_list:
            try:
                is_new_project = currProject.is_new()
                if is_new_project:
                    logging.debug("start project(%s). It's a new project." % currProject.name)
                    currProject.process_new()
                    analyse_data(currProject.id)
                else: # end of is_new_project
                    logging.debug("start project(%s). It's a old project." % currProject.name)
                    is_reach_history_project = currProject.process_old()
                    if is_reach_history_project:
                        break
            # 含AttributeError，KeyError， UnicodeEncodeError
            except AttributeError:
                conn.rollback()
                logging.error("process project(%s) fail. Attribute Error" % currProject.name)
            except KeyError:
                conn.rollback()
                logging.error("process project(%s) fail. Key Error" % currProject.name)
            except Exception, e:
                conn.rollback()
                logging.error(e)
                logging.error("process project(%s) fail. skip this project" % currProject.name)
                continue
            else:
                # 每成功处理一个Project,提交一次数据库
                conn.commit()
            finally:
                pass

        if is_reach_history_project:
            update_system_status()
            logging.info("reach history project, finish project loop")
            break


if __name__ == '__main__':
    
    init_sys()

    while True:
        try:
            loop_run()
        except MySQLdb.Error, e:
            # 保证数据完整性. 
            conn.rollback()
            conn.close()
            logging.error("error code:%d, %s" % (e.args[0], e.args[1]))
            import sys
            sys.exit(1)
        logging.info("finish current project loop, sleep 30 min")
        import time
        time.sleep(1800)

    logging.error("exit program normally.")

