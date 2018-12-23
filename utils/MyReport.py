# -*- coding: utf-8 -*-
# 字体库
from reportlab.pdfgen.canvas import Canvas
import matplotlib.pyplot as plt
import numpy as np
import hashlib
import os
# 字体
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# 用于定位的inch库，inch将作为我们的高度宽度的单位
from reportlab.lib.units import inch
# 颜色
from reportlab.lib.colors import HexColor
# 时间戳
from datetime import datetime
# 热词
import jieba
from collections import Counter
# 词云
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
# 遮罩
from PIL import Image


def create_pdf(
               friend_hotwords_image='./image/we2.png',
               name='李爱国国',                                            # 用户名
               name_id='111222199312091111',                               # 用户id√
               head_image='./image/me.png',                                # 头像
               key_words='硬核少年',                                       # 关键词
               user_data=[[2, 2, 1], [5, 6, 2], [3, 3, 1], [2, 3, 1], [6, 7, 2], [4, 8, 3]],  # 六个能力
               key_language='爱国敬业诚信友善富强民主文明和谐自由平等公',  # 评价
               value_data=[[1, 3], [20, 200], [31, 310], [90, 100]],       # [我贡献值, 科室贡献值]
               friend_name='航小天',                                         # 好友姓名√
               friend_date='2018-00-00',                                   # 初次相遇√
               friend_time='6666',                                         # 研讨次数√
               friend_file='6',                                            # 文件交换√
               friend_content='云雀 云雀 云雀 年度 11室',                  # 讨论内容（好友）√
               team_date='2018-11-11',                                     # 创建时间√ 现在是int，最好(str)'2018-11-11'
               team_file='8',                                              # 上传文件√ int->str?我转？
               team_name='航大天',                                         # 最佳发言人√
               team_time='8888',                                           # 团队人数√ int->str?我转？
               team_content='年报 年报 年报 年度 11室'                     # 讨论内容（团队）√(str)"121253" "发生的"
               ):  # 显示上：缺头像、雷达图、关键词、评价、科室贡献
    '''--- 第一页 ---'''
    # 处理雷达图
    digist, radar_image = create_radar_img(name, user_data)  # userdata = [[数据,最大,最小值], [数据,最大,最小值], [数据,最大,最小值], [数据,最大,最小值]]
    stopwords = {"我", '你',' ', '，', '的', ',','了','这','跟','不是','吗','么','嘛','嗯','好的','好'}
    mask = np.array(Image.open('./image/we.png'))  # 遮罩
    hotwords_image = pain_word_cloud(friend_content, stopword_set=stopwords, mask=mask)
    # 开画布
    can = Canvas(f"./static/{name_id}.pdf")  # digist
    # 注册字体
    pdfmetrics.registerFont(TTFont('msyh', './ttf/msyh.ttf'))
    pdfmetrics.registerFont(TTFont('song', './ttf/汉仪大宋简.ttf'))
    can.drawImage('./image/a.png', 0, 0, 596, 843)
    # 加头像
    can.drawImage(head_image, 69, 486, height=0.53 * inch, width=0.63 * inch)
    # 加关键词
    key_words = key_words
    can.setFillColor(HexColor(0x01f7fd))
    can.setFont('song', 50)
    can.drawString(1.8 * inch, 6.75 * inch, key_words)
    # 加雷达图
    can.drawImage(radar_image, 360, 400, 170, 170, mask='auto')
    # 关键词语解释(改进：换行)
    can.setFillColor(HexColor(0xffffff))
    can.setFont('song', 14)
    can.drawString(0.9 * inch, 6.3 * inch, key_language)
    can.drawString(0.9 * inch, 6.0 * inch, key_language)
    can.drawString(0.9 * inch, 5.7 * inch, key_language)
    '''--- 我的贡献值 ---'''
    mvalue_data = [i[0]/i[1] for i in value_data]
    can.setFillColor(HexColor(0x01f7fd))
    can.setFont('song', 18)
    can.drawString(1.3 * inch, 3.55 * inch, '{:.2%}'.format(mvalue_data[0]))
    can.drawString(3.0 * inch, 3.55 * inch, '{:.2%}'.format(mvalue_data[1]))
    can.drawString(4.55 * inch, 3.55 * inch, '{:.2%}'.format(mvalue_data[2]))
    can.drawString(6.2 * inch, 3.55 * inch, '{:.2%}'.format(mvalue_data[3]))
    '''--- 年度星好友 ---'''
    can.setFillColor(HexColor(0xffffff))
    can.setFont('song', 24)
    can.drawString(1.4 * inch, 1.12 * inch, friend_name)
    can.setFillColor(HexColor(0x01f7fd))
    can.setFont('song', 16)
    can.drawString(5.15 * inch, 1.36 * inch, friend_date)
    can.drawString(6.75 * inch, 1.36 * inch, friend_time+'次')
    can.drawString(5.6 * inch, 0.55 * inch, friend_file+'个')
    # 测试
    friend_word = '硬核'
    can.drawString(6.75 * inch, 0.55 * inch, friend_word)
    can.drawImage(hotwords_image, 5 * inch, 0.5 * inch, 240, 120, mask='auto')
    can.showPage()  # showPage将保留之前的操作内容之后新建一张空白页
    os.remove(radar_image)
    # os.remove(hotwords_image)

    '''--- 第二页 ---'''
    can.drawImage('./image/b.png', 0, 0, 596, 843)
    can.showPage()
    # 将所有的页内容存到打开的pdf文件里面
    can.save()
    return f"{name_id}.pdf"  # D:\toolsupload\Report\user_id.pdf

