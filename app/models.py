# coding=utf-8
import json
from app import db
from datetime import datetime
from sqlalchemy import UniqueConstraint, text

SUPER_USERS = [
    "14xfdeng",
    "14jhwang",
    "13yjli3"
]

VISIBILITY_VISIBLE = 1
VISIBILITY_INVISIBLE = 2


# 互动区域的吹水, 或者活动发布都可以
class Post(db.Model):
    # 话题, 用户自发的
    POST_TYPE_TOPIC = 0

    # (公众号推文)
    POST_TYPE_ACTIVITY = 1  # 如果是这种类型的话, 那么客户端处理的时候就要注意把content作为文章的URL

    # 校园活动的文章, 类似于推文
    # content视为URL, description为描述信息
    POST_TYPE_SCHOOL_ACTIVITY = 2

    # 匿名消息，当type为3的时候不记录用户UID
    POST_TYPE_ANONYMOUS = 3

    __tablename__ = "posts"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 类型
    post_type = db.Column(db.SMALLINT, nullable=False)

    # 描述信息(比如说公众号的推文的描述信息)
    description = db.Column(db.String(140))

    # 内容
    content = db.Column(db.TEXT)

    # 用户同时上传的图片列表, 存储原始的json数据
    photo_list_json = db.Column(db.TEXT)

    # 发布时间
    post_time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    # 是否对外部可见
    visibility = db.Column(db.SMALLINT, default=VISIBILITY_VISIBLE)

    # 记录客户端系统, 如 iOS android, 也可以记录活动部门
    source = db.Column(db.VARCHAR(20), nullable=True)

    # 主题
    title = db.Column(db.String(50))

    # =========== 活动相关 ===========
    # 活动开始时间
    activity_start_time = db.Column(db.TIMESTAMP, nullable=True)
    # 活动结束时间
    activity_end_time = db.Column(db.TIMESTAMP, nullable=True)
    # 活动地点
    activity_location = db.Column(db.VARCHAR(40), nullable=True)

    # =========== 活动相关 ===========

    # 发布者(外键)
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # 匿名情况下的uid
    real_uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"), nullable=True)

    # ========== 关系 ==========

    # 这篇文章得到的评论
    # cascade="all, delete-orphan", 表示删除这个文章的时候将会删除所有与之关联起来的对象
    # primaryjoin 指明 join 的条件
    comments = db.relationship("Comment", backref="post", cascade="all, delete-orphan",
                               primaryjoin="and_(Post.id==Comment.post_id, Comment.visibility==1)")

    # 这篇文章得到的赞
    thumb_ups = db.relationship("ThumbUp", backref="post", cascade="all, delete-orphan")

    # ========== 关系 ==========

    def __repr__(self):
        return "<Post {username}> - {content}".format(username=self.user.account, content=self.content)


# 用户表
class User(db.Model):
    # 性别常量
    GENDER_FEMALE = 0
    GENDER_MALE = 1
    GENDER_UNKNOWN = -1

    USER_NOT_FORBIDDEN = 1
    USER_FORBIDDEN = 0

    LEVEL_NORMAL = 0  # 普通权限
    LEVEL_CAN_POST_ACTIVITY = 1  # 可以发布活动信息
    LEVEL_MANAGER = 2  # 管理员权限, 可以删除任意信息

    __tablename__ = "users"  # 表名

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 用户账号
    account = db.Column(db.String(20), nullable=False, unique=True)

    # 用于封号
    valid = db.Column(db.SMALLINT, default=USER_NOT_FORBIDDEN)

    # 昵称, 默认为帐号名
    nickname = db.Column(db.String(20), default=account, unique=True)

    # 性别
    gender = db.Column(db.SMALLINT, default=GENDER_UNKNOWN)

    # 个人说明
    profile = db.Column(db.String(40))

    # 生日
    birthday = db.Column(db.TIMESTAMP, default=None)

    # token
    token = db.Column(db.String(6), default="000000")

    # 头像地址
    image = db.Column(db.String(128))

    # 是否对外部可见
    visibility = db.Column(db.SMALLINT, default=VISIBILITY_VISIBLE)

    # 记录用户权限
    level = db.Column(db.SMALLINT, default=LEVEL_NORMAL)

    # ========== 关系 ==========

    # 该用户做出过的评论
    comments = db.relationship("Comment", backref="user", lazy="dynamic")

    # 该用户点过的post赞
    thumb_ups = db.relationship("ThumbUp", backref="user", lazy="dynamic")

    # 该用户点过的comment赞
    comment_thumb_ups = db.relationship("CommentThumbUp", backref="user", lazy="dynamic")

    # 该用户发表过的Post
    posts = db.relationship("Post", backref="user", lazy="dynamic", foreign_keys=[Post.uid])
    anonymous_posts = db.relationship("Post", backref="publisher", lazy="dynamic", foreign_keys=[Post.real_uid])

    # 该用户的课程评价
    evaluations = db.relationship("Evaluation", backref="user", lazy="dynamic")

    # 该用户的TODO
    todo_list = db.relationship("ToDo", backref="user", lazy="dynamic")

    # 该用户的FindLost
    findlost_list = db.relationship("FindLost", backref="user", lazy="dynamic")

    # ========== 关系 ==========

    def __repr__(self):
        return "<User %r %r %r>" % (self.account, self.nickname, self.token)


