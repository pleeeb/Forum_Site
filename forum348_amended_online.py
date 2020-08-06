from flask import Flask, session, request, url_for, render_template, escape, Markup, jsonify, flash, redirect
import mysql.connector, uuid, hashlib
from datetime import datetime

app=Flask(__name__)
app.secret_key = ''

@app.route('/get_topics', methods=['POST'])
def get_topics():
    topicList = []
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    query = "SELECT topic.header, topic.date, user.username, topic.topicID, user.userID FROM topic INNER JOIN user ON topic.userID=user.userID;" 
    cursor.execute(query)
    for head, d, user, t_id, u_id in cursor:
        topicList.append([head,d,user,t_id, u_id])
    for topic in topicList:
        cursor.execute("SELECT count(claimID) FROM claim INNER JOIN topic on claim.topicID=topic.topicID WHERE claim.topicID=%s",(topic[3],))
        quantity = cursor.fetchone()
        if quantity:
            topic.append(quantity[0])
        cursor.execute("SELECT claim.udate FROM claim INNER JOIN topic on claim.topicID=topic.topicID WHERE claim.topicID=%s ORDER by udate DESC limit 1",(topic[3],))
        latest = cursor.fetchone()
        if latest:
            topic.append(latest[0])
    return jsonify(render_template('topic_data.html', topics=topicList))



@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template("main_page.html")

@app.route('/mainlogin', methods=['POST'])
def mainlogin():
    details = request.form
    username = details['usernamein']
    pword = details['passwordin']
    login(username,pword)
    return redirect(url_for('main'))

@app.route('/mainsignup', methods=['GET','POST'])
def mainsignup():
    uname = request.form.get("usernamein")
    emaila = request.form.get("email_address")
    pword = request.form.get("passwordin")
    signup(uname,emaila,pword)
    return redirect(url_for('main'))

def signup(uname, email, pword):  
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    salt = uuid.uuid4().hex
    hashed = hashlib.sha512(salt.encode()+pword.encode()).hexdigest()+':'+salt
    cursor.execute("INSERT INTO user(username, email_address, password, isAdmin) VALUES (%s,%s,%s,0)",(uname,email,hashed))
    cnx.commit()
    cursor.close()
    cnx.close()
    return None

@app.route('/user_check', methods=['POST'])
def username_check():
    details = request.form
    username = details['usernamein']
    cnx = mysql.connector.connect(user="19015310",
                        password="",
                        host="127.0.0.1",
                        database="")
    cursor = cnx.cursor()
    cursor.execute("SELECT username FROM user WHERE username=%s", (username,))
    row = cursor.fetchone()

    if row:
        resp = jsonify({'reply':'<span style=\'color:red;\'>Username unavailable</span>', 'sub':'false'})
        resp.status_code = 200
        return resp
    else:
        resp = jsonify({'reply': "", 'sub':'true'})
        resp.status_code = 200
        return resp

@app.route('/email_check', methods=['POST'])
def email_check():
    details = request.form
    email = details['email_address']
    cnx = mysql.connector.connect(user="19015310",
                        password="",
                        host="127.0.0.1",
                        database="")
    cursor = cnx.cursor()
    cursor.execute("SELECT email_address FROM user WHERE email_address=%s", (email,))
    row = cursor.fetchone()

    if row:
        resp = jsonify({'reply':'<span style=\'color:red;\'>Email already registered</span>', 'sub':'false'})
        resp.status_code = 200
        return resp
    else:
        resp = jsonify({'reply': "", 'sub':'true'})
        resp.status_code = 200
        return resp

def login(uname, pword):
    cnx = mysql.connector.connect(user="19015310",
                        password="",
                        host="127.0.0.1",
                        database="")
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM user WHERE username=%s", (uname,))
    row = cursor.fetchone()
    if row:
        if row[1]!="deleted":
            hashed, salt = row[3].split(':')
            if hashed == hashlib.sha512(salt.encode()+pword.encode()).hexdigest():
                session['loggedin'] = 'True'
                session['id'] = str(row[0])
                session['username'] = str(row[1])
                if row[4]==1:
                    session['admin'] = 'True'
                flash ("Successfully logged in")
            else:
                flash ("Incorrect username/password")
            return None
        else: flash("Incorrect username/password")
        return None
    else:
        flash("Incorrect username/password")
        return None

