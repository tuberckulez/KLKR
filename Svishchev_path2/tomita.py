from pymongo import MongoClient
import os

client = MongoClient("mongodb+srv://makeev:makeev@cluster0.38igd.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = client["db"]
collection = database["news"]

for news in collection.find( {} ):
    with open("input.txt","w") as f:
        f.write(news['text_news'])

    os.system("/home/vagrant/tomita-parser/build/bin/tomita-parser config.proto")

    person = []
    object = []
    place = ""

    with open("/home/vagrant/spark_laba/output.txt","r") as f:
        foutput = f.read()
        words = foutput.split()
        for i in range(len(words)):
            if words[i] == "People_output":
                if words[i+2] not in person:
                    person.append(words[i+2])
            elif words[i] == "Buildings_output":
                while words[i+2] != "}":
                    place += " " + words[i+2]
                    i+=1
                if place not in object:
                    object.append(place)
                    place = ""


    for i in range(len(person)):            
        collection.update({
                "_id": news["_id"]
            }, {
                "$pull": {
                "Person": person[i] 
                }
            }) 

    for i in range(len(object)):            
        collection.update({
                "_id": news["_id"]
            }, {
                "$pull": {
                "Object": object[i] 
                }
            }) 

    for i in range(len(person)):
        collection.update({
            "_id": news["_id"]
        }, {
            "$push": {
            "Person": person[i] 
            }
        }) 
    
    for i in range(len(object)):
        collection.update({
            "_id": news["_id"]
        }, {
            "$push": {
            "Object": object[i] 
            }
        }) 

    person.clear()
    object.clear()






