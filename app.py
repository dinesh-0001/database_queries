from flask import Flask, render_template, request
import mysql.connector as connection
import pandas as pd
import csv

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("main.html")

@app.route("/dbms_connection", methods=['POST'])
def get_connection():
    if request.method == 'POST':
        db = request.form['DBMS_connector']
        if db == 'MySQL':
            return render_template('sql_connector_credentials.html')

@app.route("/sql_connection", methods=['Post'])
def sql_connector():
    if request.method == 'POST':
    #storing the data of sql connection credentials
        global host
        global user
        global pwd
        host = request.form.get('host')
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        try:
            mydb = connection.connect(host = host, user = user, password = pwd, use_pure = True)
            conn = True
            if conn:
                return render_template("establish_connection.html")
        except connection.Error as e:
            # If connection fails, return the error message in HTML format centered in an h1 heading
            return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>{e.msg}</h1></div>"
    
@app.route('/operations_mysql', methods=['Post'])
def operations_mysql():
    if request.method == 'POST':
        operation = request.form['operation']
        # this is for showing the database present in my_sql
        if operation == 'show_dbs':
            try:
                mydb = connection.connect(host = host, user = user, password = pwd, use_pure = True)
                query = "SHOW Databases"
                cur = mydb.cursor()
                cur.execute(query)
                df = pd.DataFrame(cur.fetchall(), columns = ['Databases'])
                cur.close()
                mydb.close()
                table_html = df.to_html(classes='table table-striped', index=False)
                return render_template('dataframe_render.html', table=table_html)
            except Exception as e:
                mydb.close()
                print(str(e))

        # this operation is used for redirecting to create_database page where new database is created
        if operation == 'create_databases':
            return render_template('create_database.html')
        
        # this will redirect to the queries page
        if operation == 'predefined_queries':
            return render_template('query.html')
        
        #this will redirect to create new table name page
        if operation == 'create_table':
            return render_template('create_table.html')
        
        # this will give permission to write custom queries
        if operation == 'custom_query':
            return render_template('custom_query.html')
            

# this function is used for creating a new database
@app.route('/insert_new_database', methods = ['POST'])
def insert_new_database():
    if request.method == 'POST':
        database_name = request.form['database_name']
        try:
            mydb = connection.connect(host = host, user = user, password = pwd, use_pure = True)
            cur = mydb.cursor()
            query = f"CREATE DATABASE {database_name}"
            cur.execute(query)
            return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Database {database_name} created successfully.</h1></div>"    
        except connection.Error as err:
            if err.errno == connection.errorcode.ER_DB_CREATE_EXISTS:
                return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Database {database_name} already exists.</h1></div>"
                
            else:
                return f"Error: {err}"
        finally:
            cur.close()
            mydb.close()

#this will define the pre-defined queries
@app.route('/queries', methods = ['POST'])
def queries():
    if request.method == 'POST':
        #try:
            global qdatabase_name
            qdatabase_name = request.form['qdatabase_name']
            #this is for validating the database exist or not
            try:
                # Attempt to validate the database name
                connection.connect(host = host, database = qdatabase_name, user = user, password = pwd, use_pure = True)
                res = True
            except connection.Error as err:
                if err.errno == connection.errorcode.ER_BAD_DB_ERROR:
                # The error code indicates an invalid database name
                    res = False
                else:
                # Other errors may occur, handle them as needed
                    raise
            
            
            if res:
                table = get_table_names(qdatabase_name)
                query = request.form['query']
                template_mapping = {
                    'Select_operation': 'select_operation.html',
                    'Insertion_operation': 'insert_operation.html',
                    'Update_operation': 'update_operation.html',
                    'Delete_operation': 'delete_operation.html'
                }
                if query in template_mapping:
                    template_name = template_mapping[query]
                    return render_template(template_name, tables = table)
            
    
            else :
                return "<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Enter the valid Database Name.</h1></div>"
        # except Exception as e:
        #         print(str(e))
    

#this function will be used for custom query
@app.route('/custom_query', methods=['POST'])
def custom_query():
    if request.method == 'POST':
    
            database = request.form['database_name']
            
            try:
                # Attempt to validate the database name
                connection.connect(host = host, database = database, user = user, password = pwd, use_pure = True)
                res = True
            except connection.Error as err:
                if err.errno == connection.errorcode.ER_BAD_DB_ERROR:
                # The error code indicates an invalid database name
                    res = False
                else:
                # Other errors may occur, handle them as needed
                    raise
            
            if res:
                mydb = connection.connect(host = host, database = database, user = user, password = pwd, use_pure = True)
                cur = mydb.cursor()
                query = request.form['custom_query']
                result = pd.read_sql(query, mydb)
                return render_template('result.html', query_result=result, query=query)
            else:
                return "<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Enter the valid Database Name.</h1></div>"
            
       