@app.route('/topiclogin', methods=['POST'])
def topiclogin():
    details = request.form
    username = details['usernamein']
    pword = details['passwordin']
    login(username,pword)
    return redirect(url_for('claim',topic_id=details['currentpath']))

@app.route('/topicsignup', methods=['POST'])
def topicsignup():
    uname = request.form.get("usernamein")
    emaila = request.form.get("email_address")
    pword = request.form.get("passwordin")
    signup(uname,emaila,pword)
    return redirect(url_for('claim',topic_id=request.form.get('currentpath')))

@app.route('/searchlogin', methods=['POST'])
def searchlogin():
    details = request.form
    username = details['usernamein']
    pword = details['passwordin']
    login(username,pword)
    return redirect(url_for('searchclaim',search=details['currentpath']))

@app.route('/searchsignup', methods=['POST'])
def searchsignup():
    uname = request.form.get("usernamein")
    emaila = request.form.get("email_address")
    pword = request.form.get("passwordin")
    signup(uname,emaila,pword)
    return redirect(url_for('searchclaim',search=request.form.get('currentpath')))

@app.route('/replylogin', methods=['POST'])
def replylogin():
    details = request.form
    username = details['usernamein']
    pword = details['passwordin']
    login(username,pword)
    return redirect(url_for('replypage',claim_id=details['currentpath']))

@app.route('/replysignup', methods=['POST'])
def replysignup():
    uname = request.form.get("usernamein")
    emaila = request.form.get("email_address")
    pword = request.form.get("passwordin")
    signup(uname,emaila,pword)
    return redirect(url_for('replypage',claim_id=request.form.get('currentpath')))


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return "success"

@app.route('/add_topic', methods=['POST'])
def add_topic():
    details = request.form
    topicd = details['topichead']
    cnx = mysql.connector.connect(user="19015310",
                        password="",
                        host="127.0.0.1",
                        database="")
    cursor = cnx.cursor()
    now = datetime.now()
    user = session['id']
    currenttime = now.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO topic(header,date,userID) VALUES (%s, %s, %s)", (topicd,currenttime,user))
    cnx.commit()
    cursor.close()
    cnx.close()
    return redirect(url_for('main'))

@app.route('/add_claim', methods=['POST'])
def add_claim():
    details = request.form
    claimh = details['claimhead']
    user = session['id']
    now = datetime.now()
    currenttime = now.strftime('%Y-%m-%d %H:%M:%S')
    tID = details['topicID']
    claimType = details['claimType']
    relateID = details['relateID']
    if claimType == "norelate":
        cnx = mysql.connector.connect(user="19015310",
                    password="",
                    host="127.0.0.1",
                    database="")
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO claim(header,date,udate,topicID,userID) VALUES (%s,%s,%s,%s,%s)", (claimh,currenttime,currenttime,tID,user))
        cnx.commit()
        cursor.close()
        cnx.close()
    elif claimType == "equiv":
        cnx = mysql.connector.connect(user="19015310",
                    password="",
                    host="127.0.0.1",
                    database="")
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO claim(header,date,udate,topicID,userId,relateClaim,equiv) VALUES (%s,%s,%s,%s,%s,%s,1)", (claimh,currenttime,currenttime,tID,user,relateID))
        cnx.commit()
        cursor.close()
        cnx.close()
    elif claimType == "opposed":
        cnx = mysql.connector.connect(user="19015310",
                    password="",
                    host="127.0.0.1",
                    database="")
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO claim(header,date,udate,topicID,userId,relateClaim,opposed) VALUES (%s,%s,%s,%s,%s,%s,1)", (claimh,currenttime,currenttime,tID,user,relateID))
        cnx.commit()
        cursor.close()
        cnx.close()   
    return redirect(url_for('claim', topic_id=tID))

@app.route('/claim/<int:topic_id>', methods=['GET'])
def claim(topic_id):
    claimList = []
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    query = "SELECT claim.header, claim.date, user.username, claim.claimID, claim.udate, user.userID FROM ((claim INNER JOIN topic ON claim.topicID=topic.topicID) INNER JOIN user ON claim.userID=user.userID) WHERE claim.topicID=%s ORDER BY udate DESC;"
    cursor.execute(query, (topic_id,))
    for head, d, user, c_id, udate, u_id in cursor:
        claimList.append([head,d, user, c_id, udate, u_id])
    for claim in claimList:
        cursor.execute("SELECT count(relateClaim) FROM claim WHERE relateClaim=%s and equiv='1'",(claim[3],))
        equiv = cursor.fetchone()
        if equiv:
            claim.append(equiv[0])
        cursor.execute("SELECT count(relateClaim) FROM claim WHERE relateClaim=%s and opposed='1'",(claim[3],))
        opposed = cursor.fetchone()
        if opposed:
            claim.append(opposed[0])
        cursor.execute("SELECT count(replyID) FROM reply WHERE claimID=%s",(claim[3],))
        replycount = cursor.fetchone()
        if replycount:
            claim.append(replycount[0])
    cursor.close()
    cnx.close()
    t_list = topicList()
    return render_template("topic_page.html", claims=claimList, topic=topic_id, topics=t_list)

