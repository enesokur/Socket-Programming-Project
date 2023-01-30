from socket import *

#This function searches a room inside room list which is read from rooms.txt
def search_room(roomname,rooms):
    for i in rooms:
        if roomname == i:
            return True
    return False

#localhost and port number
hostname = "127.0.0.1"
port = 8081
#Creating socket
serversocket = socket(AF_INET,SOCK_STREAM)
serversocket.bind((hostname,port))
serversocket.listen(1)
#Getting requests
while True:
    clientcon, clientadress = serversocket.accept()
    request = clientcon.recv(1024).decode()
    #Separating url to know whether it is add,remove etc.
    headers = request.split("\n")
    path = headers[0].split()[1]
    functionality = path.split("?")[0]
    # If it is add request room is added to txt file if it doesn't exist.
    if functionality == "/add":
        roomname = path[10:]
        with open("rooms.txt","r") as f:
            rooms = f.read().splitlines()
        roomalreadyexists = search_room(roomname,rooms)
        #If the room doesn't exist we add it and send 200 OK message
        if not roomalreadyexists:
            with open("rooms.txt", "a") as f:
                f.write(roomname + "\n")
                response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Room Added</title></head><body>"+roomname+" added</body></html>"
        #If the room already exists we send 403 FORBIDDEN message
        else:
            response = "HTTP/1.0 403 FORBIDDEN\n\n" + "<html><head><title>Error</title></head><body>"+roomname+" already exists</body></html>"
    #If it is remove request room is removed from the txt file if it exists.
    elif functionality == "/remove":
        roomname = path[13:]
        with open("rooms.txt","r") as f:
            rooms = f.read().splitlines()
        roomalreadyexists = search_room(roomname,rooms)
        #If room doesn't exist we send 403 FORBIDDEN message
        if not roomalreadyexists:
            response = "HTTP/1.0 403 FORBIDDEN\n\n" + "<html><head><title>Error</title></head><body>" + roomname + " not found</body></html>"
        #If room exists it is removed from txt file and 200 OK message is sent.
        else:
            rooms.remove(roomname)
            with open("rooms.txt","w") as f:
                for room in rooms:
                    f.write(room + "\n")
            response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Room Removed</title></head><body>" + roomname + " removed</body></html>"
    # If it is reserve request we get reservation informations from url and make reservation if the room is available.
    elif functionality == "/reserve":
        can_reserve = True
        parameters = path[9:].split("&")
        #Getting reservation informations from url.
        room_name = parameters[0][5:]
        activity_name = parameters[1][9:]
        day = parameters[2][4:]
        hour = parameters[3][5:]
        duration = parameters[4][9:]
        #Checking if room exists.
        with open("rooms.txt","r") as f:
            rooms = f.read().splitlines()
        roomalreadyexists = search_room(room_name,rooms)
        with open("reservations.txt","r") as f:
            reservations = f.read().splitlines()
        #Sending 404 NOT FOUND response if the room doesn't exist.
        if roomalreadyexists == False:
            response = "HTTP/1.0 404 NOT FOUND\n\n" + "<html><head><title>Error</title></head><body>"+room_name+" not found</body></html>"
        #If the room exists we check whether the room is available in desired time slot.
        else:
            for i in reservations:
                if len(i) > 1:
                    room_already_reserved = i.split(" ")[1]
                    day_already_reserved = i.split(" ")[3]
                    hour_already_reserved = i.split(" ")[4]
                    duration_already_reserved = i.split(" ")[5]
                    #Checking whether the room is full or not. If it is full 403 FORBIDDEN response is sent back.
                    if room_name == room_already_reserved:
                        if day == day_already_reserved and ((int(hour_already_reserved) < int(hour) < int(hour_already_reserved) + int(duration_already_reserved)) or (int(hour_already_reserved) < int(hour) + int(duration) < int(hour_already_reserved) + int(duration_already_reserved)) or (int(hour) == int(hour_already_reserved) and int(hour) + int(duration) == int(hour_already_reserved) + int(duration_already_reserved)) or (int(hour) == int(hour_already_reserved) and int(hour) + int(duration) > int(hour_already_reserved) + int(duration_already_reserved)) or (int(hour) + int(duration) == int(hour_already_reserved) + int(duration_already_reserved)) and int(hour) < int(hour_already_reserved)):
                            response = "HTTP/1.0 403 FORBIDDEN\n\n" + "<html><head><title>Error</title></head><body>" + "Room " + room_name + " is full " + " on day " + day + " between " + hour + " and " + str(int(hour) + int(duration)) + "</body></html>"
                            can_reserve = False
                            break
            #If it is not full then reservation is made and 200 OK message is sent back.
            if can_reserve == True:
                with open("reservations.txt", "a") as f:
                    f.write(str(len(reservations) + 1) + " " + room_name + " " + activity_name + " " + day + " " + hour + " " + duration + "\n")
                response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Reservation Successful</title></head><body>" + "Room " + room_name + " is reserved for activity " + activity_name + " on day " + day + " between " + hour + " and " + str(int(hour) + int(duration)) + " Your reservation id is " + str(len(reservations) + 1) + "</body></html>"
    #If it is checkavailability request we print available hours for rooms.
    elif functionality == "/checkavailability":
        #If & is in request that means user wants to know availabile hourse for a specified day.
        if "&" in path[19:]:
            availablehours = ["9","10","11","12","13","14","15","16","17"]
            parametersforavailability = path[19:].split("&")
            roomforavailability = parametersforavailability[0][5:]
            dayforavailability = parametersforavailability[1][4:]
            with open("rooms.txt","r") as f:
                rooms = f.read().splitlines()
            roomalreadyexistss = search_room(roomforavailability, rooms)
            if roomalreadyexistss == True:
                with open("reservations.txt", "r") as f:
                    reservations = f.read().splitlines()
                # Searching through reservation.txt file for specified room and day. If reservation exists 200 OK message and available hours is sent
                for reservation in reservations:
                    reservationsplit = reservation.split(" ")
                    if reservationsplit[1] == roomforavailability and reservationsplit[3] == dayforavailability:
                        starttime = reservationsplit[4]
                        #Calculating available hourses.
                        for i in range(0,int(reservationsplit[5])):
                            availablehours.remove(str(int(starttime) + i))
                response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Available Hours</title></head><body>" + "On day " + dayforavailability + " Room " + roomforavailability + " is available for the following hours: " + ' '.join(availablehours) + "</body></html>"
            #If reservation doesn't exist for specified room and day 404 NOT FOUND response is sent back.
            else:
                response = "HTTP/1.0 404 NOT FOUND\n\n" + "<html><head><title>Error</title></head><body>" + "Room doesn't exist" + "</body></html>"
        #If request doesn't include & sign that means user wants to know available hours for all days.
        else:
            roomforavailability2 = path[24:]
            stringforavailability =""
            with open("rooms.txt","r") as f:
                rooms = f.read().splitlines()
            roomalreadyexistss = search_room(roomforavailability2, rooms)
            if roomalreadyexistss == True:
                with open("reservations.txt", "r") as f:
                    reservations = f.read().splitlines()
                #This for loop looks for every day from 1 to 5.
                for j in range(1,6):
                    availablehours2 = ["9", "10", "11", "12", "13", "14", "15", "16", "17"]
                    for reservation in reservations:
                        reservationsplit = reservation.split(" ")
                        if reservationsplit[1] == roomforavailability2 and reservationsplit[3] == str(j):
                            starttime = reservationsplit[4]
                            #Calculating available hourses
                            for i in range(0, int(reservationsplit[5])):
                                availablehours2.remove(str(int(starttime) + i))
                    stringforavailability += "On day " + str(j) + " Room " + roomforavailability2 + " is available for the following hours: " + ' '.join(availablehours2) + "<br>"
            response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Available Hours</title></head><body>" + stringforavailability + "</body></html>"
    clientcon.send(response.encode())
    clientcon.close()
