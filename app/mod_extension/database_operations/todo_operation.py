# coding = utf-8
from app import models
from app.mod_extension.database_operations.general_operation import insert_to_database, commit, delete_from_database
from app.mod_extension.database_operations.user_operation import get_user_by_id


def todo_add(uid, label, title, content, start_time, deadline_time, priority, status, img_link=None):
    user = get_user_by_id(uid)
    if user is None:
        return False, "user doesn't exist"

    new_todo = models.ToDo(label, title, content, start_time, deadline_time, priority, status, img_link)
    user.todo_list.append(new_todo)
    ret = insert_to_database(models.ToDo,new_todo)
    # print(user)
    # print(new_todo)
    # print(ret)
    return ret


def get_todo_by_page(uid, mode=1, page_index=1, page_size=10):
    user = get_user_by_id(uid)
    # print(user)
    if user is None:
        return False, "user doesn't exist"
    todo_obj = models.ToDo.query.filter_by(uid=uid)
    total = len(todo_obj.all())

    if mode == 1:
        todo_list = todo_obj.order_by(models.ToDo.release_time.asc()).paginate(page_index,
                                                                               page_size,
                                                                               False)
    elif mode == 2:
        todo_list = todo_obj.order_by(models.ToDo.start_time.asc()).paginate(
            page_index,
            page_size, False)
    else:
        todo_list = todo_obj.order_by(models.ToDo.deadline_time.asc()).paginate(page_index,
                                                                                page_size,
                                                                                False)

    ret = []

    if todo_list:
        print(todo_list.items)
        for i in todo_list.items:
            ret.append(i.to_dict())

    data = {'eva_list': ret}
    pagination = {'limit': len(ret), 'total': total}
    return True, {'data': data, 'pagination': pagination}


def todo_search(todo_id, uid=None):
    if uid is None:
        return models.ToDo.query.filter_by(id=todo_id).first()
    else:
        return models.ToDo.query.filter_by(uid=uid).filter_by(id=todo_id).first()


def todo_update(todo_id, label, title, content, start_time, deadline_time, priority, status, img_link=None):
    result = todo_search(todo_id)
    if result is None:
        return False, "todo_id doesn't exist"

    get_todo = models.ToDo.query.filter_by(id=result.id)
    get_todo.update({
        models.ToDo.label: label,
        models.ToDo.title: title,
        models.ToDo.content: content,
        models.ToDo.start_time: start_time,
        models.ToDo.deadline_time: deadline_time,
        models.ToDo.priority: priority,
        models.ToDo.status: status,
        models.ToDo.img_link: img_link
    }, synchronize_session=False)

    return commit()


def todo_update_status(todo_id, status):
    result = todo_search(todo_id)
    if result is None:
        return False, "todo_id doesn't exist"

    get_todo = models.ToDo.query.filter_by(id=result.id)
    get_todo.update({
        models.ToDo.status: status,
    }, synchronize_session=False)

    return commit()


def todo_delete(todo_id, uid=None):
    result = todo_search(todo_id, uid)  # 查询某用户的todo，提高查询效率？
    if result is None:
        return False, "todo_id doesn't exist"
    return delete_from_database(result)
