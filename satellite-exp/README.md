## Quick Notes
- Remember to modify the `config.json` file to match your network configuration.
- Remember to modify the IP address in the s_timer.c in client before compiling it.
- Remember to modify the IP address in the nginx.conf file in server before running it.
- To be simple, run every script as root.

## Check the network configuration
- Check the IP address of the server and client by running `ifconfig`
- The IP address set in this is repository is as follows:
    - `Server`: 192.168.50.55
    - `Client`: 192.168.50.54
    - Nginx server run on port 4433
    - Socket run on port 8000

## Steps to run the server
1. Install ubuntu pre-requisites.
    ```bash
   cd server && sudo ./install_prereqs.sh
   ```


2. Modify IP address in `config.json` and `nginx.conf` file.
   - `config.json`: 
        ```json
        "server_ip": "<your_server_ip>"
        "client_ip": "<your_client_ip>"
        "tls_port": "<choose_server_port>"
        "socket_port": "<choose_socket_port>"
        ```
   - `nginx.conf`: 
        ```nginx
        listen       <your_server_ip>:<choose_server_port> ssl;
        ```

3. Set up server environment, choose the algorithm you want to test.
    ```bash
   cd <kex/sig> && sudo ./setup.sh
   ```

4. Synchronize CA key and cert to client.
    ```bash
   sudo ./syncParam.sh <your_client_ip>
   ```

5. Run server
    ```bash
   sudo ./runServer.sh
   ```

## Steps to run the client
1. Install ubuntu pre-requisites.
    ```bash
   cd client && sudo ./install_prereqs.sh
   ```


2. Modify IP address in `config.json` file.
   - `config.json`: 
     ```json
     "server_ip": "<your_server_ip>"
     "client_ip": "<your_client_ip>"
     "tls_port": "<choose_server_port>"
     "socket_port": "<choose_socket_port>"
     ```

3. Set up client environment, choose the algorithm you want to test.
    ```bash
   cd <kex/sig> && sudo ./setup.sh
   ```

4. Check if the CA key and cert are synchronized to client, if not check step 4 in server section.

5. Run client
    ```bash
   sudo ./runClient.sh
   ```