# 评论
class Comment(db.Model):
    __tablename__ = "comments"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 评论时间, 自动更新
    post_time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    # 评论内容
    comment = db.Column(db.String(140))

    # 评论的对象
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)

    # 评论的发布者
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 是否对外部可见
    visibility = db.Column(db.SMALLINT, default=VISIBILITY_VISIBLE)

    # 评论得到的赞
    thumb_ups = db.relationship("CommentThumbUp", backref="comment", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Comment {username}> - {content}".format(username=self.user.account, content=self.comment)


# post 点赞
class ThumbUp(db.Model):
    __tablename__ = "thumb_ups"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 评论时间, 自动更新
    post_time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    # 点赞的对象
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)

    # 点赞的人
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 是否对外部可见
    # visibility = db.Column(db.SMALLINT, default=VISIBILITY_VISIBLE)

    def __repr__(self):
        return "<ThumbUp from {} to {}>".format(self.user.account, self.post.description)


# comment点赞
class CommentThumbUp(db.Model):
    __tablename__ = "comment_thumb_ups"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 评论时间, 自动更新
    post_time = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    # 点赞的对象
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=False)

    # 点赞的人
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 是否对外部可见
    # visibility = db.Column(db.SMALLINT, default=VISIBILITY_VISIBLE)

    def __repr__(self):
        return "<ThumbUp from {} to {}>".format(self.user.account, self.comment.comment)


class Carpool(db.Model):
    """
    拼车信息
    """

    __tablename__ = "carpools"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 发起拼车的童鞋
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 司机信息
    driver = db.Column(db.VARCHAR(50), nullable=True)

    # 自己的联系方式
    contact = db.Column(db.VARCHAR(200), nullable=True)

    # 出发地
    source = db.Column(db.VARCHAR(50), nullable=False)

    # 目的地
    destination = db.Column(db.VARCHAR(50), nullable=False)

    # 出发时间
    departure_time = db.Column(db.TIMESTAMP, default=None)

    # 备注
    notice = db.Column(db.VARCHAR(200))

    # 最多允许几个人拼车, 默认4人
    max_people = db.Column(db.SMALLINT, default=4)

    # 目前拼车人数
    people_count = db.Column(db.SMALLINT, default=1)

    # JOIN
    passengers = db.relationship("Passenger", backref="carpool", lazy="dynamic")

    def __repr__(self):
        return "<Carpool uid: {} {}/{}".format(self.uid, self.people_count, self.max_people)


class Passenger(db.Model):
    """
    拼车的用户
    """

    __tablename__ = "passengers"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 发起拼车的童鞋
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 拼车信息id
    carpool_id = db.Column(db.Integer, db.ForeignKey("carpools.id"), nullable=False)

    # join time
    join_time = db.Column(db.TIMESTAMP, default=None)

    # 自己的联系方式(用json方式存储)
    contact = db.Column(db.VARCHAR(200), nullable=True)

    def __repr__(self):
        return "<Passenger uid:{} contact:{}".format(self.uid, self.contact)


# 未读资源
class UnRead(db.Model):
    """
    每条记录有 uid, post_id 两个外键, 表明
    用户uid在post_id这篇文章内有未读的动态.
    """
    __tablename__ = "unreads"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 点赞的对象
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)

    def __repr__(self):
        return "<UnRead uid: %r pid: %r>" % (self.uid, self.post_id)


