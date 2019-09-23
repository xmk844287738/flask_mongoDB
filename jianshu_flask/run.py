from flask import Flask, render_template, request, redirect, url_for
from pyecharts import WordCloud
from jianshu_flask.user_analysis import config,anlysis_timeline
import re



app = Flask(__name__)

@app.route('/index', methods=['GET','POST'])
@app.route('/', methods=['GET', 'POST'])
def geturl():
    if request.method == 'POST':
        form_value = request.form['url']
        print(form_value)
        match_result = re.match(r'(https://)?(www.jianshu.com/u/)?(\w{6}|\w{12})$', form_value)  #例子： https://www.jianshu.com/u/485ed2eb0d8a
        print(match_result)
        if match_result:
            user_slug = match_result.groups()[-1]
            return redirect(url_for('jianshu_timeline', slug=user_slug))
        else:
            return render_template('index.html', error_msg='输入的用户主页有问题！请重新输入！')
    else:
        return render_template('index.html')  # 返回主页



# 路由视图函数
@app.route('/timeline')
def jianshu_timeline():
    slug = request.args.get('slug')
    args = config.TIMELINE_TYPES    # config 自定义配置文件
    user = anlysis_timeline.AnalysisUser(slug, *args)       # anlysis_timeline 文件下的 AnalysisUser 类
    baseinfo = user.get_baseinfo()
    first_tag_time = user.get_first_tag_time()
    tags_data = user.tags_data()
    # 调试运行！！！
    all_month_data = user.all_tags_data(time_period='month')
    all_day_data = user.all_tags_data(time_period='day')
    all_hour_data = user.all_tags_data(time_period='hour')
    all_week_data = user.all_tags_data(time_period='week')
    share_month_data = user.one_tag_data('share_notes', 'month')   # 参数对应'share_notes'=>tag 'month' =>time_period

    week_hour = {}
    for each in args[:5]:
        if baseinfo[each + '_num'] > 100:
            week_hour[each] = user.tag_week_hour_data(each)
        else:
            week_hour[each] = []
    comments = user.get_comment()
    # 重定向至 timeline.html 页面
    return render_template('timeline.html',
                           baseinfo=baseinfo,
                           first_tag_time=first_tag_time,
                           tags_data=tags_data,
                           month_data=all_month_data,
                           day_data=all_day_data,
                           hour_data=all_hour_data,
                           week_data=all_week_data,
                           share_month_data=share_month_data[1],
                           week_hour=week_hour,
                           comments_num=comments[0],
                           wordcloud_chart=make_wordcloud(comments[1]),
                           )

def make_wordcloud(comm_data):
    name = comm_data.keys()
    value = comm_data.values()
    wordcloud = WordCloud(width='100%', height=600)
    wordcloud.add("", name, value, shape="diamond", word_size_range=[15, 120])
    return wordcloud.render_embed()




if __name__ == '__main__':
    app.run(debug=True)