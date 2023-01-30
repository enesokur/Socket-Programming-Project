from socket import *
#localhost and port number
hostname = "127.0.0.1"
port = 8080
#Creating socket
serversocket = socket(AF_INET,SOCK_STREAM)
serversocket.bind((hostname,port))
serversocket.listen(1)
#Getting requests
while True:
    clientcon, clientadress = serversocket.accept()
    request = clientcon.recv(1024).decode()
    # Separating url to know whether it is reserve,display etc.
    headers = request.split("\n")
    path = headers[0].split()[1]
    functionality = path.split("?")[0]
    #If it is reserve request, request is sent to activity server to check whether activity exists or not then it is sent to room server.
    if functionality == "/reserve":
        clientSocketActivity = socket(AF_INET, SOCK_STREAM)
        clientSocketActivity.connect((hostname, 8082))
        clientSocketActivity.send(request.encode())
        message = clientSocketActivity.recv(2048)
        response = message.decode()
    #If it is display request, information about reservation with specified id is display on browser.
    elif functionality == "/display":
        reservationfound = False
        id = path[-1]
        with open("reservations.txt","r") as f:
            reservations = f.read().splitlines()
        #If reservation with specified id exists its informations are displayed on the browser and 200 OK is sent.
        for reservation in reservations:
            if reservation[0] == id:
                parsedreservation = reservation.split(" ")
                print(parsedreservation)
                response = "HTTP/1.0 200 OK\n\n" + "<html><head><title>Reservation Info</title></head><body>" + "Reservation ID: " + parsedreservation[0] + "<br>" + "Room: " + parsedreservation[1] +"<br>" + "Activity: " + parsedreservation[2] +"<br>" + "When: " + "Day " + parsedreservation[3] + ", " + parsedreservation[4] + "-" + str(int(parsedreservation[4]) + int(parsedreservation[5]))+"</body></html>"
                reservationfound = True
                break
        #If reservation with specified id doesn't exist 404 NOT FOUND response is sent back.
        if reservationfound == False:
            response = "HTTP/1.0 404 NOT FOUND\n\n" + "<html><head><title>Error</title></head><body>"+"reservation with id " + id + " not found</body></html>"
    #If it is listavailability request, reservation server forwards request to room server and rest is handled by room server.
    elif functionality == "/listavailability":
        request = request.replace("/listavailability","/checkavailability")
        clientSocketRoom = socket(AF_INET, SOCK_STREAM)
        clientSocketRoom.connect((hostname, 8081))
        clientSocketRoom.send(request.encode())
        message = clientSocketRoom.recv(2048)
        response = message.decode()
    clientcon.send(response.encode())
    clientcon.close()