import os
from flask import Flask, render_template, request, flash, redirect, session, jsonify
import requests
import webbrowser
from threading import Timer
from bson.json_util import dumps, loads
import json
import pymongo
from pymongo import MongoClient


client = MongoClient()
# print(client.list_database_names())
portfolio_accts_db = client["portfolio_accts"]
users_col = portfolio_accts_db["users"]

app = Flask(__name__)


@app.route("/verify-account", methods=["GET"])
def verify_account():

    username = request.args.get("username")
    password = request.args.get("password")
   
    user_data = users_col.find_one({"username": username})
    
    if user_data:
        if password == user_data["password"]:
            results = {"success": 1}
            # print("verified")
        else:
            error_msg = "That username and password don't match our records"
            results = {"success": 0,
                   "error_msg": error_msg}       
    else:
        error_msg = "That username and password don't match our records"
       
        results = {"success": 0,
                   "error_msg": error_msg}


    return jsonify({"results": results})


@app.route("/fetch-account", methods=["GET"])
def fetch_account():

    username = request.args.get("username")
    # print(username)
    results = users_col.find_one({"username": username})

    del results["_id"]

    # print(results)

    return jsonify({"results": results})


@app.route("/create-account", methods=["GET"])
def create_account():

    username = request.args.get("username")
    password = request.args.get("password")


    user_data = users_col.find_one({"username": username})

    
    if user_data:
        error_msg = "That username is already in use"
        results = {"success": 0,
                "error_msg": error_msg}
    else:
        users_col.insert_one({
        "username": username, "password": password, 
        "risk": "none", "horizon": 0
        })
        results = {"success": 1}
    

    return jsonify({"results": results})

@app.route("/update-account", methods=["GET"])
def update_account():

    username = request.args.get("username")
    password = request.args.get("password")
    horizon = request.args.get("horizon")
    risk = request.args.get("risk")

    prior_user = users_col.find_one({"username": username})
    print(f"old user: {prior_user}")

    if len(password) < 1:
        password = prior_user["password"]
    if len(horizon) < 1:
        horizon = prior_user["horizon"]
    if len(risk) < 1:
        risk = prior_user["risk"]

    horizon = int(horizon)

    try:
        query_filter = {"username": username}
        update_operation = {
            "$set": {"password": password, "horizon": horizon, "risk": risk}
            }

        users_col.update_one(query_filter, update_operation)
        # new_user = users_col.find_one({"username": username})
        # print(f"new user: {new_user}")

        results = {"success": 1}

    except:
        results = {"success": 0, "error_msg": "Something has gone wrong"}

    
    return jsonify({"results": results})
    
    

if __name__ == "__main__":
    app.run(port=8002, debug=True)



