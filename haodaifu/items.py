# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# 医院信息
class Hos_info_Item(scrapy.Item):
    pass

    # define the fields for your item here like:
    # name = scrapy.Field()

    '''
        hos_name	string	医院名
        city	string	医院所在城市
        level	string	医院分级
        good_doc_num	int	好评大夫数量
        hos_vote_num	int	医院得票数量
        hos_fav_rate	float	医院好评率
        rec_specialist_num	int	推荐专家人数
    '''

    hos_name = scrapy.Field()
    city = scrapy.Field()
    level = scrapy.Field()
    good_doc_num = scrapy.Field()
    # hos_vote_num = scrapy.Field()
    hos_fav_rate = scrapy.Field()
    rec_specialist_num = scrapy.Field()


# 医生信息
class Doc_info_Item(scrapy.Item):
    pass
    '''
        hos_name	string	医生所属医院名
        doc_name	string	医生名字
        doc_rank	string	医生职称
        department	string	医生所在科室
        score	float	医生评分
        vote_num_2year	int	2年内得票
        vote_num_total	int	总票
        display	string	擅长
        price_pic	int	图文问诊费用
        price_phone	int	电话问诊费用
        vote_by_patient	int	患者投票总数
        efficacy_satisfaction	int	疗效满意度
        attitude_satisfaction	int	态度满意度
    '''

    hos_name = scrapy.Field()
    doc_name = scrapy.Field()
    doc_rank = scrapy.Field()
    department = scrapy.Field()
    score = scrapy.Field()
    vote_num_2year = scrapy.Field()
    vote_num_total = scrapy.Field()
    display = scrapy.Field()
    price_pic = scrapy.Field()
    price_phone = scrapy.Field()
    vote_by_patient = scrapy.Field()
    efficacy_satisfaction = scrapy.Field()
    attitude_satisfaction = scrapy.Field()


# 患者投票信息
class Vote_info_Item(scrapy.Item):
    pass
    '''
        hos_name	string	医生所属医院名
        doc_name	string	医生名字
        patient_name	string	患者名字
        illness_name	string	所患疾病名字
        purpose	string	看病目的
        therapy_method	string	治疗方式
        efficacy_satisfaction	string	疗效满意度
        attitude_satisfaction	string	态度满意度
        cost	string	门诊花费
        state	string	目前疾病状态
        reason	string	选择医生理由
        comment_tag	string	评价标签
        comment_content	string	评论内容
        date	string	发布时间
    '''

    hos_name = scrapy.Field()
    doc_name = scrapy.Field()
    patient_name = scrapy.Field()
    illness_name = scrapy.Field()
    purpose = scrapy.Field()
    therapy_method = scrapy.Field()
    efficacy_satisfaction = scrapy.Field()
    attitude_satisfaction = scrapy.Field()
    cost = scrapy.Field()
    state = scrapy.Field()
    reason = scrapy.Field()
    comment_tag = scrapy.Field()
    comment_content = scrapy.Field()
    date = scrapy.Field()


# 科普文章信息
class Art_info_Item(scrapy.Item):
    pass
    '''
        hos_name	string	医生所属医院名
        doc_name	string	医生名字
        article_type	string	文章分类
        article_title	string	文章标题
        article_url	string	文章链接
        comment_num	int	评价数量
        pageview	int	阅读数量
        date	string	发布时间
    '''

    hos_name = scrapy.Field()
    doc_name = scrapy.Field()
    article_type = scrapy.Field()
    article_title = scrapy.Field()
    article_url = scrapy.Field()
    comment_num = scrapy.Field()
    pageview = scrapy.Field()
    date = scrapy.Field()


# 患者问诊信息
class Inq_info_Item(scrapy.Item):
    pass
    '''
        hos_name	string	医生所属医院名
        doc_name	string	医生名字

        patient_name	string	患者名字
        title	string	问诊标题
        illness_name	string	相关疾病名字
        dialogue_num	string	对话数
        last_date	string	最后发表时间

        last_date1	string	最后发表日期
        illness_display	string	疾病描述
        illness_content	string	疾病
        hope_for_help	string	希望得到的帮助
        sick_time	string	患病时间
        visited_department	string	已就诊科室
        allergic_history	string	过敏史

    '''
    hos_name = scrapy.Field()
    doc_name = scrapy.Field()

    patient_name = scrapy.Field()
    title = scrapy.Field()
    illness_name = scrapy.Field()
    dialogue_num = scrapy.Field()
    last_date = scrapy.Field()
    last_date1 = scrapy.Field()
    illness_display = scrapy.Field()
    illness_content = scrapy.Field()
    hope_for_help = scrapy.Field()