class Collector(db.Model):
    """
    用于记录收集对象以及其创建者
    """
    __tablename__ = "collectors"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 课表用户发送时候需要附上这个不重复的6位独特的数字串
    collection_id = db.Column(db.VARCHAR(6), unique=True)

    # 开始年份
    start_year = db.Column(db.SMALLINT, nullable=False)

    # 学期, 对应学分制, 春夏秋
    season = db.Column(db.SMALLINT, nullable=False)

    # 创建这个集合的用户id
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class SyllabusCollection(db.Model):
    """
    记录用户上传的课表
    """

    __tablename__ = "syllabus_collection"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 课表用户发送时候需要附上这个不重复的6位独特的数字串
    collection_id = db.Column(db.VARCHAR(6), nullable=False)

    # 课表的JSON信息
    syllabus = db.Column(db.TEXT, nullable=False)

    # 用户账号
    account = db.Column(db.String(20), nullable=False)


class STUCourse(db.Model):
    """
        课程表
    """

    # 指定表名
    __tablename__ = "course_table"

    # id 主键
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # 课程号
    course_id = db.Column(db.String(20), nullable=False, unique=True)

    # 课程名称
    course_name = db.Column(db.String(100), nullable=False)

    # 课程学分
    credit = db.Column(db.Float, nullable=False)

    # 开课单位
    department = db.Column(db.String(100), nullable=False)

    # 课时
    total_hour = db.Column(db.Integer)

    # 是否是通识课程
    # False-非通识课 True-通识课
    is_general = db.Column(db.Boolean)

    classes = db.relationship("STUClass", backref="course", lazy="dynamic")

    course_eva = db.relationship("TeacherAndCourse", backref="course", lazy="dynamic")

    def __init__(self, course_id, course_name, credit, department, total_hour, is_general):
        self.course_id = course_id
        self.course_name = course_name
        self.credit = credit
        self.department = department
        self.total_hour = total_hour
        self.is_general = is_general

    def to_dict(self):
        return {
            'cid': self.id,
            'course_id': self.course_id,
            'course_name': self.course_name,
            'credit': self.credit,
            'department': self.department,
            'total_hour': self.total_hour,
            'is_general': self.is_general,
            # 'classes': self.classes,
            # 'course_eva': self.course_eva
        }

    def to_json(self, name=None):
        if name is None:
            return json.dumps(self.to_dict())

        my_json = {
            name: self.to_dict()
        }
        return json.dumps(my_json)

    def __repr__(self):
        return "<STUCourse by %r %r>" % (self.course_id, self.course_name)


class STUTeacher(db.Model):
    """
        老师表
    """

    # 指定表名
    __tablename__ = "teacher_table"

    # id 主键
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # 老师工号
    teacher_id = db.Column(db.Integer, unique=True)

    # 老师名字
    name = db.Column(db.String(100), nullable=False)

    # 老师性别
    # True-男 False-女
    gender = db.Column(db.Boolean)

    # 老师简介
    introduction = db.Column(db.String(500))

    # 老师所属单位
    department = db.Column(db.String(100), nullable=False)

    classes = db.relationship("STUClass", backref="teacher", lazy="dynamic")

    teacher_eva = db.relationship("TeacherAndCourse", backref="teacher", lazy="dynamic")

    def __init__(self, teacher_id, name, gender, introduction, department):
        self.teacher_id = teacher_id
        self.name = name
        self.gender = gender
        self.introduction = introduction
        self.department = department

    def to_dict(self):
        return {
            'teacher_id': self.teacher_id,
            'name': self.name,
            'gender': self.gender,
            'introduction': self.introduction,
            'department': self.department,
            # 'classes': self.classes,
            # 'teacher_eva': self.teacher_eva
        }

    def to_json(self, name=None):
        if name is None:
            return json.dumps(self.to_dict())

        my_json = {
            name: self.to_dict()
        }
        return json.dumps(my_json)

    def __repr__(self):
        return "<STUTeacher by %r %r>" % (str(self.teacher_id), self.name)


