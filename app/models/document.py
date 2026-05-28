from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    # primary_key=True：声明这是表的主键
    # lambda 匿名函数：它变成了一个“延迟执行的函数”。只有在每次执行 session.add(new_doc) 真正要插入新数据时，SQLAlchemy 才会临时调用一次这个函数，确保每次生成的 UUID 都是全新的

    document_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
    )
    # unique=True：要求这一列的数据在整个表里必须唯一，如果有两个相同的 document_id 尝试写入，数据库会直接拒绝并报错。
    # index=True：性能关键！ 为这一列建立 B-Tree 索引，加速查找

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    saved_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # str | None: 这个变量“既可以是字符串，也可以是空（None）
    # nullable=True：对应的 SQL 语法，允许这一列在数据库里存入 NULL 值

    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    text_length: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_count: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="indexed")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # 自动化时间戳钩子hooks
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    # default=datetime.utcnow：当这行数据第一次被创建（Insert）时，自动填入当前的 UTC 时间。注意，这里传入的是函数名 datetime.utcnow（没有括号）
    # onupdate=datetime.utcnow：SQLAlchemy监听器。当这行数据被修改（Update）时（比如状态从 pending 变成了 indexed），自动帮你把当前时间填入这个字段


    # 说明： 对象（Object） - 关系（Relational） 映射
    # Python 的 类 (Class) DocumentModel -> 数据库的 表 (Table) documents
    # 结构映射：Python 类的 属性 (Attributes) original_filename, status -> 数据库表的 列 (Columns)。
    # 数据映射：Python 类的 实例对象 (Instance) doc = DocumentModel(...) -> 数据库表里的 一行真实数据 (Row)。

    # 字段名: Mapped[Python类型] = mapped_column(数据库类型, 各种约束)
    # 例如: id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))