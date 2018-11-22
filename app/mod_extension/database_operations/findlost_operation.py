# coding=utf-8


from app.models import *
from app import db
from app.mod_extension.database_operations.general_operation import *
from app.mod_extension.database_operations.user_operation import *


def findlost_add(uid, title, location, find_lost_time, description, contact, img_link, kind):
    user = get_user_by_id(uid)
    if user is None:
        return False, "user doesn't exist"

    new_find_lost = FindLost(title, location, find_lost_time, description, contact, img_link, kind)
    user.findlost_list.append(new_find_lost)
    ret = insert_to_database(FindLost,new_find_lost)
    return ret


def get_findlost_by_page(kind, page_index=1, page_size=10):
    findlost_obj = FindLost.query.filter_by(kind=kind)
    total = len(findlost_obj.all())

    findlost_list = findlost_obj.order_by(FindLost.release_time.asc()).paginate(page_index, page_size, False)

    ret = []

    if findlost_list:
        for i in findlost_list.items:
            ret.append(i.to_dict())

    data = {'findlost_list': ret}
    pagination = {'limit': len(ret), 'total': total}
    return True, {'data': data, 'pagination': pagination}


def findlost_fuzzy_search(kind, fuzzy_input, mode):
    if mode == 1:
        return FindLost.query.filter(FindLost.title.like("%" + fuzzy_input + "%"),
                                     FindLost.kind.like(kind)).all()
    else:
        return FindLost.query.filter(FindLost.description.like("%" + fuzzy_input + "%"),
                                     FindLost.kind.like(kind)).all()


def findlost_update(uid, findlost_id, title, location, find_lost_time, description, contact, img_link, kind):
    result = FindLost.query.filter_by(id=findlost_id).first()
    if result is None:
        return False, "findlost_id doesn't exist"

    if uid != result.uid:
        return False, "findlost_id uid doesn't match"
    get_findlost = FindLost.query.filter_by(id=result.id)
    get_findlost.update({
        FindLost.title: title,
        FindLost.location: location,
        FindLost.find_lost_time: find_lost_time,
        FindLost.description: description,
        FindLost.contact: contact,
        FindLost.img_link: img_link,
        FindLost.kind: kind
    }, synchronize_session=False)

    return commit()


def findlost_delete(uid, findlost_id):
    result = FindLost.query.filter(FindLost.id.like(findlost_id)).first()
    if result is None:
        return False, "findlost_id doesn't exist"

    if uid != result.uid:
        return False, "findlost_id uid doesn't match"

    return delete_from_database(result)