class STUClass(db.Model):
    """
        班表
    """

    # 指定表名
    __tablename__ = "class_table"

    # id 主键
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # 班号
    class_id = db.Column(db.Integer, unique=True, nullable=False)

    # 老师工号
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher_table.teacher_id"))

    # 课程id
    cid = db.Column(db.Integer, db.ForeignKey("course_table.id"), nullable=False)

    # 年份
    years = db.Column(db.String(20))

    # 学期
    semester = db.Column(db.SMALLINT)

    # 教室
    room = db.Column(db.String(50))

    # 跨周
    span = db.Column(db.String(10))

    # 上课时间
    class_time = db.Column(db.String(100))

    evaluations = db.relationship("Evaluation", backref="user_class", lazy="dynamic")

    def __init__(self, class_id, years, semester, room, span, class_time):
        self.class_id = class_id
        self.years = years
        self.semester = semester
        self.room = room
        self.span = span
        self.class_time = class_time

    def to_dict(self):
        return {
            'class_id': self.class_id,
            'teacher_id': self.teacher_id,
            'cid': self.cid,
            'years': self.years,
            'semester': self.semester,
            'room': self.room,
            'span': self.span,
            'class_time': self.class_time
        }

    def to_json(self, name=None):
        if name is None:
            return json.dumps(self.to_dict())

        my_json = {
            name: self.to_dict()
        }
        return json.dumps(my_json)

    def __repr__(self):
        return "<STUClass by %r>" % str(self.class_id)


class Evaluation(db.Model):
    """
        评价表
    """

    # 指定表名
    __tablename__ = "evaluation_table"

    # id 主键
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # 评论学生id
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 所在班号
    class_id = db.Column(db.Integer, db.ForeignKey("class_table.class_id"))

    # 评论内容
    eva_content = db.Column(db.String(200))

    # 评论标签
    eva_tags = db.Column(db.String(50))

    # 评分
    eva_score = db.Column(db.Integer, nullable=False)

    # 评论状态
    # True-有效 False-无效
    eva_status = db.Column(db.Boolean, server_default=text('True'))

    # 评论时间
    eva_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    # # 评论学期
    eva_years_semester = db.Column(db.String(30), nullable=False)

    # 关联信息
    teacher_course = db.Column(db.Integer, db.ForeignKey("teacher_course_table.id"))

    __table_args__ = (UniqueConstraint('uid', 'teacher_course', name='unique_uid_tc'),)

    def __init__(self, eva_content, eva_tags, eva_score, eva_status, years_semester):
        self.eva_content = eva_content
        self.eva_tags = eva_tags
        self.eva_score = eva_score
        self.eva_status = eva_status
        self.eva_time = datetime.now()
        self.eva_years_semester = years_semester

    def to_dict(self):
        # print(type(self.eva_time))
        return {
            # 'uid':self.uid,
            'eva_id': self.id,
            'class_id': self.class_id,
            'teacher_id': TeacherAndCourse.query.filter_by(id=self.teacher_course).first().teacher_id,
            'cid': TeacherAndCourse.query.filter_by(id=self.teacher_course).first().cid,
            'eva_content': self.eva_content,
            'eva_tags': self.eva_tags,
            'eva_score': self.eva_score,
            'eva_status': self.eva_status,
            'eva_time': self.eva_time.strftime("%Y-%m-%d %H:%M:%S"),
            'eva_years_semester': self.eva_years_semester
            # 'teacher_course_id': self.teacher_course
        }

    def to_json(self, name=None):
        if name is None:
            return json.dumps(self.to_dict())

        my_json = {
            name: self.to_dict()
        }
        return json.dumps(my_json)

    def __repr__(self):
        return "<Evaluation by %r %r>" % (str(self.uid), self.eva_content)


class TeacherAndCourse(db.Model):
    """
        中间表
    """

    # 指定表名
    __tablename__ = "teacher_course_table"

    # id 主键
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # 老师工号
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher_table.teacher_id"))

    # 课程id
    cid = db.Column(db.Integer, db.ForeignKey("course_table.id"))

    # # 平均分
    # ave_score = db.Column(db.Integer)
    #
    # # 汇总标签
    # ave_tags = db.Column(db.String(40))

    evaluations = db.relationship("Evaluation", backref="teacher_and_course", lazy="dynamic")

    average_evaluations = db.relationship("AverageEvaluation", backref="teacher_and_course", lazy="dynamic")

    __table_args__ = (UniqueConstraint('teacher_id', 'cid', name='unique_teacher_course'),)

    def __init__(self):
        pass

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'cid': self.cid,
        }

    def to_json(self, name=None):
        if name is None:
            return json.dumps(self.to_dict())

        my_json = {
            name: self.to_dict()
        }
        return json.dumps(my_json)

    def __repr__(self):
        return "<TeacherAndCourse by %r %r>" % (str(self.teacher_id), str(self.cid))


