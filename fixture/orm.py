from pony.orm import *
from datetime import datetime
from model.data import Group
from model.data import Contact
from pymysql.converters import decoders
from pymysql.converters import encoders, decoders, convert_mysql_timestamp


class ORMFixture:
    db = Database()

    class ORMGroup(db.Entity):
        _table_ = 'group_list'
        id = PrimaryKey(int, column='group_id')
        name = Optional(str, column='group_name')
        header = Optional(str, column='group_header')
        footer = Optional(str, column='group_footer')
        contacts = Set(
            lambda: ORMFixture.ORMContact,
            table="address_in_groups",
            column="id",
            reverse="groups",
            lazy=True
        )

    class ORMContact(db.Entity):
        _table_ = 'addressbook'
        id = PrimaryKey(int, column='id')
        firstname = Optional(str, column='firstname')
        lastname = Optional(str, column='lastname')
        nickname = Optional(str, column='nickname')
        home_phone = Optional(str, column='home')
        mobile_phone = Optional(str, column='mobile')
        work_phone = Optional(str, column='work')
        secondary_phone = Optional(str, column='phone2')
        email = Optional(str, column='email')
        email2 = Optional(str, column='email2')
        email3 = Optional(str, column='email3')
        deprecated = Optional(str, column='deprecated')
        groups = Set(
            lambda: ORMFixture.ORMGroup,
            table="address_in_groups",
            column="group_id",
            reverse="contacts",
            lazy=True
        )

    def __init__(self, host, db, user, password):
        conv = encoders
        conv.update(decoders)
        conv[datetime] = convert_mysql_timestamp
        self.db.bind('mysql', host=host, db=db, user=user, password=password, conv=conv)
        self.db.generate_mapping()
        # sql_debug(True) # Debug

    def convert_groups_to_model(self, groups):
        def convert_group(group):
            return Group(id=str(group.id), name=group.name, header=group.header, footer=group.footer)
        return list(map(convert_group, groups))

    @db_session
    def get_group_list(self):
        return self.convert_groups_to_model(select(g for g in ORMFixture.ORMGroup))

    def get_group_by_name(self, name):
        return self.convert_groups_to_model(select(g for g in ORMFixture.ORMGroup if g.name == name))[0]

    @db_session
    def get_contact_list(self):
        return self.convert_contacts_to_model(select(c for c in ORMFixture.ORMContact if c.deprecated is None))

    def convert_contacts_to_model(self, contacts):
        def convert_contact(contact):
            return Contact(
                id=str(contact.id),
                firstname=contact.firstname,
                lastname=contact.lastname,
                nickname=contact.nickname,
                home_phone=contact.home_phone,
                mobile_phone=contact.mobile_phone,
                work_phone=contact.work_phone,
                secondary_phone=contact.secondary_phone,
                email=contact.email,
                email2=contact.email2,
                email3=contact.email3
            )
        return list(map(convert_contact, contacts))

    @db_session
    def get_contacts_in_group(self, group):
        orm_group = list(select(g for g in ORMFixture.ORMGroup if g.id == group.id))[0]
        return self.convert_contacts_to_model(orm_group.contacts)

    @db_session
    def get_contacts_not_in_group(self, group):
        orm_group = list(select(g for g in ORMFixture.ORMGroup if g.id == group.id))[0]
        return self.convert_groups_to_model(select(c for c in ORMFixture.ORMContact if c.deprecated is None and orm_group not in c.groups))
