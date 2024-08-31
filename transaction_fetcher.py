from fiskaly_service import FiskalyService

class TransactionFetcher:
    def __init__(self, fiskaly: FiskalyService, client, last_tx_ok, last_tx):
        self.fiskaly_service = fiskaly
        self.last_tx_processed = last_tx_ok
        self.last_tx_pending = last_tx # Esto se actualiza internamente no debe venir como param en el constructor
        self.client = client
    
    def __iter__(self):

        return self
    
    def __next__(self):
        remaining = self.last_tx_pending - self.last_tx_processed
        print("-------------------------------------")
        if remaining > 0:
            limit = 100 if remaining >= 100 else remaining
            offset = remaining - limit
            print(f"Call fiskaly. \nlast_tx_pending {self.last_tx_pending}\nlast_tx_processed {self.last_tx_processed}\nremaining {remaining}\nlimit {limit}\noffset {offset}")
            # self.fiskaly_service.get_transactions(self.tss_id, limit, offset)
            self.last_tx_processed += limit

            # return self.last_tx_processed
            return self.fiskaly_service.get_transactions(self.client, limit, offset)
        else:
            raise StopIteration

