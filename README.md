# COMP3221 Assignment2: Report
<p align="center">
  <img src="COMP3221 - assignment2@2x.png" width="450px"/>
</p>
The assignment topic is the realization of a Blockchain simulated in a local network composed of at least three peers, each of which has three different roles: server, miner and client. The image above is the graph representation of the network. <br>

## Information

All the features have been implemented by assuming prior properties of the network:

<ul>
  <li>
    There are no byzantine peers in the network
  </li>
  <li>
    The network is represented by a fully connected graph (each peer is neighbour to each other peer)
  </li>
  <li>
    Transaction order is not guaranteed
  </li>
  <li>
    The best blockchain is always the longest and where all the new blocks are valid
  </li>
  <li>
    When a peer dies, it gets inhibited. This means that the python program will still run but the peer will be made unreachable and not able anymore to send anything
  </li>
  <li>
    The blockchain will never get forked, all peers will always agree on the chain
  </li>
  <li>
    The client role is the one responsible for broadcasting new transactions to all other peers
  </li>
  <li>
    The server role is the one responsible for broadcasting the Heartbeat signal and for comparing incoming blockchain, as well as updating the current blockchain if the received is longer and valid
  </li>
</ul>

## Environment and Dependencies

This program runs on:

```
python 3.10.4
```
## Usage

This section will explain how to use the program and see as the network behaviour satisfies requirements.

### Starting a node
As stated in the assignment sheet, the program starts by running the following shell command:
```
python3 BlockchainPeer.py <Peer-id> <Port-no> <Peer-config-file>
```
### Broadcasting a new transaction (```tx``` command)

Once the peer is started, it will keep asking for user input until it gets shut down. This is what the input menu looks like:

```
Which action do you want to perform? (type the command)
tx) Transaction [tx|{sender}|{content}]
pb) Print Blockchain [pb]
cc) Close Connection [cc]
```
If we want to broadcast a new transaction, we need to first type the correspondent command (```tx```) and this will be printed:

```
Write the transaction in the format tx|{sender}|{content}
```
We can now type the transaction in the specified format, for example:
```
tx|gzan3055|100BTC
```
The transaction will be now sent to the server role residing in the same peer and to all other peers. The server residing in the same peer will respond to the client whether the transaction got accepted or rejected (```Accepted``` or ```Rejected``` will be printed by the client respectively).

### Printing the Blockchain (```pb``` command)
As a client, we can ask the server residing in the same peer as we do to give us the blockchain so that then we can print it at terminal. To do this, when the input menu is printed:
```
Which action do you want to perform? (type the command)
tx) Transaction [tx|{sender}|{content}]
pb) Print Blockchain [pb]
cc) Close Connection [cc]
```
We type in the ```pb``` command, and something like this will be printed at terminal:
```
TRANSACTIONS IN THE POOL:

tx|gzan3055|600BTC
tx|gzan3055|700BTC

CHAIN:

Index: 1 
Timestamp: 1652164888.12973 
Transactions: [] 
Proof: 100 
Previous hash: This block has no previous hash 
Current hash: 4b6928e5a4d44810b85a45bf101cc0bac453a01ae9fcd6806e815b1634ea9d9b 

Index: 2 
Timestamp: 1652164947.116981 
Transactions: ['tx|gzan3055|100BTC', 'tx|gzan3055|200BTC', 'tx|gzan3055|300BTC', 'tx|gzan3055|400BTC', 'tx|gzan3055|500BTC'] 
Proof: 5 
Previous hash: 4b6928e5a4d44810b85a45bf101cc0bac453a01ae9fcd6806e815b1634ea9d9b 
Current hash: 9f0cb2d3c3447f22b193bb84976272c0449c0254096a236a27c01b6cbe657641 
```
Where we can both see the transaction currently in the blockchain pool (waiting to be at least five and then to be added to a new block) and the current blockchain itself, which in this case is composed of two blocks (the genesis block and another one)

### Closing connection (```cc``` command)
The last input that a user can perform by using the client role is the closing connection. With this action, we will make the peer inhibited, which makes it unreachable and not able anymore to send commands and requests. To kill a peer we input the command ```cc``` as input:

```
Which action do you want to perform? (type the command)
tx) Transaction [tx|{sender}|{content}]
pb) Print Blockchain [pb]
cc) Close Connection [cc]
cc
```
After all, the threads get stopped and the peer closed all the connections, this message will be printed at terminal (telling that the operation was successful):

```
Peer terminated successfully
```

## Other commands
The other commands, which are ```gp```, ```up``` and ```hb``` are not directly managed by the user that interacts with the peer(s), but are exchanged <i> under the hood </i> by peers. 

### The ```gp``` command
The ```gp``` (get proof) command is exchanged by miner role and server role within the same peer and is used by the miner for asking the server its situation with proofs. In particular, in our implementation, the response to a "gp" command will be in this format:
```
{
  "prev_proof": int,
  "next_proof": int
}
```
Where ```prev_proof``` represents the proof of the last block of the blockchain, while ```next_proof``` represents the value of the next proof that will be used for building the new block (once five transactions are received). ```next_proof``` can assume two values:
<ul>
  <li>
    A positive integer (the actual next proof) if the server already has the next proof, which has not been used yet (less than 5 transactions in the pool). If the miner receives this value it means that it is not necessary to work on the new proof.
  </li>
  <li>
    -1 if the server doesn't have the next proof. The miner that receives this value, will compute the next proof starting from the prev_proof sent by the server.
  </li>
</ul>

When the ```next_proof = -1``` and ```prev_proof``` is different from the one the miner is currently working on, then the miner will stop and start again finding the next proof on the new ```prev_proof```. This can happen if while the miner is calculating the next proof starting from ```prev_proof1``` the server receives a new valid block where the next proof (```next_proof1```) of ```prev_proof1``` has already been found by another peer and used for creating the block. In this case it is useless for the miner to continue working on ```prev_proo1```and so it starts working on ```prev_proof2``` (which now is ```next_proof1```) for finding ```next_proof2```.

### The ```up``` command
The ```up``` (update proof) command is exchanged by miner role and server role within the same peer and is used by the miner sending the new found proof back to the server. In particular, the ```up``` package will have the following format:
```
up|{next_proof}
```
### The ```hb``` command
The ```hb``` (heartbeat) command is exchanged by server roles of the peers in the network and is used for polling other peers' blockchains. This is done to continuously and constantly agree on the blockchain. Every 5 seconds each peer sends to all other peers the ```hb``` command. Upon reception of this command, a peer will convert its blockchain to JSON and will send it back to the peer who sent the ```hb```.<br><br>

When a blockchain is received, it is checked if its length is greater than the one I own, if it is greater than it is checked that all the _exceeding blocks_ are valid (i.e. contain only valid transactions), and if this is true then my blockchain gets updated with the received, longer, valid one.<br><br>
What we mean by _exceeding blocks_ is represented by the blue blocks in the image below:

<p align="center">
  <img src="untitled@2x (2).png" width="600px"/>
</p>

In this case, if blocks 4 and 5 are valid, the OWNED BLOCKCHAIN will be updated with the RECEIVED BLOCKCHAIN.

  
