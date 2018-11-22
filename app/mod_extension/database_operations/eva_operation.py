# coding=utf-8
from app.mod_extension.database_operations.general_operation import insert_to_database, delete_from_database, commit
from app.mod_extension.database_operations.user_operation import get_user_by_id
from app.models import STUCourse, STUClass, STUTeacher, TeacherAndCourse, Evaluation


def get_class_by_class_id(class_id):
    return STUClass.query.filter_by(class_id=class_id).first()


# =================基本(增删改查)===================
#
# =================基本(增删改查)===================
def insert_eva(uid, class_id, eva_content, eva_tags, eva_score, eva_status, cid, teacher_id):
    user = get_user_by_id(uid)
    tc = get_tc_by_tid_cid(teacher_id, cid)
    user_class = get_class_by_class_id(class_id)
    years_semester = user_class.years + "-" + str(user_class.semester)

    newEva = Evaluation(eva_content, eva_tags, eva_score, eva_status, years_semester)

    user_class.evaluations.append(newEva)
    user.evaluations.append(newEva)
    tc.evaluations.append(newEva)

    return insert_to_database(Evaluation, newEva)


def update_eva(eva_id, eva_content, eva_tags, eva_score, eva_status, eva_time):
    # uid = qUser_by_account(account).id
    # get_eva = qEvaluation(uid, teacher_id, cid, 2)
    get_eva = get_eva_by_id(eva_id)
    if get_eva is None:
        print("update not find")
        return False

    get_eva.update({
        Evaluation.eva_content: eva_content,
        Evaluation.eva_tags: eva_tags,
        Evaluation.eva_score: eva_score,
        Evaluation.eva_status: eva_status,
        Evaluation.eva_time: eva_time
    }, synchronize_session=False)

    return commit()


def delete_eva_by_id(eva_id):
    result = get_eva_by_id(eva_id).first()
    if result is None:
        print("eva not found")
        return False
    # print(result)
    ret = delete_from_database(result)
    # print(ret)
    return ret


def get_eva_by_id(eva_id):
    return Evaluation.query.filter_by(id=eva_id)


def get_personal_eva_by_uid(uid, mode=1, page_index=1, page_size=10):
    user = get_user_by_id(uid)
    print(user)
    if user is None:
        return False, "user doesn't exist"
    eva_obj = Evaluation.query.filter_by(uid=uid)
    total = len(eva_obj.all())
    if mode == 1:
        eva_list = eva_obj.order_by(Evaluation.eva_time.asc()).paginate(page_index, page_size, False)
    else:
        eva_list = eva_obj.order_by(Evaluation.eva_score.asc()).paginate(page_index, page_size, False)

    ret = []
    if eva_list:
        for i in eva_list.items:
            ret.append(i.to_dict())

    data = {'eva_list': ret}
    pagination = {'limit': len(ret), 'total': total}
    return True, {'data': data, 'pagination': pagination}


def get_class_eva(teacher_id, course_id, class_id, mode=1, term=1, page_index=1, page_size=10):
    tc_id = get_tc_by_tid_cid(teacher_id, course_id).id
    # term = 1 ：课程班的本学期
    # term = 0 ：所有学期
    # mode = 1：查询同课程同老师的所有评价（有多个班），时间排序：降序
    # mode = 2：查询同课程同老师的所有评价（有多个班），分数排序：降序
    # mode = 3：查询同班课的所有评价，时间排序：降序
    # mode = 4：查询同班课的所有评价，分数排序：降序
    if mode == 1:
        eva_obj = Evaluation.query.filter_by(teacher_course=tc_id)
        if term == -1:
            eva_list = eva_obj.order_by(Evaluation.eva_time.desc()).paginate(page_index, page_size, False)
        else:
            stu_class = get_class_by_class_id(class_id)
            years_semester = stu_class.years + "-" + str(stu_class.semester)
            eva_list = eva_obj.filter_by(eva_years_semester=years_semester).order_by(
                Evaluation.eva_time.asc()).paginate(page_index, page_size, False)
    elif mode == 2:
        eva_obj = Evaluation.query.filter_by(teacher_course=tc_id)
        if term == -1:
            eva_list = eva_obj.order_by(Evaluation.eva_score.desc()).paginate(page_index, page_size, False)
        else:
            stu_class = get_class_by_class_id(class_id)
            years_semester = stu_class.years + "-" + str(stu_class.semester)
            eva_list = eva_obj.filter_by(eva_years_semester=years_semester).order_by(Evaluation.eva_score.desc()).paginate(
                page_index, page_size, False)
    elif mode == 4:
        eva_obj = Evaluation.query.filter_by(class_id=class_id)
        eva_list = eva_obj.order_by(Evaluation.eva_score.desc()).paginate(page_index, page_size, False)
    else:
        eva_obj = Evaluation.query.filter_by(class_id=class_id)
        eva_list = eva_obj.order_by(Evaluation.eva_time.desc()).paginate(page_index, page_size, False)

    total = len(eva_obj.all())
    ret = []
    if eva_list:
        for i in eva_list.items:
            ret.append(i.to_dict())

    data = {'eva_list': ret}
    pagination = {'limit': len(ret), 'total': total}
    return True, {'data': data, 'pagination': pagination}


