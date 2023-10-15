'''
Rachael Savage

9/30/23
'''
#import built-in libs
import socket # manage network sockets for network communication
import threading #managing threads
import os # work w/ files

"""
Host 3 static websites
to see the websites use the link:
http://192.168.0.214/website1/index.html
http://192.168.0.214/website2/index.html
http://192.168.0.214/website3/index.html
"""

# Define the server
HOST = '192.168.0.214'  #IP address for the server (local)
PORT = 80  # Port to listen on (80is standard HTTP port)

# create a dict(curly brackets)to hold the root dirs location of the folders and named the website
WEBSITES = {
    'website1': {
        'root_dir': r'C:\particlePortfolioWebsite',
        'name': 'Website 1',
    },
    'website2': {
        'root_dir': r'C:\UAT\csc102',
        'name': 'Website 2',
    },
    'website3': {
        'root_dir': r'C:\UAT\CSC104Web\Week5\AI_Odyssey_Lab',
        'name': 'Website 3',
    }
}

# Create a socket object for the server that use IPv4 address
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the specific host and port which defined above
server_socket.bind((HOST, PORT))

# Listen for incoming connections max 5
server_socket.listen(5)
print(f"Server is listening on {HOST}:{PORT}") #display a message to show that it's listening

#func to handle client connections
def handle_client(client_socket):
    #receive data from the connected socket
    request = client_socket.recv(1024).decode() # read data from the conneted socket, max 1024 bytes, & convert bytes into string (data type encode UTF-8)

    # Parse(analyze & extract) the request to get the requested path
    request_lines = request.split('\n') # take the request http string & split it into lines to create a list of string
    first_line = request_lines[0].strip() #extracts the first line of the request from the list. strip() remove any space
    #splits the first line of the request into parts(3parts/elements)
    # ex: b4: "GET /website1/index.html HTTP/1.1"
    #after: 
    '''
    parts[0] = "GET"
    parts[1] = "/website1/index.html"
    parts[2] = "HTTP/1.1"
    '''
    parts = first_line.split(' ')

#check whether the list above valid
    if len(parts) >= 2: #at least 2 parts
        requested_path_parts = parts[1].split('/') #at least 2 elements
    else:
        client_socket.close()#closes the client socket
        return

    if len(requested_path_parts) < 3:#3parts(the path)
        response = "HTTP/1.1 400 Bad Request\r\n\r\nInvalid URL"
        client_socket.send(response.encode())
        client_socket.close()#After sending the response, the code closes the client socket
        return

#extracting information from the parsed requested path and determining which website the client is requesting
    website_name_key = requested_path_parts[1]# extracts the second element (index 1): must match the name in the dict
    relative_path = '/'.join(requested_path_parts[2:])# joins the remaining elements of the requested_path_parts list (starting from index 2), using ('/') to separate
#looks up the website name from the dict
    website_info = WEBSITES.get(website_name_key, None)

#handle the final steps of processing the HTTP request
    if not website_info: #return error if no name found match
        response = "HTTP/1.1 400 Bad Request\r\n\r\nInvalid website"
        client_socket.send(response.encode()) #if matched,  send the HTTP response
        client_socket.close() #then close
        return

    # Construct the full path to the file
    file_path = os.path.join(website_info['root_dir'], relative_path)

    try:
        # Open and read the requested file
        with open(file_path, 'rb') as file: # 'rb' is defined to read file in binary mode
            response = file.read() # read and store in respose var
            client_socket.send(f"HTTP/1.1 200 OK\r\nContent-Length: {len(response)}\r\n\r\n".encode() + response)
    except FileNotFoundError:
        # If the file is not found, return a 404 error
        response = f"HTTP/1.1 404 Not Found\r\n\r\nFile Not Found on {website_info['name']}"
        client_socket.send(response.encode())
    except Exception as e:
        # Handle other exceptions
        response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}"
        client_socket.send(response.encode())

    client_socket.close() #close client socket

#func to start the server, handling incoming client connections
def start_server():
    while True: # use loop to run indef until terminate
        client_socket, addr = server_socket.accept() #wait for incomming connection
        print(f"Accepted connection from {addr}") #show message
        
        # Create a new thread  for each incoming client connection
        #Each time a client connects to the server, a new thread is created to handle that client's request
        #These threads run concurrently&independently of each other to handle each client/website
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

# Start the server
start_server()