@app.route('/reply/<int:claim_id>', methods=['GET'])
def replypage(claim_id):
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    cursor.execute("SELECT claim.header, claim.date, user.username, claim.claimID, claim.topicID from claim inner join user on claim.userID=user.userID where claim.claimID=%s;",(claim_id,))
    cinfo = cursor.fetchone()
    cursor.close()
    cnx.close()
    return render_template("claim_page.html", claim=cinfo)

@app.route('/update', methods=['POST'])
def replyupdate():
    details = request.form
    claim_id = details['claimID']
    base = []
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()    
    query = "SELECT reply.replyID, reply.body, reply.date, user.username, reply.clarif, reply.csupp, reply.counter, DATE_FORMAT(reply.date, %s) AS formdate, user.userID FROM reply INNER JOIN user ON reply.userID=user.userID WHERE reply.claimID=%s AND reply.linkedReply IS NULL ORDER BY reply.date DESC;"
    cursor.execute(query, ('%d-%m-%Y %h:%i:%s',claim_id))
    for r_id,text,date,user,clarif,csupp,counter,formdate,u_id in cursor:
        base.append([r_id,text,date,user,clarif,csupp,counter,formdate,u_id])
    cursor.close()
    cnx.close()
    for i in base:
        i.append(replyrecur(i[0]))
    return jsonify(render_template("replyupdate.html",replies=base,claim=claim_id))




@app.route('/createreply', methods=['POST'])
def createreply():
    details = request.form
    text = details['replyhead']
    c_id = details['claimID']
    user = session['id']
    now = datetime.now()
    currenttime = now.strftime('%Y-%m-%d %H:%M:%S')
    cnx = mysql.connector.connect(user="19015310",
                    password="",
                    host="127.0.0.1",
                    database="")
    cursor = cnx.cursor()
    if details['replyType']=="norelate":
        if details['crelate']=="Clarification":
            query = "INSERT INTO reply(body, date, clarif, csupp,counter,evidence,rsupp,rebuttal,userID,claimID) VALUES (%s,%s,1,0,0,0,0,0,%s,%s)"
            cursor.execute(query,(text,now,user,c_id))
            cursor.execute("UPDATE claim SET udate=%s WHERE claimID=%s",(currenttime,c_id))
        elif details['crelate']=="Support":
            query = "INSERT INTO reply(body, date, clarif, csupp,counter,evidence,rsupp,rebuttal,userID,claimID) VALUES (%s,%s,0,1,0,0,0,0,%s,%s)"
            cursor.execute(query,(text,now,user,c_id))
            cursor.execute("UPDATE claim SET udate=%s WHERE claimID=%s",(currenttime,c_id))
        elif details['crelate']=="Counter":
            query = "INSERT INTO reply(body, date, clarif, csupp,counter,evidence,rsupp,rebuttal,userID,claimID) VALUES (%s,%s,0,0,1,0,0,0,%s,%s)"
            cursor.execute(query,(text,now,user,c_id))
            cursor.execute("UPDATE claim SET udate=%s WHERE claimID=%s",(currenttime,c_id))
    elif details['replyType']=="reply":
        linkrep = details['relateID']
        if details['crelate']=="Clarification":
            query = "INSERT INTO reply(body, date, clarif, csupp,counter,evidence,rsupp,rebuttal,userID,claimID,linkedReply) VALUES (%s,%s,0,0,0,1,0,0,%s,%s,%s)"
            cursor.execute(query,(text,now,user,c_id,linkrep))
            cursor.execute("UPDATE claim SET udate=%s WHERE claimID=%s",(currenttime,c_id))
        elif details['crelate']=="Support":
            query = "INSERT INTO reply(body, date, clarif, csupp,counter,evidence,rsupp,rebuttal,userID,claimID,linkedReply) VALUES (%s,%s,0,0,0,0,1,0,%s,%s,%s)"
            cursor.execute(query,(text,now,user,c_id,linkrep))
            cursor.execute("UPDATE claim SET udate=%s WHERE claimID=%s",(currenttime,c_id))
        elif details['crelate']=="Counter":
            query = "INSERT INTO reply(body, date, clarif, csupp,counter,evidence,rsupp,rebuttal,userID,claimID,linkedReply) VALUES (%s,%s,0,0,0,0,0,1,%s,%s,%s)"
            cursor.execute(query,(text,now,user,c_id,linkrep))
            cursor.execute("UPDATE claim SET udate=%s WHERE claimID=%s",(currenttime,c_id))
    cnx.commit()
    return redirect(url_for('replypage',claim_id=details['claimID']))

