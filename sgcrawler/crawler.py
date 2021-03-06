#coding:utf-8
import sys, gc
reload(sys)
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
try:
    from urllib.request import urlopen  #python3
except ImportError:
    from urllib2 import urlopen, quote , HTTPError #python2

# office
# style_name
# dates
# native_place
# history_dpt
# novel_dpt
# assessment

class Crawler(object):
    url = 'http://www.e3ol.com/biography/html/'
    encoding = 'GB2312'
    errorList = []

    def __init__(self, name):
        self.name = name
        self.has_error = False
        self.get_soup()

    def handle_error(self):
        error_text = '[%s]-这个人抓不到' % self.name
        self.has_error = True
        self.assessment = self.novel_dpt = self.history_dpt = self.native_place  = self.style_name = self.office = ''
        Crawler.errorList.append(error_text)

    def get_soup(self):
        self.url = Crawler.url + quote(self.name)
        try:
            conn = urlopen(self.url)
            self.data  = conn.read()
            self.data = self.data.decode(Crawler.encoding, 'ignore')
            self.soup = BeautifulSoup(self.data, 'lxml')
            # self.soup = BeautifulSoup(self.data, 'html5lib')
            conn.close()
        except:
            self.handle_error()
            # print 'error'

    def test_soup(self):
        print self.soup.prettify()

    def crawl_tag1(self):
        """分析tag1，得到style_name（字）,native_place（籍贯）,dates（生卒）--暂时不用,office（官职）

        得到的raw_texts如:
            姓名：郭嘉 字：奉孝 生卒：170-207(38岁)
            籍贯：豫州颍川郡阳翟(河南许昌市禹州)
            容貌：暂无相关记载
            官至：
            司空军祭酒
            洧阳亭侯
            谥曰贞侯
        """
        if not self.has_error:
            tags = self.soup.select('.view_ziliao')
            if len(tags) == 0:
                self.handle_error()
                return 1
            tag1 = self.soup.select('.view_ziliao')[0]
            ps = tag1.find_all('p')
            raw_texts = list(tag1.stripped_strings)
            line1_texts = raw_texts[0].split(' ')

            #获得　style_name 字:
            raw_style_name = line1_texts[1] #字：奉孝
            if raw_style_name == u'字：未知':
                self.style_name = ''
            else:
                style_name_start = raw_style_name.find('字') + 2
                self.style_name = raw_style_name[style_name_start:].strip()

            #获得　dates 生卒:
            # if line1_texts[2].find('虚构') != -1 or line1_texts[2].count('？') == 2:
            #     self.dates = ''
            # else:
            #     raw_dates  = line1_texts[2] #生卒：170-207(38岁)
            #     dates_start = raw_dates.find('卒') + 2
            #     self.dates = raw_dates[dates_start:].strip()

            #获得 native_place 籍贯
            if raw_texts[1].find('暂无')  != -1:
                self.native_place = ''
            else:
                native_place_start = raw_texts[1].find('贯') + 2
                self.native_place = raw_texts[1][native_place_start:].strip()

            #获得 office  官职
            self.office = ' '.join(raw_texts[4:]).strip()
            del tags
            #end def crawl_tag1


    def crawl_novel_dpt(self):
        """
            获取三国演义简介
        """
        if not self.has_error:
            tags = self.soup.select('#Out1')
            if len(tags) == 0:
                self.novel_dpt = ''
            else:
                spans = tags[0].find_all('span')
                novel_dpt = ''
                texts = spans.pop().stripped_strings
                for text in texts:
                    novel_dpt += text
                self.novel_dpt = unicode(novel_dpt)
            del tags

    def crawl_history_dpt(self):
        """
            获取历史简介
        """
        if not self.has_error:
            tags = self.soup.select("#Out2")
            if len(tags) == 0:
                self.history_dpt = ''
            else:
                history_dpt = ''
                for text in tags[0].stripped_strings:
                    history_dpt += (text + '  ')
                history_dpt =  unicode(history_dpt)
                if history_dpt.startswith('暂无'):
                    self.history_dpt = ''
                else:
                    self.history_dpt = history_dpt
            del tags


    def crawl_assessment(self):
        """
            获取历史评价
        """
        if not self.has_error:
            tags = self.soup.select("#Out3")
            if len(tags) == 0:
                self.assessment = ''
            else:
                strings = tags[0].stripped_strings
                texts = list(strings)
                if len(texts) == 0:
                    self.assessment = ''
                    return 1
                if unicode(texts[0]).startswith('暂无'):
                    self.assessment = ''
                else:
                    self.assessment = '##'.join(texts).replace('◆', '') # '##'分割每个人的评价
            del tags

    def crawl_all(self):
        if self.has_error == False:
            # print 'Handle the person----%s' % self.name
            self.crawl_tag1()
            self.crawl_history_dpt()
            self.crawl_novel_dpt()
            self.crawl_assessment()
            del self.soup

    def get_profile(self):
        if self.has_error == False:
            return (self.style_name, self.native_place, self.history_dpt, self.novel_dpt, self.assessment, self.office)
        else:
            return ('', '', '', '', '', '')

if __name__ == '__main__':
    name = '夏侯霸' #曹丕 王越 赵云　貂蝉　司马懿  华雄 曹操 奥巴马 桥玄 黄承彦 祢衡 司马徽 许劭 管辂 夏侯霸
    crawler = Crawler(name)
    crawler.crawl_tag1()
    crawler.crawl_all()
    # print crawler.get_profile()
    # print Crawler.errorList[0]
    print 'name is ', crawler.name
    print 'native place is ',crawler.native_place
    print '##'
    print crawler.history_dpt
    print '##'
    print crawler.novel_dpt
    print '##'
    print crawler.assessment