class AverageEvaluation(db.Model):
    """
        教师课程 综合评价
    """

    # 指定表名
    __tablename__ = "ave_eva_table"

    # id 主键
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # 教师师课程关系id
    teacher_course = db.Column(db.Integer, db.ForeignKey("teacher_course_table.id"))

    # 平均分
    ave_score = db.Column(db.Integer)

    # 汇总标签
    ave_tags = db.Column(db.String(40))

    years_semester = db.Column(db.String(30), nullable=False)

    def __init__(self):
        pass

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_course': self.teacher_course,
            'ave_score': self.ave_score,
            'ave_tags': self.ave_tags,
            'years_semester': self.years_semester
        }

    def to_json(self, name=None):
        if name is None:
            return json.dumps(self.to_dict())

        my_json = {
            name: self.to_dict()
        }
        return json.dumps(my_json)


# todo表
class ToDo(db.Model):
    """
        ToDo表
    """

    # 指定表名
    __tablename__ = "todo_table"

    # 主键 id
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # 用户id
    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # 标签
    label = db.Column(db.String(50), nullable=False)

    # 主题
    title = db.Column(db.String(50))

    # 内容
    content = db.Column(db.String(500), nullable=False)

    # 发布时间
    release_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    # server_default = db.func.current_timestamp()

    # 开始时间
    start_time = db.Column(db.TIMESTAMP)

    # 截止时间
    deadline_time = db.Column(db.TIMESTAMP, nullable=False)

    # 优先级
    priority = db.Column(db.Integer, nullable=False)

    # 完成状态
    status = db.Column(db.Boolean, server_default=text('False'))

    # 图片链接
    img_link = db.Column(db.String(500))

    def __init__(self, label, title, content, start_time, deadline_time, priority, status, img_link=None):
        self.label = label
        self.title = title
        self.content = content
        self.release_time = datetime.now()
        self.start_time = start_time
        self.deadline_time = deadline_time
        self.priority = priority
        self.status = status
        self.img_link = img_link

    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'title': self.title,
            'content': self.content,
            'release_time': self.release_time.strftime("%Y-%m-%d %H:%M:%S"),
            'start_time': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'deadline_time': self.deadline_time.strftime("%Y-%m-%d %H:%M:%S"),
            'priority': self.priority,
            'status': self.status,
            'img_link': self.img_link
        }

    def to_json(self, name=None):
        if name is None:
            return json.dumps(self.to_dict())

        my_json = {
            name: self.to_dict()
        }
        return json.dumps(my_json)

    def __repr__(self):
        return "<ToDo by %r %r>" % (str(self.uid), self.content)


class FindLost(db.Model):
    """
    失物招领
    """

    __tablename__ = "findlost_table"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    uid = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    release_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    title = db.Column(db.String(50), nullable=False)

    location = db.Column(db.String(50), nullable=False)

    description = db.Column(db.String(140), nullable=False)

    contact = db.Column(db.String(30), nullable=False)

    img_link = db.Column(db.String(500))

    kind = db.Column(db.Integer, nullable=False)

    status = db.Column(db.Boolean, server_default=text('False'))

    def __init__(self, title, location, description, contact, img_link, kind):
        self.title = title
        self.location = location
        self.description = description
        self.contact = contact
        self.img_link = img_link
        self.kind = kind

    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'release_time': self.release_time.strftime("%Y-%m-%d %H:%M:%S"),
            'title': self.title,
            'location': self.location,
            'description': self.description,
            'contact': self.contact,
            'img_link': self.img_link,
            'kind': self.kind,
            'status': self.status
        }

    def to_json(self, name=None):
        if name is None:
            return json.dumps(self.to_dict())

        my_json = {
            name: self.to_dict()
        }
        return json.dumps(my_json)

    def __repr__(self):
        return "<FindLost by %r %r>" % (str(self.id), self.title)


# post topic 表
class Topic(db.Model):
    __tablename__ = "topic"

    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 话题名
    name = db.Column(db.VARCHAR(30))

    post_topic = db.relationship("Post", backref="topic", lazy="dynamic")