def replyrecur(reply_id, level=3):
    replies = []
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    cursor.execute("select reply.replyID, reply.body, reply.date, user.username, reply.evidence, reply.rsupp, reply.rebuttal, DATE_FORMAT(reply.date, %s) AS formdate, user.userID from reply inner join user on reply.userID=user.userID where linkedReply=%s;",('%d-%m-%Y %h:%i:%s',reply_id))
    for r_id, body, date, username,evi,sup,reb, formdate, u_id in cursor:
        replies.append([r_id, body, date, username,evi,sup,reb,formdate,u_id])
    for reply in replies:
        reply.append(level)
        reply.append(replyrecur(reply[0],level=level+3))
    return replies


    #query = "select replyID,body,date,evidence,rsupp,rebuttal,user.username,linkedReply, DATE_FORMAT(date, %s) AS formdate from (select * from reply order by linkedReply, replyID) as reply_sorted inner join user on reply_sorted.userID=user.userID, (select @pv:=%s) initialisation where find_in_set(linkedReply, @pv) and length(@pv:=concat(@pv,',',replyID));"
    #cursor.execute(query, ('%d-%m-%Y %h:%i:%s',reply_id))
    #for r_id,body,date,evi,rsupp,reb,u_name,l_rep,formdate in cursor:
        #replies.append([r_id,body,date,evi,rsupp,reb,u_name,l_rep,formdate])
    
    #return replies

@app.route('/claimrelate', methods=['POST'])
def relatedclaims():
    relatedclaims = []
    details = request.form
    relate_id = details['rowID']
    t_id = details["t_id"]
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    cursor.execute("select claim.header, claim.date, user.username, claim.claimID, claim.udate FROM ((claim INNER JOIN topic ON claim.topicID=topic.topicID) INNER JOIN user ON claim.userID=user.userID) WHERE claim.topicID=%s and claim.relateClaim=%s  ORDER BY udate DESC;",(t_id,relate_id))
    for head, d, user, c_id, udate in cursor:
        relatedclaims.append([head,d, user, c_id, udate])
    for claim in relatedclaims:
        cursor.execute("SELECT count(relateClaim) FROM claim WHERE relateClaim=%s and equiv='1'",(claim[3],))
        equiv = cursor.fetchone()
        if equiv:
            claim.append(equiv[0])
        cursor.execute("SELECT count(relateClaim) FROM claim WHERE relateClaim=%s and opposed='1'",(claim[3],))
        opposed = cursor.fetchone()
        if opposed:
            claim.append(opposed[0])
        cursor.execute("SELECT count(replyID) FROM reply WHERE claimID=%s",(claim[3],))
        replycount = cursor.fetchone()
        if replycount:
            claim.append(replycount[0])
    return jsonify(render_template('claimdata.html', claims=relatedclaims, topic=t_id))

@app.route('/searchclaim/<search>', methods=['GET'])
def searchclaim(search):
    claimList = []
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    query = "SELECT claim.header, claim.date, user.username, claim.claimID, claim.udate, claim.topicID, user.userID FROM claim inner join user on claim.userID=user.userID where header REGEXP %s;"
    cursor.execute(query, (search,))
    for head, d, user, c_id, udate,t_id,u_id in cursor:
        claimList.append([head,d, user, c_id, udate,t_id,u_id])
    for claim in claimList:
        cursor.execute("SELECT count(relateClaim) FROM claim WHERE relateClaim=%s and equiv='1'",(claim[3],))
        equiv = cursor.fetchone()
        if equiv:
            claim.append(equiv[0])
        cursor.execute("SELECT count(relateClaim) FROM claim WHERE relateClaim=%s and opposed='1'",(claim[3],))
        opposed = cursor.fetchone()
        if opposed:
            claim.append(opposed[0])
        cursor.execute("SELECT count(replyID) FROM reply WHERE claimID=%s",(claim[3],))
        replycount = cursor.fetchone()
        if replycount:
            claim.append(replycount[0])
    cursor.close()
    cnx.close()
    t_list = topicList()
    return render_template("searchclaim.html", search=search, claims=claimList, topics=t_list)

