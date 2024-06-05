from db import cur, conn
from models import User, Todo
from sessions import Session
import utils

session = Session()


def login(username: str, password: str):
    user: Session | None = session.check_session()
    if user:
        return utils.BadRequest('You are already logged in', status_code=401)

    get_user_by_username = '''select * from users where username = %s;'''
    cur.execute(get_user_by_username, (username,))
    user_data = cur.fetchone()
    if not user_data:
        return utils.BadRequest('Username not found in my DB')
    _user = User(username=user_data[1], password=user_data[2], role=user_data[3], status=user_data[4],
                 login_try_count=user_data[5])

    if password != _user.password:
        update_count_query = """update users set login_try_count = login_try_count + 1 where username = %s;"""
        cur.execute(update_count_query, (_user.username,))
        conn.commit()

        if _user.login_try_count >= 2:
            return utils.BadRequest('You have exceeded the maximum number of login attempts. Your account is blocked.',
                                    status_code=401)

        return utils.ResponseData('Incorrect password')

    session.add_session(_user)
    return utils.ResponseData('User Successfully Logged in')


def delete_todo(todo_id: int):
    user: Session | None = session.check_session()
    if not user:
        return utils.BadRequest('You are not logged in', status_code=401)

    delete_todo_query = '''delete from "users" where id = %s;'''
    cur.execute(delete_todo_query, (todo_id,))
    conn.commit()
    return utils.ResponseData('User successfully deleted')


def update_todo(todo_id: int, new_username: str):
    user: Session | None = session.check_session()
    if not user:
        return utils.BadRequest('You are not logged in', status_code=401)

    update_todo_query = '''update "users" set username = %s where id = %s;'''
    cur.execute(update_todo_query, (new_username, todo_id))
    conn.commit()
    return utils.ResponseData('Username successfully updated')


def block_user(username: str):
    admin_user: Session | None = session.check_session()
    if not admin_user:
        return utils.BadRequest('You are not logged in', status_code=401)

    if admin_user.role != 'SUPERADMIN':
        return utils.BadRequest('You do not have the required permissions', status_code=403)

    block_user_query = '''update users set status = 'blocked', login_try_count = 100 where id = %s;'''
    cur.execute(block_user_query, (username,))
    conn.commit()
    return utils.ResponseData(f'User {username} successfully blocked')


if __name__ == "__main__":
    while True:
        choice = input('Enter your choice:\n(1 to login)\n(2 to delete)\n(3 to update)\n(4 to block): ')
        if choice == '1':
            username = input('Enter your username: ')
            password = input('Enter your password: ')
            response = login(username, password)
            print(response.data)
            if response.status_code == 401:
                break
        elif choice == '2':
            todo_id = int(input('Enter todo ID to delete: '))
            response = delete_todo(todo_id)
            print(response.data)
        elif choice == '3':
            todo_id = int(input('Enter user ID to update username: '))
            new_username = input('Enter new username: ')
            response = update_todo(todo_id, new_username)
            print(response.data)
        elif choice == '4':
            username = input('Enter username to block: ')
            response = block_user(username)
            print(response.data)
        else:
            break

