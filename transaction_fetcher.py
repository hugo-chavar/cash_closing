from fiskaly_service import FiskalyService

class TransactionFetcher:
    def __init__(self, fiskaly: FiskalyService, last_tx_ok, last_tx):
        self.fiskaly_service = fiskaly
        self.last_tx_processed = last_tx_ok
        self.last_tx_pending = last_tx
    
    def __iter__(self):

        return self
    
    def __next__(self):
        remaining = self.last_tx_pending - self.last_tx_processed
        print("-------------------------------------")
        if remaining > 0:
            limit = 100 if remaining >= 100 else remaining
            offset = remaining - limit
            print(f"Call fiskaly. \nlast_tx_pending {self.last_tx_pending}\nlast_tx_processed {self.last_tx_processed}\nremaining {remaining}\nlimit {limit}\noffset {offset}")
            
            self.last_tx_processed += limit

            return self.last_tx_processed
        else:
            raise StopIteration
        
tf = TransactionFetcher(None, 13797, 14889)

myiter  = iter(tf)

print(next(myiter))
print(next(myiter))
print(next(myiter))
print(next(myiter))
print(next(myiter)) 
print(next(myiter))
print(next(myiter))
print(next(myiter))
print(next(myiter))
print(next(myiter)) 
print(next(myiter)) 
print(next(myiter)) 