from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

# SQLAlchemy: Python中的SQL工具包和对象关系映射器，方便用python操作数据库
# 避免：cursor.execute("SELECT * FROM users WHERE name = '" + username + "'")
# 改为：session.query(User).filter_by(name="Alice").first()
# 增删改查等操作不需要写SQL语句，只需要操作对象
# python --- SQLAlchemy --- SQL语句