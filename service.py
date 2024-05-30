from db import cur, conn
from models import User
from sessions import Session
import utils

session = Session()


def login(username: str, password: str):
    user: Session | None = session.check_session()
    if user:
        return utils.BadRequest('You already logged in', status_code=401)

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

    session.check_session()
    return utils.ResponseData('User Successfully Logged in')


if __name__ == "__main__":
    while True:
        choice = input('Enter your choice: ')
        if choice == '1':
            username = input('Enter your username: ')
            password = input('Enter your password: ')
            response = login(username, password)
            if response.status_code == 401:
                print(response.data)
                break
            print(response.data)
        else:
            break

