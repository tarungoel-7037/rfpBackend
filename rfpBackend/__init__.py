import pymysql

# Django 6 checks the MySQLdb client version during backend startup.
# When PyMySQL is used as a drop-in replacement, expose a compatible
# version tuple/string so the backend can proceed.ls
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.__version__ = "2.2.1"

pymysql.install_as_MySQLdb()
