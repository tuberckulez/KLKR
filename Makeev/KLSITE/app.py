from flask import Flask, render_template, request, jsonify, make_response
import time
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://makeev:makeev@cluster0.38igd.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = client["db"]
collection = database["news"]
synonyms = database["synonims"]
res = database.collection.count_documents({})

app.config['JSON_AS_ASCII'] = False

all_news = list(collection.find().sort('_id', 1))
all_synonyms = list(synonyms.find().sort('_id', 1))

db = []
db2 = []
db3 = []
posts = res
a = 0

quantity = 10

for item in all_news:
    news_title = item['name_news']
    news_description = item['text_news']
    news_link = item['link_news']
    news_date = item['date_news']
    news_person = ""
    news_object = ""
    news_tonality = ""
    no_person = ""
    no_object = ""
    no_tonality = ""
    try:
        if item["Person"]:
            news_person = item["Person"][0]
        if item["Object"]:
            news_object = item["Object"][0]
        if item["tonality"]:
            news_tonality = item["tonality"][0]

    except:
        print("")

    if news_person:
        a = 0
    else:
        no_person = "Нет персон"

    if news_object:
        a = 0
    else:
       no_object = "Нет достопримечательностей"

    if news_tonality:
        a = 0
    else:
        no_tonality = "Нет тональности"

    string = [news_title, news_description, news_link, news_date, news_person, news_object, news_tonality]
    db.append(string)



for item in all_synonyms:
    name = item['name']
    sinonim = item['synonym']
    db3.append(["".join(name), "".join(sinonim)])

@app.route("/")
def index():
    """ Route to render the HTML """
    return render_template("index.html")

@app.route("/synonym", methods=['GET', 'POST'])
def sinonim():
    return render_template("synonym.html")

@app.route("/load")
def load():
    """ Route to return the posts """

    time.sleep(0.2) 

    if request.args:
        counter = int(request.args.get("c"))  

        if counter == 0:
            print(f"Returning posts 0 to {quantity}")
           
            res = make_response(jsonify(db[0: quantity]), 200)

        elif counter == posts:
            print("No more posts")
            res = make_response(jsonify({}), 200)

        else:
            print(f"Returning posts {counter} to {counter + quantity}")
           
            res = make_response(jsonify(db[counter: counter + quantity]), 200)

    return res
@app.route("/load1")
def load1():
    """ Route to return the posts """

    time.sleep(0.2)  

    if request.args:
        counter = int(request.args.get("c"))  

        if counter == 0:
            print(f"Returning posts 0 to {quantity}")
            
            res = make_response(jsonify(db2[0: quantity]), 200)

        elif counter == posts:
            print("No more posts")
            res = make_response(jsonify({}), 200)

        else:
            print(f"Returning posts {counter} to {counter + quantity}")
            
            res = make_response(jsonify(db2[counter: counter + quantity]), 200)
    return res

@app.route("/load2")
def load2():
    """ Route to return the posts """

    time.sleep(0.2)  

    if request.args:
        counter = int(request.args.get("c"))  

        if counter == 0:
            print(f"Returning posts 0 to {quantity}")
            
            res = make_response(jsonify(db3[0: quantity]), 200)

        elif counter == posts:
            print("No more posts")
            res = make_response(jsonify({}), 200)

        else:
            print(f"Returning posts {counter} to {counter + quantity}")
            
            res = make_response(jsonify(db3[counter: counter + quantity]), 200)
    return res

if __name__ == '__main__':
    app.run(debug=True)