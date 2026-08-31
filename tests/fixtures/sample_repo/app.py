def validate_order(order):
    return bool(order)


def save_order(order):
    return order


def process_order(order):
    if not validate_order(order):
        raise ValueError("invalid order")
    return save_order(order)


class CheckoutService:
    def checkout(self, order):
        return process_order(order)
