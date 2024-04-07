# Project DFS - Telematics course

```
  ____  _____ ____        __  __
 |  _ \|  ___/ ___|      |  \/  | ___  ___ _   _ ___ 
 | | | | |_  \___ \ _____| |\/| |/ _ \/ __| | | / __|
 | |_| |  _|  ___) |_____| |  | |  __/ (__| |_| \__ \
 |____/|_|   |____/      |_|  |_|\___|\___|\__,_|___/

```

## <-Base architecture-> 

![image](https://github.com/Adrephos/DFS-Mecus/assets/83888452/212fecee-3cf5-46af-9c3b-03f4e25f8af0)

## Uploading file process

![image](https://github.com/Adrephos/DFS-Mecus/assets/83888452/ebe1a06a-54fa-457b-a504-ff449fbb837e)

## Running the project in local:

### 1. Downloading dependencies. 

Go to each folder (client, data-node and name-node) and run the following command:

```pip install -r requirements.txt```

It is recommended to install the project requirements in a virtual machine, but it is not mandatory. 

### 2. Running the project

Go to the name node folder, run the command

```python name-node.py```

![image](https://github.com/Adrephos/DFS-Mecus/assets/83888452/107a1e12-5b5a-48be-b531-403de75ab01b)

Then, go to bootstrap.py, comment the leader config and uncomment the slave config

![image](https://github.com/Adrephos/DFS-Mecus/assets/83888452/e60cbab9-eaae-4b7d-bf12-aa7ae16263da)

then, run the command:

```python name-node.py```

![image](https://github.com/Adrephos/DFS-Mecus/assets/83888452/34025a86-a8bd-4322-bb28-719faebe1e95)

That is how the name-node and the name-node backup start running! After that, run the ```data-node.py``` and the ```client.py``` codes. 

![image](https://github.com/Adrephos/DFS-Mecus/assets/83888452/8698889d-4d67-4976-833c-e96e6630c9e8)

That is it! Register an account, login and if not sure about a command, just run the command ```help``` 💗






