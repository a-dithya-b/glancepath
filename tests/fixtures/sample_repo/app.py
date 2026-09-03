from helpers import apply_discount


def validate_order(order):
    return bool(order)


def save_order(order):
    return order


def process_order(order):
    if not validate_order(order):
        raise ValueError("invalid order")
    order = apply_discount(order)
    return save_order(order)


class CheckoutService:
    def checkout(self, order):
        return self._process(order)

    def _process(self, order):
        return process_order(order)
