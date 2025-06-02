class TransactionFixer:
    """
    The purpose of this class is complete some information in the line items. Sometimes the frontend leaves null instead of the item_id. This code fixes that.
    So, this class completes missing product data in transactions by enriching line items with product information.

    This class is responsible for:
    - Identifying gaps in transaction numbers
    - Retrieving product data from a ProductProvider
    - Updating line items with retrieved product information

    Attributes:
        product_provider (ProductProvider): Instance of ProductProvider for retrieving product data
        last_processed_tx_number (int): Last processed transaction number

    Methods:
        complete_transaction_data(transactions, config): Completes missing product data in transactions
    """
    
    def __init__(self, product_provider, fiskaly_service, config):
        """
        Initializes the TransactionFixer.

        :param product_provider: An instance of ProductProvider
        """
        self.product_provider = product_provider
        self.last_processed_tx_number = None
        self.fiskaly_service = fiskaly_service
        self.config = config

    def complete_transaction_data(self, transactions):
        """
        Completes missing product data in transactions.

        :param transactions: List of transactions
        :param config: Configuration object with last_processed_tx_number
        """
        self.last_processed_tx_number = self.config.last_processed_tx_number

        for transaction in transactions:
            try:
                self._check_transaction_number_gap(transaction)
                self._complete_product_data(transaction)
            except Exception as e:
                print(f"Exception in transaction {transaction['number']}: {e}", flush=True)
                print("New transactions were added to the backend", flush=True)
                print(f"Last transaction in list: {transactions[-1]}", flush=True)
                
                raise e
                

    def cancel_active_txn(self, transactions):
        for transaction in transactions:
            if transaction["state"] == "ACTIVE":
                # TODO: check if it is a very recent tx
                self.fiskaly_service.cancel_transaction(self.config.client, transaction)
                transaction["state"] = "CANCELLED"

    def _check_transaction_number_gap(self, transaction):
        """
        Checks for gaps in transaction numbers.

        :param transaction: Current transaction
        """
        if self.last_processed_tx_number != (transaction['number'] - 1):
            msg = f"{self.last_processed_tx_number} => {(transaction['number'] - 1)} TF falta el siguiente"
            print(f"{msg}  ************ ERROR split\n\n", flush=True)
            raise Exception(msg)
            print(f"Set LAST_PROCESSED_TX_NUMBER to {(transaction['number'] - 1)} \n\n")
        self.last_processed_tx_number = transaction['number']

    def _complete_product_data(self, transaction):
        """
        Completes missing product data in a transaction.

        :param transaction: Current transaction
        """
        if "schema" in transaction and "standard_v1" in transaction["schema"]:
            standard_v1 = transaction["schema"]["standard_v1"]
            if "order" in standard_v1 and "line_items" in standard_v1["order"]:
                for line_item in standard_v1["order"]["line_items"]:
                    self._complete_line_item_data(line_item)

    def _complete_line_item_data(self, line_item):
        """
        Completes missing product data in a line item.

        :param line_item: Current line item
        """
        if line_item["text"].startswith("null"):
            try:
                product_title = line_item["text"].split(' - ')[1]
                line_item["text"] = str(self.product_provider.get_by_title(product_title))
            except (AttributeError, IndexError, TypeError) as e:
                print(f"Error completing line item data: {e}")
            except KeyError:
                print(f"Product not found: {product_title}")