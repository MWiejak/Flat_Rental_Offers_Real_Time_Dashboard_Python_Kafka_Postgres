from connect import connect

def create_table_if_doesnt_exist():

    conn = connect() 
    cursor = conn.cursor()

    print("Checking if flats table exists...")

    sql1 = '''SELECT EXISTS (
        SELECT FROM 
            information_schema.tables 
        WHERE 
            table_schema LIKE 'public' AND 
            table_type LIKE 'BASE TABLE' AND
            table_name = 'flats'
        );'''

    cursor.execute(sql1)
    exists = cursor.fetchone()[0]

    if not exists:

        print("Flats table doesn't exist. Creating...")
        sql ='''CREATE TABLE flats(
        url CHAR(500) PRIMARY KEY,
        location VARCHAR,
        date DATE,
        size REAL,
        price INT
    )'''
        cursor.execute(sql)
        print("Flats table created!")

    print("Checking done.")
    conn.commit()
    conn.close()