#this function will return the select operation data from sql    
@app.route("/selection_operations_detail", methods = ['POST'])
def selection_operations_detail():
    if request.method == 'POST':
        try:
            mydb = connection.connect(host = host, database = qdatabase_name, user = user, password = pwd, use_pure = True)
            cur = mydb.cursor()
        
            operation = request.form['operation']
            table_name = request.form['table']
            where = request.form['where-condition']
            if where == "":
                if operation == 'all':
                    query = f'SELECT * FROM {table_name}'
                    result = pd.read_sql(query, mydb)
                
                    return render_template('result.html', query_result=result, query=query)
                if operation != 'all':
                    column_name = request.form['input-text']
                    query = f'SELECT {operation}({column_name}) FROM {table_name}'
                    result = pd.read_sql(query, mydb)
            
                    return render_template('result.html', query_result=result, query=query)
            else:
                if operation == 'all':
                    query = f'SELECT * FROM {table_name} WHERE {where}'
                    result = pd.read_sql(query, mydb)
                
                    return render_template('result.html', query_result=result, query=query)
                if operation != 'all':
                    column_name = request.form['input-text']
                    query = f'SELECT {operation}({column_name}) FROM {table_name} WHERE {where}'
                    result = pd.read_sql(query, mydb)
            
                    return render_template('result.html', query_result=result, query=query)
            cur.close()
            mydb.close()
        except:
            return "Error in function"
            cur.close()
            mydb.close()

#this will handle the insertion operations and excute or return error (if any) while executing
@app.route("/insertion_operations_detail", methods = ["Post"])
def insertion_operations_detail():
    if request.method == 'POST':
        insert_operation_type = request.form["insert_operation"]
        table = request.form["table"]
        if insert_operation_type == "single_insert_operation":
            value_form = request.form.getlist("single_insert_value")
            value = list(value_form)
            try:
                mydb = connection.connect(host = host, database = qdatabase_name, user = user, password = pwd, use_pure = True)
                cur = mydb.cursor()
                num_columns = col_size(table)
                padded_values = pad_values(value, num_columns)
                query = f"INSERT INTO {table} VALUES (" + ",".join(["%s"] * num_columns) + ")"
                cur.execute(query, padded_values)
                mydb.commit()
                mydb.close()
                cur.close()
                return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Successfully Inserted Values {padded_values}.</h1></div>"
            except:
                return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Error Occured {padded_values}.</h1></div>"

            
        if insert_operation_type == "multiple_insert_operation":
            multiple_values = request.form.getlist("multiple_insert_values[]")
            values = tuple(tuple(map(str.strip, element.split(","))) for element in multiple_values)
            try:
                mydb = connection.connect(host = host, database = qdatabase_name, user = user, password = pwd, use_pure = True)
                cur = mydb.cursor()
                num_columns = col_size(table)
                padded_values = [pad_row(row, num_columns) for row in values]
                query = f"INSERT INTO {table} VALUES (" + ",".join(["%s"] * num_columns) + ")"
                cur.executemany(query, padded_values)
                mydb.commit()
                cur.close()
                mydb.close()
                return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Successfully Inserted Values {padded_values}.</h1></div>"
            except:
                return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Error Occured {padded_values}.</h1></div>"

        if insert_operation_type == "csv_insert_operation":
            if 'csv_file' not in request.files:
                return 'No file uploaded', 400

            file = request.files['csv_file']

            # Check if file is empty
            if file.filename == '':
                return 'No selected file', 400

            if file:
                # Read the CSV file
                csv_data = file.stream.read().decode("utf-8")
        
                # Parse CSV data
                csv_reader = csv.reader(csv_data.splitlines())
        
                # Process CSV rows
                for row in csv_reader:
                    return f"{row}"

#this route is for updating the values of table given by user
@app.route("/update_operation_detail", methods = ['POST'])
def update_operation_detail():
    if request.method == 'POST':
        table = request.form["table"]
        set = request.form['set']
        where = request.form['where']
        try:
            mydb =  connection.connect(host = host, user = user, database = qdatabase_name, password = pwd, use_pure = True)
            cur = mydb.cursor()
            query = f"UPDATE {table} SET {set} WHERE {where}"
            cur.execute(query)
            mydb.commit()
            cur.close()
            mydb.close()
            return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Succesfully Updated the Values : {set}.</h1></div>"
        except:
            return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Error in the values : {set} Where: {where}.</h1></div>"

