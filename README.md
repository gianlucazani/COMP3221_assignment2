# COMP3221_assignment2
Implement a p2p Blockchain using Python


## QUESTIONS

1) In which case multiple miners will access the same server at the same time? 
2) it says "A miner polls the blockchain server every 1 seconds to check the proof. If the proof is changed (a new block is added to the blockchain), miner will try to find a new proof and submit it to server for creating a new block as soon as possible." but if a new block has been just added to the blockchain, this means that the transaction pool is now empty so why do the miner need to compute a new proof? This is: miner1 and miner2 are computing the proof at the same time, miner 2 solves the cryptopuzzle before miner1 and broadcasts the block with the nonce (transaction pool has been processed, now peer2 has an empty pool). Once a peer (let's say peer1) receives the block, if the block is correct then it will add the block to its own blockchain and miner1 will stop computing the proof because a solution has been already found, it will empty its transaction pool. Now peer1 has no transactions to work on, so why should it start computing a new proof?
