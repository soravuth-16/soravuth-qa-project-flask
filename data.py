from app.model import *

Samnang = MKT_QUESTION(Title="hello",Body="welcome",Tag="hello",Vote=1,User=1,BestAnswer=1)


print(f">>>>>>>{Samnang}")
with app.app_context():
    db.session.add(Samnang)
    db.session.commit()