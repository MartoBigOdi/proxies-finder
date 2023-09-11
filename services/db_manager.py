import sqlite3


def create_connection():
    """
        Crea una conexión a la base de datos SQLite "vips.db"
    """
    try:
        conn = sqlite3.connect('proxys.db')
        return conn
    except Exception as e:
        print(e)
        raise e


def create_tables(conn):
    """ Crea las tablas de la base de datos"""
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS proxy
                    (ip_port text, success_count integer, fail_count integer, last_sucess datetime, last_fail datetime, status integer)''')
        conn.commit()
    except Exception as e:
        print(e)
        raise e


def insert_proxy(conn, ip_port, success_count, fail_count, last_sucess, last_fail, status):
    """
    Crea un nuevo registro en la tabla "proxy"
    :param conn:
    :param ip_port:
    :return: ip_port id
    """
    sql = ''' INSERT INTO proxy(ip_port, success_count, fail_count, last_sucess, last_fail, status)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (ip_port, success_count, fail_count, last_sucess, last_fail, status))
    conn.commit()
    return cur.lastrowid


def update_status(conn, ip_port, status):
    """
    Actualiza el status de un proxy en la tabla "proxy"
    :param conn:  el objeto Connection
    :param ip_port: el ip_port del proxy a actualizar
    :return:
    """
    sql = 'UPDATE proxy SET status=? WHERE ip_port=?'
    cur = conn.cursor()
    cur.execute(sql, (status, ip_port))
    conn.commit()


def is_proxy_exist(conn, ip_port):
    """
    Verifica si un proxy existe en la tabla "proxy"
    :param conn:  el objeto Connection
    :param ip_port: el ip_port del proxy a verificar
    :return: True si existe, False si no
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM proxy WHERE ip_port=?", (ip_port,))
    rows = cur.fetchall()
    return len(rows) > 0


def AddProxy(ip_port):
    """
    Crea una nueva conexión a la base de datos y agrega un nuevo proxy
    :param ip_port:
    :return: ip_port id
    """
    try:
        conn = create_connection()
        with conn:
            create_tables(conn)
            insert_proxy(conn, ip_port, 0, 0, None, None, 0)
    except Exception as e:
        print(e)
        raise e


def AddProxyList(proxy_list):
    """
    Crea una nueva conexión a la base de datos y agrega una lista de proxys
    :param ip_port:
    :return: ip_port id
    """
    try:
        conn = create_connection()
        with conn:
            create_tables(conn)
            for proxy in proxy_list:
                insert_proxy(conn, proxy, 0, 0, None, None, 0)
       
    except Exception as e:
        print(e)
        raise e


def FilterExistingProxys(proxy_list):
    """
    Crea una nueva conexión a la base de datos y filtra los proxys que ya existen
    :param ip_port:
    :return: ip_port id
    """
    try:
        print("Filtrando proxys existentes...")
        conn = create_connection()
        with conn:
            create_tables(conn)
            new_list = []
            for proxy in proxy_list:
                if not is_proxy_exist(conn, proxy):
                    new_list.append(proxy)
            print("Se filtraron los proxy. Los nuevos proxy a evaluar son " + str(len(new_list)) + " de " + str(len(proxy_list)))
            return new_list
    except Exception as e:
        print(e)
        raise e


def UpdateProxyStatus(ip_port, status):
    """
    Crea una nueva conexión a la base de datos y actualiza el status de un proxy
    :param ip_port:
    :return: ip_port id
    """
    try:
        conn = create_connection()
        with conn:
            update_status(conn, ip_port, status)
    except Exception as e:
        print(e)
        raise e
    