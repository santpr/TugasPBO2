import pymysql
from flaskext.mysql import MySQL
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps
import mysql.connector
import json
import requests

app = Flask(__name__)
mysql = MySQL(app)
#app.config['DEBUG'] = True

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'dbase'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
mysql.init_app(app)

def checkKey(dict, key):
#mengembalikan true jika key ada di dictionary dan false jika tidak
    if key in dict: 
        return True
    else: 
        return False

def isiDbase():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    for i in range (137000, 137100):
    #melakukan pencarian sesuai range yang ditetapkan
        try :
            url = 'https://webpac.lib.itb.ac.id/index.php/marc/view/{}/JSON'.format(i)

            #memasukkan data JSON ke variabel data
            data = requests.get(url)
            data = json.loads(data.text)

            #mencari Judul (Jika tidak ada diberi nilai null)
            for j in range (0, len(data[0]['fields'])):
                if checkKey(data[0]['fields'][j],'245') :
                    Judul = data[0]['fields'][j]['245']['subfields'][0]['a']
                    break
                else :
                    Judul = "null"
                    
            #mencari ISBN (Jika tidak ada diberi nilai null)
            for j in range (0, len(data[0]['fields'])):
                if checkKey(data[0]['fields'][j],'020') :
                    ISBN = data[0]['fields'][j]['020']['subfields'][0]['a']
                    break
                else :
                    ISBN = "null"

            #mencari Penulis (Jika tidak ada diberi nilai null)
            for j in range (0, len(data[0]['fields'])):
                if checkKey(data[0]['fields'][j],'100') :
                    Penulis = data[0]['fields'][j]['100']['subfields'][0]['a']
                    break
                else :
                    Penulis = "null"

            #mencari Penerbit dan Tahun Terbit (Jika tidak ada diberi nilai null)
            for j in range (0, len(data[0]['fields'])):
                if checkKey(data[0]['fields'][j],'260') :
                    Penerbit = data[0]['fields'][j]['260']['subfields'][1]['b']
                    Tahun_terbit = data[0]['fields'][j]['260']['subfields'][2]['c']
                    break
                else :
                    Penerbit = "null"
                    Tahun_terbit = "null"

            #insert into database
            instance = (Judul, ISBN, Penulis, Penerbit, Tahun_terbit)
            query = """INSERT INTO book(
                Judul,
                ISBN,
                Penulis,
                Penerbit,
                Tahun_terbit
                )
                Values (%s,%s,%s,%s,%s)"""
            cursor.execute(query, instance)

        #menghandle exception
        except Exception as e:
            print(e)
            continue

    conn.commit()
    
    cursor.close()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    #mengambil dari database
    global cursor, conn
    if request.method == 'GET':
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("select * from book")
            res = cursor.fetchall()
        except Exception as e:
            return e
        finally:
            cursor.close()
            conn.close()
    else:
        res = [{
            'status': 201,
            'message': 'Failed',
        }]
        
    return jsonify({'result': res})

@app.route('/admin/', methods=['POST','DELETE','PUT'])
def change():
    global cursor, conn
    #mengupload ke database
    if request.method == 'POST':
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            judul = request.args.get('judul')
            isbn = request.args.get('isbn')
            penulis = request.args.get('penulis')
            penerbit = request.args.get('penerbit')
            tahun_terbit = request.args.get('tahun_terbit')
            total = request.args.get('total')
            tersedia = request.args.get('tersedia')
            sedang_dipinjam = request.args.get('sedang_dipinjam')

            query = "INSERT INTO book(Judul, ISBN, Penulis, Penerbit, tahun_terbit, Sedang_dipinjam, Tersedia, total) VALUES(%s,%s,%s,%s,%s,%d,%d,%d)"

            data = (judul, isbn, penulis, penerbit, tahun_terbit, sedang_dipinjam, tersedia, total)
            cursor.execute(query, data)
            conn.commit()
            res = {
                'message' : 'Success',
                'data': {
                    'Judul' : judul,
                    'ISBN' : isbn,
                    'Penulis' : penulis,
                    'Penerbit' : penerbit,
                    'Tahun_terbit' : tahun_terbit,
                    'Sedang_dipinjam' : sedang_dipinjam,
                    'Tersedia' : tersedia,
                    'Total' : total
                    }
                }

        except Exception as e:
            return e
        finally:
            cursor.close()
            conn.close()

    #menghapus dari database
    elif request.method == 'DELETE':
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            data = request.args.get('judul')
            query = """DELETE FROM book WHERE judul=%s"""
            cursor.execute(query, data)
            conn.commit()
            res = [{
            'status': 200,
            'message': "Deleted"
            }]
            return jsonify(res)
        except Exception as e:
            return e
        finally:
            cursor.close()
            conn.close()

    #mengubah entri database
    elif request.method == 'PUT':
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            judul = request.args.get('judul')
            isbn = request.args.get('isbn')
            penulis = request.args.get('penulis')
            penerbit = request.args.get('penerbit')
            tahun_terbit = request.args.get('tahun_terbit')
            total = request.args.get('total')
            tersedia = request.args.get('tersedia')
            sedang_dipinjam = request.args.get('sedang_dipinjam')

            query = "UPDATE book SET ISBN=%s, Penulis=%s, Penerbit=%s, tahun_terbit=%s, Sedang_dipinjam=%d, Tersedia=%d, total=% WHERE Judul=%s"
            data = (isbn,penulis,penerbit,tahun_terbit, sedang_dipinjam, tersedia, total, judul)
            cursor.execute(query,data)
            conn.commit()

            res = {
                'message' : 'Success',
                'data': {
                    'Judul' : judul,
                    'ISBN' : isbn,
                    'Penulis' : penulis,
                    'Penerbit' : penerbit,
                    'tahun_terbit' : tahun_terbit,
                    'Sedang_dipinjam' : sedang_dipinjam,
                    'Tersedia' : tersedia,
                    'Total' : total
                    }
                }  
        except Exception as e:
            return e
        finally:
            cursor.close()
            conn.close()
            
    else:
        res = [{
            'status': 201,
            'message': 'Failed',
        }]
        
    return jsonify({'result': res})



@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.errorhandler(405)
def not_found(error=None):
    message = {
        'status': 405,
        'message': 'Method ' + request.method + ' is not allowed',
    }
    resp = jsonify(message)
    resp.status_code = 405

    return resp

if __name__ == '__main__':
    isiDbase()
    app.run()
