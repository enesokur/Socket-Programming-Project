from socket import *
#This function searches an activity inside activity list which is read from activities.txt
def search_activity(activityname,activites):
    for i in activities:
        if activityname == i:
            return True
    return False

#localhost and port number
hostname = "127.0.0.1"
port = 8082
#Creating socket
serversocket = socket(AF_INET,SOCK_STREAM)
serversocket.bind((hostname,port))
serversocket.listen(1)
#Getting requests
while True:
    clientcon, clientadress = serversocket.accept()
    request = clientcon.recv(1024).decode()
    # Separating url to know whether it is add,remove etc.
    headers = request.split("\n")
    path = headers[0].split()[1]
    functionality = path.split("?")[0]
    # If it is add request activity is added to txt file if it doesn't exist.
    if functionality == "/add":
        activityname = path[10:]
        with open("activities.txt", "r") as f:
            activities = f.read().splitlines()
        activityalreadyexists = search_activity(activityname, activities)
        # If the activity doesn't exist we add it and send 200 OK message
        if not activityalreadyexists:
            with open("activities.txt", "a") as f:
                f.write(activityname + "\n")
                response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Activity Added</title></head><body>"+activityname+" added</body></html>"
        # If the activity already exists we send 403 FORBIDDEN message
        else:
            response = "HTTP/1.0 403 FORBIDDEN\n\n" + "<html><head><title>Error</title></head><body>"+activityname+" already exists</body></html>"
    # If it is remove request activity is removed from the txt file if it exists.
    elif functionality == "/remove":
        activityname = path[13:]
        with open("activities.txt","r") as f:
            activities = f.read().splitlines()
        activityalreadyexists = search_activity(activityname, activities)
        # If activity doesn't exist we send 403 FORBIDDEN message
        if not activityalreadyexists:
            response = "HTTP/1.0 403 FORBIDDEN\n\n" + "<html><head><title>Error</title></head><body>" + activityname + " not found</body></html>"
        # If activity exists it is removed from txt file and 200 OK message is sent.
        else:
            activities.remove(activityname)
            with open("activities.txt","w") as f:
                for activity in activities:
                    f.write(activity + "\n")
            response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Activity Removed</title></head><body>" + activityname + " removed</body></html>"
    #If it is check request we check whether desired activity exists in activites.txt or not.
    elif functionality == "/check":
        activityname = path[12:]
        with open("activities.txt","r") as f:
            activities = f.read().splitlines()
        activityalreadyexists = search_activity(activityname, activities)
        #If activity doesn't exist 404 NOT FOUND response is sent.
        if not activityalreadyexists:
            response = "HTTP/1.0 404 NOT FOUND\n\n" + "<html><head><title>Error</title></head><body>" + activityname + " not found</body></html>"
        #If activity exists 200 OK message is sent back.
        else:
            response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Activity Found</title></head><body>" + activityname + " found</body></html>"
    #If user makes a reserve request, it is sent from reservation server to activity server and activity server sends this request to room server.
    elif functionality == "/reserve":
        parameters = path[9:].split("&")
        #Getting reservation informations from url.
        roomname = parameters[0][5:]
        activityname = parameters[1][9:]
        day = parameters[2][4:]
        hour = parameters[3][5:]
        duration = parameters[4][9:]
        with open("activities.txt","r") as f:
            activities = f.read().splitlines()
        activityalreadyexists = search_activity(activityname, activities)
        # If activity doesn't exist for reservation 404 NOT FOUND message is sent back.
        if not activityalreadyexists:
            response = "HTTP/1.0 404 NOT FOUND\n\n" + "<html><head><title>Error</title></head><body>" + activityname + " not found</body></html>"
        #If activity exists request is forwarded to room server.
        else:
            clientSocketRoom = socket(AF_INET, SOCK_STREAM)
            clientSocketRoom.connect((hostname, 8081))
            clientSocketRoom.send(request.encode())
            message = clientSocketRoom.recv(2048)
            response = message.decode()
    clientcon.send(response.encode())
    clientcon.close()