# 暂时未用

# def get_eva_by_uid(uid):
#     return Evaluation.query.filter_by(uid=uid).all()


# def get_eva(uid, teacher_id, cid, mode=1):
#     tc_id = get_tc_by_tid_cid(teacher_id, cid).id
#     if mode == 1:
#         return Evaluation.query.filter(Evaluation.uid.like(uid),
#                                        Evaluation.teacher_course.like(tc_id)).first()
#     else:
#         return Evaluation.query.filter(Evaluation.uid.like(uid),
#                                        Evaluation.teacher_course.like(tc_id))


# def get_eva_by_tid_cid(teacher_id, cid):
#     tc_id = get_tc_by_tid_cid(teacher_id, cid).id
#     return Evaluation.query.filter(Evaluation.teacher_course.like(tc_id)).all()


# def delete_eva(uid, teacher_id, cid):
#     result = get_eva(uid, teacher_id, cid)
#     if result is None:
#         print("delete not found")
#         return False
#     ret = delete_from_database(result)
#     return ret[0]


# ================Course=======================
#
# ================Course=======================
def get_course_by_id(id):
    return STUCourse.query.filter_by(id=id).first()


def get_course_by_course_name(course_name):
    return STUCourse.query.filter_by(course_name=course_name).all()


def fuzzy_search_course_by_course_name(fuzzy_input):
    return STUCourse.query.filter(STUCourse.course_name.like("%" + fuzzy_input + "%")).all()


def get_course_by_department(department):
    return STUCourse.query.filter_by(department=department).all()


def fuzzy_search_course_by_department(fuzzy_input):
    result = STUCourse.query.filter(STUCourse.department.like("%" + fuzzy_input + "%")).all()

    dep_set = set()

    for i in result:
        dep_set.add(i.department)

    return list(dep_set)


# 暂时未用
# def get_course_by_course_id(course_id):
#     return STUCourse.query.filter_by(course_id=course_id).first()

# def get_course_by_dep_gen(department, is_general):
#     return STUCourse.query.filter(STUCourse.department.like(department),
#                                   STUCourse.is_general.like(is_general)).all()


# =================Teacher=======================
#
# =================Teacher=======================

def get_teacher_by_teacher_id(teacher_id):
    return STUTeacher.query.filter_by(teacher_id=teacher_id).first()


def fuzzy_search_teacher_by_name(fuzzy_input):
    return STUTeacher.query.filter(STUTeacher.name.like("%" + fuzzy_input + "%")).all()


# 暂时没用

# def get_teacher_by_name(name):
#     return STUTeacher.query.filter_by(name=name).all()

# def get_teacher_by_department(department):
#     return STUTeacher.query.filter_by(department=department).all()


# =================TeacherCourse===================
#
# =================TeacherCourse===================
def get_tc_by_course_id(cid):
    return TeacherAndCourse.query.filter_by(cid=cid).all()


def get_tc_by_teacher_id(teacher_id):
    return TeacherAndCourse.query.filter_by(teacher_id=teacher_id).all()


def get_tc_by_tid_cid(teacher_id, cid):
    return TeacherAndCourse.query.filter(TeacherAndCourse.teacher_id.like(teacher_id),
                                         TeacherAndCourse.cid.like(cid)).first()
