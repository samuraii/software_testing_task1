import random
from model.data import Contact

def test_edit_group_data(app):
    app.session.login('admin', 'secret')
    name  = random.randint(1, 100)
    app.contact.edit_data(Contact(firstname='firstname{}'.format(name), lastname='lastname', nickname='nickname{}'.format(name)))
    app.session.logout()