#this will delete and drop the rows, columns, tables and databases
@app.route('/delete_operation_details', methods = ['POST'])    
def delete_operation_details():
    if request.method == 'POST':
        operation_type = request.form['delete_drop_operation']
        if operation_type == "delete_operation":
            table = request.form['table']
            where = request.form['where']
            try:
                mydb = connection.connect(host = host, user = user, database = qdatabase_name, password = pwd, use_pure = True)
                cur = mydb.cursor()
                query = f"DELETE FROM {table} WHERE {where}"
                cur.execute(query)
                mydb.commit()
                cur.close()
                mydb.close()
                return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Values are Deleted : {where} From Table: {table}.</h1></div>"
            except:
                return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Error in the values : {where}.</h1></div>"
        if operation_type == "drop_operation":
            drop_operation_type = request.form['drop_operation_type']
            if drop_operation_type == "database_drop":
                database = request.form['database_name']
                try:
                      mydb = connection.connect(host = host, user = user, password = pwd, use_pure = True)
                      cur = mydb.cursor()
                      query = f"DROP DATABASE {database}" 
                      cur.execute(query)
                      mydb.commit()
                      cur.close()
                      mydb.close()
                      return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Database {database} Deleted from MySQL</h1></div>"
                except:
                    return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Enter Valid Database Name</h1></div>"
            if drop_operation_type == "table_drop":
                table = request.form['table_name']
                try:
                      mydb = connection.connect(host = host, user = user, database = qdatabase_name, password = pwd, use_pure = True)
                      cur = mydb.cursor()
                      query = f"DROP TABLE {table}" 
                      cur.execute(query)
                      mydb.commit()
                      cur.close()
                      mydb.close()
                      return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Table {table} Deleted from Database {qdatabase_name}</h1></div>"
                except:
                    return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Enter Valid Table Name</h1></div>"
            if drop_operation_type == 'column_drop':
                table = request.form['table_name']
                column = request.form['column_name']
                try:
                      mydb = connection.connect(host = host, user = user, database = qdatabase_name, password = pwd, use_pure = True)
                      cur = mydb.cursor()
                      query = f"ALTER TABLE {table} Drop COLUMN {column}" 
                      cur.execute(query)
                      mydb.commit()
                      cur.close()
                      mydb.close()
                      return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Column {column} Deleted from Table {table}</h1></div>"
                except:
                    return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Enter Valid Table Name</h1></div>"

#this is used to create a new table name in database
@app.route('/insert_new_table', methods = ["POST"])
def insert_new_table():
    if request.method == 'POST':
        database = request.form['database_name']
        try:
            # Attempt to validate the database name
            connection.connect(host = host, database = database, user = user, password = pwd, use_pure = True)
            res = True
        except connection.Error as err:
            if err.errno == connection.errorcode.ER_BAD_DB_ERROR:
            # The error code indicates an invalid database name
                res = False
            else:
                # Other errors may occur, handle them as needed
                raise
            
        if res:
            table = request.form['table_name']
            schema = request.form['schema']
            mydb = connection.connect(host = host, database = database, user = user, password = pwd, use_pure = True)
            cur = mydb.cursor()
            query = f"CREATE TABLE IF NOT EXISTS {table} ({schema})"
            cur.execute(query)
            mydb.commit()
            cur.close()
            mydb.close()
            
            return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Table : {table} Created Successfully in Database {database}.</h1></div>"
           
        else:
            return f"<div style='display: flex; justify-content: center; align-items: center; height: 100vh;'><h1>Enter the valid Database Name.</h1></div>"
           

#this function will take you to the homepage
@app.route('/go_to_homepage', methods = ['GET'])
def go_to_homepage():
    return render_template("main.html")

#this function will take you to the operation page
@app.route('/go_to_operation', methods = ['GET'])
def go_to_operation():
    return render_template('establish_connection.html')

 #this is for retreiving the table_names from giving database name
def get_table_names(database_name):
   
        try:
            mydb = connection.connect(host = host, database = database_name, user = user, password = pwd, use_pure = True)
            cur = mydb.cursor()
            cur.execute('SHOW TABLES')
            tables = cur.fetchall()
            cur.close()
            mydb.close()
            # return the table names
            return [table[0] for table in tables]
        except:
            cur.close()
            mydb.close()

#this function will return the column size
def col_size(table_name):
    mydb = connection.connect(host = host, database = qdatabase_name, user = user, password = pwd, use_pure = True)
    cur = mydb.cursor()
    cur.execute(f"DESCRIBE {table_name}")
    column_names = [row[0] for row in cur.fetchall()]
    num_columns = len(column_names)
    return num_columns
    

#this function is used to enter the None Values to the if any value is not inserted by user
def pad_row(values, num_columns):
    return tuple(values) + (None,) * (num_columns - len(values))

def pad_values(values, num_columns):
    # Split the string into individual values
    values_split = values[0].split(",")
    # Pad with None values
    padded_values = values_split + [None] * (num_columns - len(values_split))
    return tuple(item.strip() if item is not None else None for item in padded_values)


if __name__ == '__main__':
    app.run()