@app.route('/searchtopic/<search>', methods=['GET'])
def searchtopic(search):
    topicList = []
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    query = "SELECT topic.header, topic.date, user.username, topic.topicID, user.userID FROM topic INNER JOIN user ON topic.userID=user.userID where topic.header REGEXP %s;"
    cursor.execute(query,(search,))
    for head, d, user, t_id, u_id in cursor:
        topicList.append([head,d,user,t_id, u_id])
    for topic in topicList:
        cursor.execute("SELECT count(claimID) FROM claim INNER JOIN topic on claim.topicID=topic.topicID WHERE claim.topicID=%s",(topic[3],))
        quantity = cursor.fetchone()
        if quantity:
            topic.append(quantity[0])
        cursor.execute("SELECT claim.udate FROM claim INNER JOIN topic on claim.topicID=topic.topicID WHERE claim.topicID=%s ORDER by udate DESC limit 1",(topic[3],))
        latest = cursor.fetchone()
        if latest:
            topic.append(latest[0])
    return render_template("searchtopic.html", topics=topicList)

    

@app.route('/removeTopic', methods=['POST'])
def removeTopic():
    t_id = request.form.get('t_id')
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    claimList=[]
    cursor.execute("SELECT claimID FROM claim WHERE topicID=%s",(t_id,))
    for claim in cursor:
        claimList.append(claim[0])
    for c_id in claimList:
        cursor.execute("DELETE FROM reply WHERE claimID=%s",(c_id,))
        cursor.execute("DELETE FROM claim WHERE claimID=%s",(c_id,))
    cursor.execute("DELETE FROM topic WHERE topicID=%s",(t_id,))
    cnx.commit()
    cursor.close()
    cnx.close()
    return "Success"

@app.route('/removeClaim', methods=['POST'])
def removeClaim():
    t_id = request.form.get('t_id')
    c_id = request.form.get('rowID')
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    cursor.execute("DELETE FROM reply WHERE claimID=%s",(c_id,))
    cursor.execute("DELETE FROM claim WHERE claimID=%s",(c_id,))
    cnx.commit()
    cursor.close()
    cnx.close()
    return "Success"

@app.route('/removeReply', methods=['POST'])
def removeReply():
    r_id = request.form.get('r_id')
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    cursor.execute("DELETE FROM reply WHERE replyID=%s OR linkedReply=%s",(r_id,r_id))
    cnx.commit()
    cursor.close()
    cnx.close()
    return "Success"

@app.route('/removeUser', methods=['POST'])
def removeUser():
    reply = request.form
    u_id = reply['userIDchoice']
    t_id = reply['currentpath']
    page = reply['page']
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    cursor.execute("UPDATE user SET username='deleted' WHERE userID=%s",(u_id,))
    cnx.commit()
    cursor.close()
    cnx.close()
    if page=="claim":
        return redirect(url_for('claim', topic_id=t_id))
    elif page=="main":
        return redirect(url_for('main'))
    elif page=="reply":
        return redirect(url_for('replypage',claim_id=t_id))
    elif page=="search":
        return redirect(url_for('searchclaim',search=t_id))
    

@app.route('/moveClaim', methods=['POST'])
def moveClaim():
    result = request.form
    t_id = result['topic']
    c_id = result['claim']
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    cursor.execute("UPDATE claim SET topicID=%s WHERE claimID=%s", (t_id,c_id))
    cnx.commit()
    cursor.close()
    cnx.close()
    return "Success"

def topicList():
    topicList = []
    cnx = mysql.connector.connect(user="19015310",
                              password="",
                              host="127.0.0.1",
                              database="")
    cursor = cnx.cursor()
    query = "SELECT topic.header, topic.date, user.username, topic.topicID FROM topic INNER JOIN user ON topic.userID=user.userID;" 
    cursor.execute(query)
    for head, d, user, t_id in cursor:
        topicList.append([head,d,user,t_id])
    return topicList
