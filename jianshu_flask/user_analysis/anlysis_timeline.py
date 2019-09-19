import pymongo
from jianshu_flask.user_analysis import config
from jianshu_flask.user_analysis.jianshu_timeline import GetAllInfo    # . 当前文件夹




class AnalysisUser():
    def __init__(self, slug,*args):
        self.client = pymongo.MongoClient(config.MONGO_HOST, config.MONGO_PORT)
        self.db = self.client[config.MONGO_TABLE]
        self.slug = slug
        self.parent_tags = args
        self.zh_parent_tags = ['发表评论','喜欢文章','赞赏文章','发表文章','关注用户','关注专题','点赞评论','关注文集']     #  定义八个字段 对应 初始化盛数据的容器：timeline

        user_data = self.db.user_timeline.find_one({'slug': self.slug})
        update = config.UPDATE
        if user_data and update==False:
            '''如果指定不更新数据且数据已经在mongodb中'''
            self.user_data = user_data
        else:
            '''获取或更新数据到mongodb中'''
            GetAllInfo().getallinfo(slug)
            '''从mongodb中取出该用户的数据'''
            self.user_data = self.db.user_timeline.find_one({'slug': self.slug})    # mongoDB 操作语法 键值对



    # '''以下为辅助函数，用来时间提取及统计'''
    def extract_first_tag_time(data):
        '''
        根据给出的data，以时间对列表进行排序，返回列表的第一个值，即为数据列表中的第一次动态
        :param data: 用户某个类型的动态列表，如所有关注用户数据
                    {'like_users':[{'slug': 'y3Dbcz', 'time': '2013-05-24 18:26:01'},
                                    {'slug': '2f1c0190679d', 'time': '2014-02-11 13:02:03'}]}
        :return: 数据列表中的第一次动态
        '''
        if data:
            sorted_data = sorted(data, key=lambda each: each['time'])
            first_tag_time = sorted_data[0]
            return first_tag_time
        else:
            return None

    # 根据给出的时间点列表，进行时间分片，和时间段统计
    def extract_time_func(self,time_list, start, end):  # time_list 时间列表  start 开始时间    end结束时间
        if time_list:
            user_time_you_want = [time[start:end] for time in time_list]
            counter_you_want_f = Counter(user_time_you_want)    #from collections import Counter
            sort_counter = sorted(counter_you_want_f.items(), key=lambda t: t[0])
            data = {'time_slot': [a[0] for a in sort_counter],
                    'freqency': [a[1] for a in sort_counter]}
            return data
        else:
            return None



    # 根据给出的得时间列表，以月为时间段，统计每月动态频次
    def extract_month_data(self,time_list):
        if time_list:
            data = self.extract_time_func(time_list, 0, 7)
            month_data = {'month_line': data['time_slot'], 'month_freqency': data['freqency']}
            # print(month_data)
            return month_data
        else:
            return None

    # 根据给出的得时间列表，以周为时间段，统计每周动态频次
    def extract_week_data(time_list):
        pass


    # 根据给出的得时间列表，以日为时间段，统计每日动态频次
    def extract_day_data(time_list):
        pass


# 根据给出的得时间列表，以小时为时间段，统计每小时动态频次
    def extract_hour_data(time_list):
        pass

    # 通过datetime模块，将时间串转化为周
    def date_to_week(string_date):
        pass



    def get_baseinfo(self):
        baseinfo = {'head_pic': self.user_data['head_pic'],
                    'nickname': self.user_data['nickname'],
                    'update_time': self.user_data['update_time'],
                    'like_users_num': self.user_data['following_num'],
                    'followers_num': self.user_data['followers_num'],
                    'share_notes_num': self.user_data['articles_num'],
                    'words_num': self.user_data['words_num'],
                    'be_liked_num': self.user_data['be_liked_num'],
                    'like_notes_num': len(self.user_data['like_notes']),
                    'like_colls_num': len(self.user_data['like_colls']),
                    'like_nbs_num': len(self.user_data['like_notebooks']),
                    'comment_notes_num': len(self.user_data['comment_notes']),
                    'like_comments_num': len(self.user_data['like_comments']),
                    'reward_notes_num': len(self.user_data['reward_notes'])
                    }
        # print(baseinfo)
        return baseinfo



    def get_first_tag_time(self):
        first_tag_time = {
            'join_time': self.user_data['join_time'],
            'first_like_user': self.extract_first_tag_time(self.user_data['like_users']),
            'first_share_note': self.extract_first_tag_time(self.user_data['share_notes']),
            'first_like_note': self.extract_first_tag_time(self.user_data['like_notes']),
            'first_like_coll': self.extract_first_tag_time(self.user_data['like_colls']),
            'first_like_nb': self.extract_first_tag_time(self.user_data['like_notebooks']),
            'first_comment': self.extract_first_tag_time(self.user_data['comment_notes']),
            'first_like_comment': self.extract_first_tag_time(self.user_data['like_comments']),
            'first_reward_note': self.extract_first_tag_time(self.user_data['reward_notes']),
        }
        return first_tag_time


    def tags_data(self):
        tags_name = [{'name': name} for name in self.zh_parent_tags]    # 列表表达式 [表达式 for 变量 in 列表]，表示把得到的每一个变量值都放到 for 前面的表达式中计算 ，然后生成一个列表
        tags_value = [{'value': len(self.user_data[tag])} for tag in self.parent_tags]
        tags_data = [dict(tags_name[i], **tags_value[i]) for i in range(len(tags_name))]
        return tags_data


    def all_tags_time(self):
        '''all_tags = ('comment_notes', 'like_notes', 'reward_notes','share_notes',
                 'like_users', 'like_colls','like_comments', 'like_notebooks')'''
        all_time_list = []
        for tag in self.parent_tags:
            pertime = [each['time'] for each in self.user_data['%s' % tag]]
            all_time_list.extend(pertime)
        # 加入简书的时间
        join_time = self.user_data['join_time']
        if join_time == None:
            pass
        else:
            all_time_list.append(join_time)
        return all_time_list

    def per_tag_time(self, tag):
          # param tag: 标签，动态的类型  return: 子注册以来，发生该种类型动态的所有时间点
        per_tag_time = [each['time'] for each in self.user_data['%s' % tag]]    #列表表达式
        return per_tag_time

    # 根据选择对的时间段，得出注册以来所有动态在时间段内的分布统计 param  time_period: 时间段。可选 'month', 'week', 'day', 'hour' 四种类型，分别以月，周，天，小时分类
    def all_tags_data(self,time_period):
        # 根据选择对的时间段，得出注册以来所有动态在时间段内的分布统计  param time_period: 时间段。
        # 可选 'month', 'week', 'day', 'hour' 四种类型，分别以月，周，天，小时分类
        if time_period == 'month':
            all_tags_data = self.extract_month_data(self.all_tags_time())

    # 抽出所有评论，进行词频统计，得出该用户评论中最常用的词，并绘制词云
    def get_comment(self):
        pass





if __name__ == '__main__':
    print("open")
    slug = 'yZq3ZV'
    args = config.TIMELINE_TYPES
    user = AnalysisUser(slug, *args)

    first_tag_time = user.get_first_tag_time()
