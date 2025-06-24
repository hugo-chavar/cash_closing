from fiskaly_service import FiskalyService


class TransactionFetcher:
    def __init__(self, fiskaly: FiskalyService, client):
        self.fiskaly_service = fiskaly
        self.last_tx_processed = client.last_processed_tx_number
        self.client = client

    def __iter__(self):

        return self

    def __next__(self):
        remaining = self.last_tx_pending - self.last_tx_processed
        print("-------------------------------------")
        if remaining > 0:
            limit = 100 if remaining >= 100 else remaining
            offset = remaining - limit
            print(
                f"last_tx_pending {self.last_tx_pending}\nlast_tx_processed {self.last_tx_processed}\nremaining {remaining}\nlimit {limit}\noffset {offset}"
            )
            self.last_tx_processed += limit

            return self.get_transactions(limit, offset)
        else:
            raise StopIteration

    def get_transactions(self, limit, offset):
        return self.fiskaly_service.get_transactions(self.client, limit, offset)

    def update_last_tx_pending(self):
        self.last_tx_pending = self.get_transactions(limit=1, offset=0)["count"]
