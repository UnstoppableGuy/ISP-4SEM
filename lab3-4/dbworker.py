from rethinkdbcm import UseDatabase
from config import Config

USER1 = Config.USER_PERMISSION


class UseDB(object):
    def __init__(self, config: dict):
        self.config = config

    def presence_id(self, use_db, name_t, id_mane, req):
        with UseDatabase(self.config) as db:
            try:
                return db.countid(use_db, name_t, id_mane, req)
            except:
                return False

    def db_init(self, use_db):
        with UseDatabase(self.config) as db:
            try:
                return db.create_db(use_db)
            except:
                return False

    def db_delete(self, use_db):
        with UseDatabase(self.config) as db:
            try:
                return db.del_db(use_db)
            except:
                return False

    def tab_creat(self, use_db, use_tab):
        with UseDatabase(self.config) as db:
            try:
                return db.create_tab(use_db, use_tab)
            except:
                return False

    def tab_all(self, use_db):
        with UseDatabase(self.config) as db:
            try:
                return db.all_table(use_db)
            except:
                return False

    def tab_delete(self, use_db, use_tab):
        with UseDatabase(self.config) as db:
            try:
                return db.del_tab(use_db, use_tab)
            except:
                return False

    def new_record(self, use_db, use_tab, json):
        with UseDatabase(self.config) as db:
            try:
                return db.insert(use_db, use_tab, json)
            except:
                return False

    def get_all(self, use_db, use_tab):
        with UseDatabase(self.config) as db:
            try:
                return db.gettasks(use_db, use_tab)
            except:
                return False

    def get_root_user(self, use_db, use_tab, req):
        with UseDatabase(self.config) as db:
            try:
                return db.getroot(use_db, use_tab)[req]
            except:
                return False

    def get_one_user(self, use_db, use_tab, id_name):
        with UseDatabase(self.config) as db:
            try:
                return db.gettask(use_db, use_tab, id_name)
            except:
                return False

    def update_one_user(self, use_db, use_tab, id_name, json):
        with UseDatabase(self.config) as db:
            try:
                return db.updetask(use_db, use_tab, id_name, json)
            except:
                return False

    def delete_one_user(self, use_db, use_tab, id_name):
        with UseDatabase(self.config) as db:
            try:
                return db.delltask(use_db, use_tab, id_name)
            except:
                return False

    def get_user_id(self, use_db, use_tab, id_name):
        with UseDatabase(self.config) as db:
            try:
                d = db.gettask(use_db, use_tab, id_name)
                out = d if d else USER1
                return out
            except:
                return False
