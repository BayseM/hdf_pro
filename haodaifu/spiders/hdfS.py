# -*- coding: utf-8 -*-
import scrapy, re
from selenium import webdriver
from haodaifu.items import Hos_info_Item, Doc_info_Item, Vote_info_Item, Art_info_Item, Inq_info_Item


class HdfsSpider(scrapy.Spider):
    name = 'hdfS'
    start_urls = ['https://www.haodf.com/jibing/yixianai.htm']
    handle_httpstatus_list = [521]

    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        # 获取胰腺癌全部推荐医院 每一页的链接  共13页
        target_url_list = ['https:' + response.xpath('//body/div[4]/div[2]/div[1]/div[3]/div[1]/a[1]/@href').get()[
                                      :55] + f'{i + 1}.htm' for i in range(13)]
        # print(target_url_list)
        # print(len(target_url_list))     # 13
        # 遍历列表 获取每一页的链接
        for target_url in target_url_list:
            yield scrapy.Request(url=target_url, dont_filter=True, callback=self.first)

    def first(self, response):
        # 第一层：该疾病的全国所有医院
        hosps = response.xpath('//tr[@class="con_list"]')
        # print(hosps)
        for hosp in hosps:
            # 医院名称
            hosp_name = hosp.xpath('./td[@class="td_link"]/a/p[@class="pl15"]/text()').get()
            # 医院所在城市
            city = hosp.xpath('./td[2]/text()').get()
            # 医院分级
            level = hosp.xpath('./td[3]/text()').get()
            # 好评大夫的数量
            dr_num = hosp.xpath('.//a[@class="num"]/text()').get()
            # # 得票数
            # hos_vote_num = hosp.xpath("./td[5]/span[@class='num']/a[@class='num']/text()").get()
            # 医院详情页链接
            hosp_url = 'https:' + hosp.xpath('./td[@class="td_link"]/a/@href').get()

            # print(hosp_name, city, level, dr_num, vote, hosp_url)

            yield scrapy.Request(url=hosp_url, dont_filter=True, callback=self.second,
                                 meta={'url_prefix': hosp_url, 'hos_name': hosp_name, 'city': city, 'level': level,
                                       'good_doc_num': dr_num})

    def second(self, response):

        url_prefix = response.meta["url_prefix"]
        hos_name = response.meta['hos_name']
        city = response.meta['city']
        level = response.meta['level']
        good_doc_num = response.meta['good_doc_num']
        # hos_vote_num = response.meta['hos_vote_num']

        # 第二层：每一家医院的好评汇总中的信息
        fav_info = response.xpath("//table[@class='ysjs']")
        for fav in fav_info:
            # 好评率
            fav_vate = (re.sub('\s', '', fav.xpath('.//tr[2]/td[2]/text()').get())).split(':')[1].replace('%', '')
            # 推荐专家人数
            rec_expert_num = ''.join(re.findall('\d', fav.xpath('.//tr[3]/td[2]/text()').get()))
            # print(fav_vate, rec_expert_num)

            item = Hos_info_Item()
            item['hos_name'] = hos_name
            item['city'] = city
            item['level'] = level
            item['good_doc_num'] = int(good_doc_num)
            # item['hos_vote_num'] = int(hos_vote_num)

            item['hos_fav_rate'] = round(float(fav_vate), 1)
            item['rec_specialist_num'] = int(rec_expert_num)
            yield item

        # 获取每个医院的大夫信息页面的总页码
        total_page = response.xpath("//div[@class='p_bar']/a[@class='p_text'][1]/text()").get()

        # 获取大夫信息页面的每一页的链接：
        # 如果医院详情页只有一页,则直接用当前详情页的链接
        if total_page == None:
            page_url_list = [url_prefix]
        # 多页时：
        else:
            # 获取页面分页器中的'共 x 页’中的页码(总页码)
            total_page_num = int(
                ''.join(re.findall('\d', response.xpath("//div[@class='p_bar']/a[@class='p_text'][1]/text()").get())))

            page_url_list = [
                # 获取到当前页面中分页器里第二页的url链接,裁剪掉页码,并拼接遍历 总页码
                url_prefix + response.xpath("//div[@class='p_bar']/a[@class='p_num'][1]/@href").get()[:-1] + f'{p + 1}'
                for p in range(total_page_num)]

        # print(page_url_list)

        for doc_page_url in page_url_list:
            yield scrapy.Request(url=doc_page_url, dont_filter=True, callback=self.third, meta={'hos_name': hos_name})

    def third(self, response):
        hos_name = response.meta['hos_name']
        # 第三层：获取该医院下的所有大夫信息
        drs = response.xpath("//tr[@class='yy_jb_df2']")
        # print(drs)    # 有些医院暂时一个医生都没,所以需要判断
        if drs != []:
            doctors = drs

            for doc in doctors:
                # 医生名字
                doc_name = doc.xpath(".//a[@class='blue']/text()").get()
                # 医生详情页链接
                doc_detail_url = doc.xpath(".//a[@class='blue']/@href").get()

                doc_vote_url = doc_detail_url + 'doctor/commentlist'

                # 医生职称需要把职称1和职称2合在一起，以便储存
                # 医生职称1
                doc_r1 = doc.xpath(".//table[@class='yy_jb_df3']/tr[2]/td[2]/text()").get()
                if doc_r1 == None:
                    doc_rank1 = ''
                else:
                    doc_rank1 = doc_r1
                # 医生职称2
                doc_r2 = doc.xpath(".//table[@class='yy_jb_df3']/tr[3]/td[2]/text()").get()

                if doc_r2 == None:
                    doc_rank2 = ''
                else:
                    doc_rank2 = doc_r2

                doc_rank = ''.join(doc_rank1) + ',' + ''.join(doc_rank2)

                # 医生科室      有的医生没有科室
                department = doc.xpath(".//table[@class='yy_jb_df3']/tbody/tr[4]/td[2]/a/text()").get()

                # 医生评分 例：4.1
                sc = doc.xpath(".//i[@class='bigblue']/text()").get()
                if sc != None:
                    score = round(float(sc), 1)
                else:
                    score = 0

                # 医生票数
                doc_vote = doc.xpath("./td[@class='va_center']/p/text()").get()
                if doc_vote != None:
                    # 2年内得票数
                    vote_num_2year = int(re.findall(r"2年内(.*?)票", doc_vote)[0])
                    # 总票数
                    vote_num_total = int(re.findall(r"总(.*?)票", doc_vote)[0])
                else:
                    vote_num_2year = 0
                    vote_num_total = 0

                # 擅长
                skill = doc.xpath("./td[3]/span/text()").get()

                # 包含问诊费用的li     待做判断处理 有的长度为0，有的为1，有的为2
                price_li = len(doc.xpath(".//ul[@class='yy_jb_df']/li"))
                # 图文问诊和电话问诊需要取出其中的具体数字：
                # 图文问诊费用
                price_pic = doc.xpath(".//ul[@class='yy_jb_df']/li[1]/a[@class='product-text']/text()").get()
                # 电话问诊费用
                price_phone = doc.xpath(".//ul[@class='yy_jb_df']/li[2]//a[@class='product-text']/text()").get()

                # print(doc_name,doc_info_url,doc_rank1,doc_rank2,department,score,vote_num_2year,vote_num_total)
                # print(doc_name,price_pic,price_phone,price_li)

                yield scrapy.Request(url=doc_vote_url, dont_filter=True, callback=self.fourth,
                                     meta={'hos_name': hos_name, 'doc_name': doc_name,
                                           'doc_rank': doc_rank, 'department': department, 'score': score,
                                           'vote_num_2year': vote_num_2year, 'vote_num_total': vote_num_total,
                                           'skill': skill, 'price_pic': price_pic, 'price_phone': price_phone})

    def fourth(self, response):
        hos_name = response.meta['hos_name']
        doc_name = response.meta['doc_name']
        doc_rank = response.meta['doc_rank']
        department = response.meta['department']
        score = response.meta['score']
        vote_num_2year = response.meta['vote_num_2year']
        vote_num_total = response.meta['vote_num_total']
        display = response.meta['skill']
        price_pic = response.meta['price_pic']
        price_phone = response.meta['price_phone']

        # 医生的患者投票页面：
        # 医生全部投票数
        all_vote = response.xpath("//span[@class='vote-total-num']/text()").get()
        # print(all_vote)

        # 医生主页链接(获取患者对医生的两个满意度)
        doc_index_url = 'https:' + response.xpath(
            "//div[4]/div[@class='second-page-tabs']/a[@class='tab-item first']/@href").get()
        # print(doc_index_url)

        yield scrapy.Request(url=doc_index_url, dont_filter=True, callback=self.fifth,
                             meta={'vote_by_patient': all_vote, 'hos_name': hos_name, 'doc_name': doc_name,
                                   'doc_rank': doc_rank, 'department': department, 'score': score,
                                   'vote_num_2year': vote_num_2year, 'vote_num_total': vote_num_total,
                                   'display': display, 'price_pic': price_pic, 'price_phone': price_phone})

        # 患者投票信息分页：
        # 患者投票信息下的 '共 x 页'  有些网页为None
        tp = response.xpath("//a[@class='p_text']/text()").get()

        # 需要将此列表往下传递，然后编写一层用于获取所有页的投票信息
        url_list = []  # 列表中存放所有分页链接
        if tp != None:
            # 患者投票信息下的 '共 x 页' 中的页码
            total_page_num = int(''.join(re.findall('\d', tp)))

            for t in range(total_page_num):
                '''
                        response.url:
                              例: https://www.haodf.com/jingyan/all-wulili-11.htm?id=
                        分页url:
                                  https://www.haodf.com/jingyan/all-wulili-11/2.htm
                                  https://www.haodf.com/jingyan/all-wulili-11/10.htm
                '''
                eve_page_url = response.url[:-8] + '/' + f'{t + 1}.htm'
                url_list.append(eve_page_url)

        else:
            eve_page_url = response.url
            url_list.append(eve_page_url)

        # print(url_list)

        for vote_page_url in url_list:
            yield scrapy.Request(url=vote_page_url, dont_filter=True, callback=self.sixth,
                                 meta={'hos_name': hos_name, 'doc_name': doc_name})

        # 医生科普文章页：
        doc_au = response.xpath("//div[4]/div[@class='second-page-tabs']/a[contains(text(),'科普文章')]/@href").get()
        if doc_au != None:
            doc_art_url = 'https:' + doc_au
            yield scrapy.Request(url=doc_art_url, dont_filter=True, callback=self.seventh, meta={'hos_name': hos_name, 'doc_name': doc_name})

        # 医生患者问诊页：
        doc_inq = response.xpath("//div[4]/div[@class='second-page-tabs']/a[contains(text(),'患者问诊')]/@href").get()
        # print(doc_inq)
        if doc_inq != None:
            doc_inq_url = 'https:' + doc_inq
            # print(doc_inq_url)
            yield scrapy.Request(url=doc_inq_url, dont_filter=True, callback=self.ninth,
                                 meta={'hos_name': hos_name, 'doc_name': doc_name})

    def fifth(self, response):
        # pass
        hos_name = response.meta['hos_name']
        doc_name = response.meta['doc_name']
        doc_rank = response.meta['doc_rank']
        department = response.meta['department']
        score = response.meta['score']
        vote_num_2year = response.meta['vote_num_2year']
        vote_num_total = response.meta['vote_num_total']
        display = response.meta['display']
        price_pic = response.meta['price_pic']
        price_phone = response.meta['price_phone']
        vote_by_patient = response.meta['vote_by_patient']

        # 获取各个医生主页的满意度：

        satis_info = response.xpath("//div[@class='satisfaction clearfix']")
        # print(satis_info)
        for satis in satis_info:
            # 疗效满意度
            efs = satis.xpath("./div[@class='satis-item'][1]/i[@class='sta-num']/text()").get()
            if efs != None:
                efficacy_satisfaction = int(efs)
            else:
                efficacy_satisfaction = 0

            # 态度满意度
            ats = satis.xpath("./div[@class='satis-item'][2]/i[@class='sta-num']/text()").get()
            if efs != None:
                attitude_satisfaction = int(ats)
            else:
                attitude_satisfaction = 0

            # print(efficacy_satisfaction, attitude_satisfaction)

            item = Doc_info_Item()
            item['hos_name'] = hos_name
            item['doc_name'] = doc_name
            item['doc_rank'] = doc_rank
            item['department'] = department
            item['score'] = score
            item['vote_num_2year'] = vote_num_2year
            item['vote_num_total'] = vote_num_total
            item['display'] = display
            item['price_pic'] = price_pic
            item['price_phone'] = price_phone
            item['vote_by_patient'] = vote_by_patient

            item['efficacy_satisfaction'] = efficacy_satisfaction
            item['attitude_satisfaction'] = attitude_satisfaction

            yield item

    def sixth(self, response):
        hos_name = response.meta['hos_name']
        doc_name = response.meta['doc_name']

        # 获取医生的患者投票所有分页下的信息：

        vote_info = response.xpath("//div[@class='patient-eva']")  # 包含所有投票信息的div
        # print(vote_info)
        for vi in vote_info:

            # 患者姓名
            patient_name = vi.xpath(".//span[@class='patient-name']/text()").get()
            # 疾病名称
            illness_name = vi.xpath(".//span[@class='disease-tag']/text()").get()
            # 看病目的
            purpose = vi.xpath(".//span[@class='patient-sumary-item'][1]/text()").get()
            # 治疗方式
            therapy_method = vi.xpath(".//span[@class='patient-sumary-item'][2]/text()").get()
            # 疗效满意度
            efficacy_satisfaction = vi.xpath(".//span[@class='patient-sumary-item'][3]/text()").get()
            # 态度满意度
            attitude_satisfaction = vi.xpath(".//span[@class='patient-sumary-item'][4]/text()").get()

            # 门诊花费
            ct = vi.xpath(".//span[@class='patient-sumary-item'][5]/text()").get()
            if ct == None:
                cost = '空'
            else:
                cost = ct
            # 目前疾病状态
            st = vi.xpath(".//span[@class='patient-sumary-item'][6]/text()").get()
            if st == None:
                state = '空'
            else:
                state = st

            # 选择医生理由
            rea = vi.xpath(".//span[@class='patient-sumary-item'][7]/text()").get()
            if rea == None:
                reason = '空'
            else:
                reason = rea

            # print(doc_name, patient_name, illness_name, purpose, therapy_method, efficacy_satisfaction, attitude_satisfaction, cost, state, reason)

            # 评价标签
            ct_list = [ct.get() for ct in vi.xpath(".//div[@class='trait']/text()")]
            if len(ct_list) == 0:
                comment_tag = '无'
            else:
                comment_tag = ','.join(ct_list)

            # 评论内容
            comment_content = re.sub('\s', '', vi.xpath("./div[@class='eva-detail']/text()").get())
            # 发布时间
            date = re.sub('\s', '', vi.xpath(".//div[@class='evaluate-date']/text()").get())

            # print(doc_name, patient_name, comment_tag, comment_content, date)

            item = Vote_info_Item()
            item['hos_name'] = hos_name
            item['doc_name'] = doc_name
            item['patient_name'] = patient_name
            item['illness_name'] = illness_name
            item['purpose'] = purpose
            item['therapy_method'] = therapy_method
            item['efficacy_satisfaction'] = efficacy_satisfaction
            item['attitude_satisfaction'] = attitude_satisfaction
            item['cost'] = cost
            item['state'] = state
            item['reason'] = reason
            item['comment_tag'] = comment_tag
            item['comment_content'] = comment_content
            item['date'] = date
            yield item

    def seventh(self, response):
        hos_name = response.meta['hos_name']
        doc_name = response.meta['doc_name']

        # 获取医生科普文章页下的分页链接、总页码
        # tp 为总页码,如果tp为None 则表示只有一页
        tp = response.xpath("//a[@class='page_turn_a'][5]/text()").get()

        # print(tp)
        url_list = []  # 列表中存放所有分页链接

        if tp != None:
            # 患者投票信息下的 '共 x 页' 中的页码
            total_page_num = int(''.join(re.findall('\d', tp)))
            # print(total_page_num)
            for t in range(total_page_num):
                '''
                        response.url:
                              例: https://maxuezhen.haodf.com/lanmu
                        分页url:
                                  https://maxuezhen.haodf.com/lanmu_2
                                  https://maxuezhen.haodf.com/lanmu_19
                '''
                eve_page_url = response.url + '_' + f'{t + 1}'
                url_list.append(eve_page_url)

        else:
            eve_page_url = response.url
            url_list.append(eve_page_url)
        # print(url_list)
        for art_page_url in url_list:
            yield scrapy.Request(url=art_page_url, dont_filter=True, callback=self.eighth,
                                 meta={'hos_name': hos_name, 'doc_name': doc_name})

    def eighth(self, response):
        hos_name = response.meta['hos_name']
        doc_name = response.meta['doc_name']

        # 获取医生科普文章所有分页下的数据

        # 判断医生有没有发表文章,没有发表过文章的医生文章页会有此 span
        not_art = response.xpath("//span[@class='s_hint']/text()").get()
        # print(not_art)

        # 结果为 None 就是说明医生有文章
        if not_art == None:

            # 获取文章页信息
            all_art_list = response.xpath("//ul[@class='article_ul']/li/div[@class='clearfix']")
            '''
                article_type	string	文章分类
                article_title	string	文章标题
                article_url	string	文章链接
                comment_num	int	评价数量
                pageview	int	阅读数量
                date	string	发布时间

            '''
            # at_list = []
            for da in all_art_list:
                # 文章分类
                # 当文章类型为[引用文章]时,a标签下的为font
                at = da.xpath(".//a[@class='pr5 art_cate']/text()").get()
                # print(at)
                # 当文章类型不是[引用文章]时
                if at != None:
                    article_type = ((re.sub('\s','',at)).replace('[','')).replace(']','')
                    # print(article_type)

                    # 文章标题
                    article_title = da.xpath('.//a[2]/text()').get()

                    # 文章链接
                    article_url = da.xpath('.//a[2]/@href').get()
                    # print(article_title, article_url)

                    # 评价数量
                    cn = da.xpath(".//span[@class='gray1 ml5']/text()").get()
                    if cn != None:
                        #
                        comment_num = int(''.join(re.findall('\d', re.sub('\s','',cn))))

                    else:
                        comment_num = 0

                    # print(article_title, comment_num)

                    # 阅读数量
                    pageview = int((re.sub('\s', '', da.xpath("./p[@class='read_article']/span[@class='gray1'][1]/text()").get())).split('人')[0])
                    # print(article_title, pageview)

                    # 发布时间
                    date = (re.sub('\s', '', da.xpath(".//span[@class='gray1'][2]/text()").get())).split('于')[-1]
                    # print(article_title, date)

                    item = Art_info_Item()
                    item['hos_name'] = hos_name
                    item['doc_name'] = doc_name
                    item['article_type'] = article_type
                    item['article_title'] = article_title
                    item['article_url'] = article_url
                    item['comment_num'] = comment_num
                    item['pageview'] = pageview
                    item['date'] = date

                    yield item

    def ninth(self, response):
        hos_name = response.meta['hos_name']
        doc_name = response.meta['doc_name']

        # 获取医生患者问诊页码和分页链接:

        # tp 为总页码,如果tp为None 则表示只有一页
        tp = response.xpath("//a[@class='page_turn_a'][5]/text()").get()

        # print(tp)
        url_list = []  # 列表中存放所有分页链接

        if tp != None:  # 则为多页
            total_page_num = int(tp)
            # print(total_page_num)
            for t in range(total_page_num):
                '''
                        response.url:
                              例: https://linyaruo.haodf.com/thread/index
                        分页url:
                                  https://linyaruo.haodf.com/thread/index?p_type=all&p=2
                                  https://linyaruo.haodf.com/thread/index?p_type=all&p=24
                '''
                eve_page_url = response.url + '?p_type=all&p=' + f'{t + 1}'
                url_list.append(eve_page_url)

        else:
            eve_page_url = response.url
            url_list.append(eve_page_url)
        # print(url_list)

        for inq_page_url in url_list:
            yield scrapy.Request(url=inq_page_url, dont_filter=True, callback=self.tenth,
                                 meta={'hos_name': hos_name, 'doc_name': doc_name})

    def tenth(self, response):
        hos_name = response.meta['hos_name']
        doc_name = response.meta['doc_name']

        # 获取医生所有分页下的 问诊信息 及 每条问诊信息的链接

        # 包含所有问诊信息的tr
        # 第一个tr里面是标题,所以需要切掉
        doc_inqs = response.xpath("//div[@class='zixun_list']/table//tr")[1:]
        # print(inqs)
        if doc_inqs != []:
            for di in doc_inqs:
                # 患者名字
                patient_name = di.xpath(".//td[2]/p/text()").get()

                # 问诊标题
                tit = di.xpath(".//a[@class='td_link']/text()").get()
                if tit != None:
                    title = tit
                else:
                    title = '无'
                # print(title)

                # 每条问诊信息的链接   需要传递给下一级
                eve_inq_url = di.xpath(".//a[@class='td_link']/@href").get()
                # print(title, eve_inq_url)

                # 相关疾病名字
                illness_name = di.xpath(".//a[@class='rela_dis']/text()").get()
                # print(title, illness_name)

                # 对话数
                dialogue_num = (re.sub('\s', '', di.xpath("./td[5]").get()).replace('<fontclass="green3pl5pr5">',
                                                                                    '')).replace('</font>', '')[4:-5]
                # print(title, dialogue_num)

                # 最后发表时间
                last_date = di.xpath(".//span[@class='gray3']/text()").get()
                # print(title, last_date)

                yield scrapy.Request(url=eve_inq_url, dont_filter=True, callback=self.eleventh,
                                     meta={'hos_name': hos_name, 'doc_name': doc_name, 'patient_name': patient_name,
                                           'title': title, 'illness_name': illness_name, 'dialogue_num': dialogue_num,
                                           'last_date': last_date})

    def eleventh(self, response):
        hos_name = response.meta['hos_name']
        doc_name = response.meta['doc_name']

        patient_name = response.meta['patient_name']
        title = response.meta['title']
        illness_name = response.meta['illness_name']
        dialogue_num = response.meta['dialogue_num']
        last_date = response.meta['last_date']

        '''
            sick_time	string	患病时间
            visited_department	string	已就诊科室
            allergic_history	string	过敏史

        '''

        last_date1 = ((response.xpath("//h2[@class='bccard-title']/text()").get()).split('患')[0]).split('：')[-1]
        # print(last_date1)
        ill_dis = response.xpath("//section[2]/section[1]/section[1]/div[1]/section[1]/section[1]/div[1]/div[1]/div[contains(text(),'疾病描述')]")
        # print(illness_display)
        if ill_dis != []:
            # 疾病描述
            illness_display = response.xpath("//section[2]/section[1]/section[1]/div[1]/section[1]/section[1]/div[1]/div[1]/div[2]/p[1]/text()").get()
            # 具体疾病
            illness_content = response.xpath("//section[2]/section[1]/section[1]/div[1]/section[1]/section[1]/div[1]/div[2]/div[2]/p[1]/text()").get()
            hfh = response.xpath("//section[2]/section[1]/section[1]/div[1]/section[1]/section[1]/div[1]/div[3]/div[2]/p[1]/text()").get()
            # 希望得到的帮助
            if hfh == None:
                hope_for_help = '无'
            else:
                hope_for_help = hfh


            item = Inq_info_Item()
            item['hos_name'] = hos_name
            item['doc_name'] = doc_name

            item['patient_name'] = patient_name
            item['title'] = title
            item['illness_name'] = illness_name
            item['dialogue_num'] = dialogue_num
            item['last_date'] = last_date
            item['last_date1'] = last_date1
            item['illness_display'] = illness_display
            item['illness_content'] = illness_content
            item['hope_for_help'] = hope_for_help

            yield item











