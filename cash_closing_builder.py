import cash_closing

class CashClosingBuilderException(Exception):
    def __init__(self, message):
        super().__init__(message)

def build(config, transactions, product_provider):
    try:
        cc = cash_closing.build_cash_closing(
            transactions, config.cash_closing_options(), product_provider
        )

        config.last_receipt_number = cc.transactions[-1].head.number
        
        return cc
    except cash_closing.CashClosingException as e:
        raise CashClosingBuilderException(str(e))
    