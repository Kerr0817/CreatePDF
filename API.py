from flask import Flask, request, send_from_directory, make_response
from utils.MyReport import create_pdf
import requests, json
from flask import jsonify
# 时间戳
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return r"服务范例"

@app.route('/input', methods=['GET'])  # 添加路由input
def input():
    # json_yq = request.args.get('data')
    # print('云雀json数据', json_yq)
    '''--- 测试数据 --'''
    json_yq = '{"BestTeams":{"content":["121253","发生的"],"date":1542261532000,"file":9,"name":"test","time":7,"userid":"20411542261473232"},"Starfriends":{"content":[{"content":"阿道夫","date":1542607597000,"type":"text"},{"content":"123132","date":1544770491000,"type":"text"},{"content":"41","date":1543477116000,"type":"text"},{"content":"明德慎罚","date":1542607595000,"type":"text"},{"content":"克劳德萨弗兰克","date":1542607594000,"type":"text"},{"content":"阿道夫","date":1542607597000,"type":"text"},{"content":"你家里宽带覆盖到了分公司","date":1542607592000,"type":"text"},{"content":"123132","date":1544770491000,"type":"text"},{"content":"你家里宽带覆盖到了分公司","date":1542607592000,"type":"text"},{"content":"41","date":1543477116000,"type":"text"},{"content":"明德慎罚","date":1542607595000,"type":"text"},{"content":"克劳德萨弗兰克","date":1542607594000,"type":"text"}],"date":"2018-11-19","file":4,"name":"设计师3","time":18,"userid":"10000025600000"}}'
    data_yq = json.loads(json_yq)
    '''--- 星好友 ---'''
    friend_data = data_yq["Starfriends"]
    '''--- 最佳团队 ---'''
    team_data = data_yq["BestTeams"]
    '''--- 讨论测试数据 ---'''
    content_words = '阿道夫 123132 41 明德慎罚 哈哈 克劳德萨弗兰克 234 9001 四个 四个 四个 四个 四个人 阿道夫 你家里宽带覆盖到了分公司 你家里宽带覆盖到了分公司 41 明德慎罚 克劳德萨弗兰克 哈哈哈 这就是 我跟你说' \
                    '这艘不是 这都不是谁 硬核 太给力了 开会 明天要集体讨论 嗯 设计模式 哈哈 就这样吧 统一 同意 领导找你 对 就是这个 我不是跟你熟 来一下室办 是这个 你有' \
                    '照片么 文档发我一下 啊哪儿跟啊 在哪里开会 我在研发楼等你 打印一下报告 明天交报告 嗯嗯 好的 恩恩恩恩呢 嗯嗯 好的好的' \
                    '让我来 这是我来做 云雀 云雀 云雀 云雀 用云雀传 不用云雀传 云雀还可以 你把资料传云雀上 呼叫领导上云雀 我觉得可以 收到' \
                    '吃饭 楼下 这就来 感觉可以 真棒 先这样试试 辛苦了 发邮件 发nas 上传 光盘 刻录机 刚觉是 那本控制院里 知值奥 直到控制 ' \
                    '导航制导 仿真技术 北京故将 北京仿真中心 什么专业 不易 毕业了么 书记 主任 副主任 组长 研究院 副科长 胜利 好的 就这么牛皮'
    starttime = datetime.now()
    file_name = create_pdf(
        name='李爱国国',                                            # 用户名
        name_id=friend_data["userid"],                              # 用户id√
        head_image='./image/me.png',                                # 头像
        key_words='硬核少年',                                       # 关键词
        user_data=[[2, 2, 1], [5, 6, 2], [3, 3, 1], [2, 3, 1], [6, 7, 2], [4, 8, 3]],  # 六个能力
        key_language='爱国敬业诚信友善富强民主文明和谐自由平等公',  # 评价
        value_data=[[1, 3], [20, 200], [31, 310], [90, 100]],       # [我贡献值, 科室贡献值]
        friend_name=friend_data["name"],                            # 好友姓名√
        friend_date=friend_data["date"],                            # 初次相遇√
        friend_time=str(friend_data["time"]),                       # 研讨次数√
        friend_file=str(friend_data["file"]),                       # 文件交换√
        friend_content=content_words,                    # 讨论内容（好友）√ get_text_friend(data_yq)
        team_date=str(team_data['date']),                           # 创建时间√ 现在是int，最好(str)'2018-11-11'
        team_file=str(team_data['file']),                           # 上传文件√ int->str?我转？
        team_name=team_data['name'],                                # 最佳发言人√
        team_time=str(team_data['time']),                           # 团队人数√ int->str?我转？
        team_content=get_text_team(team_data["content"])            # 讨论内容（团队）√(str)"121253" "发生的"
    )
    print('[Report]画PDF：', (datetime.now() - starttime))
    '''--- 返回json对象 to 忠哥 ---'''
    rjson={}
    rjson['answer'] = 'success'
    rjson['data'] = file_name
    return jsonify(rjson)

@app.route("/download/<filename>")  # <参数>
def download(filename):
    response = make_response(send_from_directory('./static', filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1')) # filename有中文也没问题
    return response

def get_text_friend(chart_string):
    return " ".join([i["content"] for i in chart_string["Starfriends"]["content"]])
def get_text_team(chart_string):
    return " ".join(i for i in chart_string)
'''
a = json.loads(s)
b = a["Starfriends"]["content"]
c = [i["content"] for i in b]
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1028)  # 10.12.97.23  ipconfig
    # 0.0.0.0 监听全网
    # http://localhost:1028/input?data=test

'''
    # if tool == 'CreatReport':  # http://localhost:1028/input?data=CreatReport&user_id=111222199312091111
        # user_id = request.args.get('user_id')
        # r = requests.get('http://10.12.97.3:8083/interfaces/report/starfriends')
        # content_words = get_text(r.text)
        # else:
     # return "错误校权token"
'''
'''
    # return f"http://localhost:1028/download/{file_name}"
    # return f'<a href="localhost:1028/download/{file_name}">下载链接</a>'
'''
'''
{"knowledgeBehavior":{"knowledgeUploadCount":9,"knowledgeSharedCount":4,"knowledgeReadCount":28}}
'''

# http://10.12.97.22:8006/giksp/count!getUserKB2018.action?formvalue=123456