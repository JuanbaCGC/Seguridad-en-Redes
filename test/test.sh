#!/bin/bash

#Get version of the program
echo "Getting the version of the program..."
curl --silent -X GET https://127.0.0.1:5000/version
echo -e "\n"

# Create differents users
echo "Creating differents users with differents names..."
token1=$(curl --silent -X POST -d '{"username":"Juanba","password":"Juanba++1"}' https://127.0.0.1:5000/signup | jq -r '.access_token')
token2=$(curl --silent -X POST -d '{"username":"Arturo","password":"Arturo+1"}' https://127.0.0.1:5000/signup | jq -r '.access_token')
token3=$(curl --silent -X POST -d '{"username":"Alberto","password":"Alberto+1"}' https://127.0.0.1:5000/signup | jq -r '.access_token')

echo "Creating a repeated user..."
curl --silent -X POST -d '{"username":"Juanba","password":"Juanba++1"}' https://127.0.0.1:5000/signup
echo -e "\n"

echo "Triying a login with a wrong password..."
curl --silent -X POST -d '{"username":"Juanba","password":""}' https://127.0.0.1:5000/signup
echo -e "\n"

echo "Doing a login with correct username and password..."
curl --silent -X POST -d '{"username":"Arturo","password":"Arturo+1"}' https://127.0.0.1:5000/login
echo -e "\n"

#Post a document for each user
echo "Posting a document for Juanba..."
curl -X POST -H "Authorization:token $token1" -d '{"doc_content":{
    "id": 44,
    "game": "Colonos de Catan",
    "author": "Klaus Teuber",
    "ages": "10+"
}}' https://127.0.0.1:5000/Juanba/doc1
echo -e "\n"

echo "Posting a document for Arturo..."
curl -X POST -H "Authorization:token $token2" -d '{"doc_content":{
  "name": "John",
  "age": 30,
  "car": null
}}' https://127.0.0.1:5000/Arturo/John
echo -e "\n"

echo "Posting a document for Alberto..."
curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{
    "id": 44,
    "game": "Colonos de Catan"
}}' https://127.0.0.1:5000/Alberto/AlbertoDocument
echo -e "\n"

echo "Posting a document for Alberto without a Json struct..."
curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{
    "id": 44,
    "game": "Colonos de Catan"
}' https://127.0.0.1:5000/Alberto/AlbertoDocument2
echo -e "\n"

echo "Posting a document for Alberto without a Json struct..."
curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{  
    "employee": {  
        "name":       "sonoo",   
        "salary":      56000,   
        "married":    true  
    }  
}  ' https://127.0.0.1:5000/Alberto/newDoc
echo -e "\n"

echo "Posting two new documents for Alberto..."
curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{  
    "employee": {  
        "name":       "sonoo",   
        "salary":      56000,   
        "married":    true  
    }  
}  }' https://127.0.0.1:5000/Alberto/Information
curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{
  "llave1": "valor1",
  "llave2": "valor2",
  "llave3": "valor3",
  "llave4": 7,
  "llave5": null,
  "favAmigos": ["Kolade", "Nithya", "Dammy", "Jack"],
  "favJugadores": {"uno": "Kante", "dos": "Hazard", "tres": "Didier"}
}}' https://127.0.0.1:5000/Alberto/doc1
echo -e "\n"

echo "Getting all the documents of Alberto..."
curl --silent -X GET -H "Authorization:token $token3" https://127.0.0.1:5000/Alberto/_all_docs
echo -e "\n"

echo "Deleting a document of Alberto that exists..."
curl --silent -X DELETE -H "Authorization:token $token3" https://127.0.0.1:5000/Alberto/Information
echo -e "\n"

echo "Deleting a document of Alberto that does not exists..."
curl --silent -X DELETE -H "Authorization:token $token3" https://127.0.0.1:5000/Alberto/name
echo -e "\n"

echo "Getting all the documents of Alberto again..."
curl --silent -X GET -H "Authorization:token $token3" https://127.0.0.1:5000/Alberto/_all_docs
echo -e "\n"

echo "Updating a document of Alberto with new content..."
curl -X PUT -H "Authorization:token $token3" -d '{"doc_content":{  
    "Seguridad": {  
        "aprobados":       100,   
        "suspensos":      0,   
        "matricula":    true  
    }  
}  }' https://127.0.0.1:5000/Alberto/doc1
echo -e "\n"

echo "Geting the updated document of Alberto..."
curl --silent -X GET -H "Authorization:token $token3" https://127.0.0.1:5000/Alberto/doc1

echo "Trying to post more than 5 documents..."
curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{  
    "employee": {  
        "name":       "sonoo",   
        "salary":      56000,   
        "married":    true  
    }  
}}' https://127.0.0.1:5000/Alberto/Doc1
echo -e "\n"

curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{  
    "employee": {  
        "name":       "sonoo",   
        "salary":      56000,   
        "married":    true  
    }  
}  }' https://127.0.0.1:5000/Alberto/Doc2
echo -e "\n"

curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{  
    "employee": {  
        "name":       "sonoo",   
        "salary":      56000,   
        "married":    true  
    }  
}  }' https://127.0.0.1:5000/Alberto/Doc3
echo -e "\n"

curl -X POST -H "Authorization:token $token3" -d '{"doc_content":{  
    "employee": {  
        "name":       "sonoo",   
        "salary":      56000,   
        "married":    true  
    }  
}  }' https://127.0.0.1:5000/Alberto/Doc4
echo -e "\n"

echo "Getting all the documents of Alberto again..."
curl --silent -X GET -H "Authorization:token $token3" https://127.0.0.1:5000/Alberto/_all_docs
echo -e "\n"

echo "Creating request for Juanba till the API stops..."
filecontent=( `cat "test/pass_brute_force.txt" `)

for t in "${filecontent[@]}"
do
curl --silent -X POST -d '{"username":"Juanba","password":"'${t}'"}' https://127.0.0.1:5000/login
done