'''--- 雷达图 ---'''
def create_radar_img(name, data):
    labels = np.array(['任务', '研讨', '工具', '数据', '知识', '搜索'])
    try:
        data = [(i[0]-i[2])/(i[1]-i[2]) for i in data]  # 归一化
    except:
        print('数据错误')
    data.append(data[0])
    angles = [np.pi * 3 / 6, np.pi * 5 / 6, np.pi * 7 / 6, np.pi * 9 / 6, np.pi * 11 / 6, np.pi / 6]
    angles = np.concatenate((angles, [angles[0]]))
    # 处理数据
    num = 20
    mdata = []
    for i in range(num):
        tmp = [j/num*(num-i) for j in data]
        mdata.append(tmp)

    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)  # polar参数！！
    for i in range(num):
        ax.plot(angles, mdata[i], 'b-', linewidth=1, alpha=0.5)
        ax.fill(angles, mdata[i], alpha=0.3, facecolor='m')  # 填充
    ax.set_thetagrids(angles * 180 / np.pi, labels, fontproperties='SimHei', fontsize=25, color='#01f7fd')
    # ax.set_title(f"{name}的雷达图", va='bottom', fontproperties="SimHei")
    ax.grid(False)  # 不显示默认的分割线
    ax.spines['polar'].set_visible(False)  # 不显示极坐标最外圈的圆
    ax.set_yticks([])  # 不显示坐标间隔
    # # 画若干个六边形
    floor = int(min(data))
    ceil = int(max(data))+0.2
    ax.plot(angles, [ceil] * 7, '-', lw=3, color='#01f7fd')
    md = hashlib.md5()
    md.update(name.encode('utf-8'))
    digest = md.hexdigest()

    pathRadar = f'./image/{digest}.png'
    plt.savefig(pathRadar, format='png', bbox_inches='tight', transparent=True)
    # plt.show()
    return digest, pathRadar
'''--- 判断数字：中文数字、阿拉伯数字、正负小数'''
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
'''--- 分词 ---'''
def trans_CN(text, stopwords):
    word_list = jieba.cut(text)  # 不是list，是生成器，你要的时候才去生成一点，对内存有帮助 # text是所有评论用逗号隔开
    tmp = list(word_list)
    # stop = {' ', '，', '的', ',', '阿道夫'}
    stop = stopwords
    for m_word in stop:
        while m_word in tmp[::-1]:
            tmp.remove(m_word)
    print(tmp)

    number_zh = {'一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万'}  # set 集合
    number_zh.update({f'{i}' for i in range(10)})
    for i in tmp[::-1]:  # 倒叙遍历
        if set(i) & number_zh:  # set(i)把"四个"分成"四"和"个"
            tmp.remove(i)
    print(tmp)
    word_fre = Counter(tmp)
    print(word_fre)
    print(word_fre.most_common(1))
    print(word_fre.most_common(1)[0][0])
    result = " ".join(tmp)  # result是很长的字符串，list用空格隔开变成str word_list
    return result  # 往外传
'''--- 词云 ---'''
def pain_word_cloud(
        word_string,
        scale=3,
        stopword_set=None,
        mask=None,
        font_path="C:\Windows\Fonts\STXINGKA.TTF",
        randowm_state=42,
        max_font_size=40):
    text = trans_CN(word_string, stopword_set)
    # 设置停用词
    stopwords = set(STOPWORDS)
    stopwords.update(stopword_set)
    image_colors = ImageColorGenerator(mask)
    # 设置词云形状
    wordcloud = WordCloud(
        background_color=(255, 255, 255, 0), scale=scale, mask=mask, stopwords=stopwords, max_font_size=400,
        random_state=randowm_state, font_path=font_path, mode="RGBA"
    ).generate(text)  # mask：遮罩；random_state词云参数；font_path字体路径

    # 只用mask遮罩
    image_co = wordcloud.recolor(color_func=image_colors)
    image_produce = image_co.to_image()
    # image_produce.show()
    pathHotWords = './image/we2.png'
    image_produce.save(pathHotWords)
    return pathHotWords


if __name__ == '__main__':

    content_words = '阿道夫 123132 41 明德慎罚 哈哈 克劳德萨弗兰克 234 9001 四个 四个 四个 四个 四个人 阿道夫 你家里宽带覆盖到了分公司 你家里宽带覆盖到了分公司 41 明德慎罚 克劳德萨弗兰克 哈哈哈 这就是 我跟你说' \
                    '这艘不是 这都不是谁 硬核 太给力了 开会 明天要集体讨论 嗯 设计模式 哈哈 就这样吧 统一 同意 领导找你 对 就是这个 我不是跟你熟 来一下室办 是这个 你有' \
                    '照片么 文档发我一下 啊哪儿跟啊 在哪里开会 我在研发楼等你 打印一下报告 明天交报告 嗯嗯 好的 恩恩恩恩呢 嗯嗯 好的好的' \
                    '让我来 这是我来做 云雀 云雀 云雀 云雀 用云雀传 不用云雀传 云雀还可以 你把资料传云雀上 呼叫领导上云雀 我觉得可以 收到' \
                    '吃饭 楼下 这就来 感觉可以 真棒 先这样试试 辛苦了 发邮件 发nas 上传 光盘 刻录机 刚觉是 那本控制院里 知值奥 直到控制 ' \
                    '导航制导 仿真技术 北京故将 北京仿真中心 什么专业 不易 毕业了么 书记 主任 副主任 组长 研究院 副科长 胜利 好的 就这么牛皮'
    stopwords = {"我", '你',' ', '，', '的', ',', '了', '这', '跟', '不是', '吗','么','嘛','嗯','好的','好'}
    mask = np.array(Image.open('../image/quan.tif'))  # 遮罩
    pain_word_cloud(content_words, stopword_set=stopwords, mask=mask)  # font_path="C:\Windows\Fonts\hanyi.TTF"
    # create_pdf(friend_content=content_words)
