

class RAM:
    def __init__(self):
        self.users = {}

    def check_user(self, user_id : int = None):
        if self.users.get(user_id):
            return True
        else:
            return False

    def add_user(self, user_id : int = None, user_name : str = None):
        data = {'name' : user_name,
                'where' : None,
                'action' : 'get_name'}
        self.users[user_id] = data

    def get_action(self, user_id):
        return self.users[user_id]['action']

    def set_action(self, user_id = None, action = None):
        self.users[user_id]['action'] = action