from typing import TYPE_CHECKING
import random
import math

from trade_simulator.amm_agents.basic_amm import AMM

if TYPE_CHECKING:
    from trade_simulator.order.order import Order
    from trade_simulator.pool.pool import Pool


class MarianaAMM(AMM):
    def __init__(self, pool: "Pool", weights: dict[str, float] = None, fee_rate: float = 0, **kwargs):
        """
        pool.tokens_info: словарь вида {'EUR': amount_eur, 'SGD': amount_sgd, 'CHF': amount_chf}
        weights: словарь весов для каждого токена, сумма весов должна быть =1. Если None — ставим равные веса.
        fee_rate: комиссия с входящего объёма (например, 0.05%)
        """
        super().__init__(pool, **kwargs)
        # Инициализируем веса
        symbols = list(pool.tokens_info.keys())
        if weights is None:
            w = 1.0 / len(symbols)
            self.weights = {t: w for t in symbols}
        else:
            self.weights = weights

        print(self.weights)

        self.fee_rate = fee_rate
        # Вычисляем начальный инвариант k = ∏ R_i^{w_i}
        self.k = self._compute_invariant(pool.tokens_info)

    def _compute_invariant(self, reserves: dict[str, float]) -> float:
        k = 1.0
        for token, R in reserves.items():
            k *= R ** self.weights[token]
        return k

    def execute_order(self, order: "Order"):
        """
        order.operation_type: "BUY" или "SELL"
        order.token: токен-цель (для BUY) или токен-продажи (для SELL)
        order.token_volume: запрошенный объём целевого (для BUY) или продаваемого (для SELL) токена
        """
        if order.status != "Awaiting":
            return

        # 1) Определяем direction и входной/выходной токен
        if order.operation_type == "BUY":
            want = order.token
            give = [t for t in self.pool.tokens_info if t != want]
            # Выбираем один из других — в Mariana арбитраж распределяется по всем, но для простоты:
            # пусть Trader отдаёт только один другой токен (обычно по наилучшему курсу)
            give = random.choice(give)
            amount_out = order.token_volume

            # сколько надо подать (до комиссии)?
            # находим новую величину R_want': решение f(R') = k / ∏_{j≠want} R_j^{w_j}
            R = self.pool.tokens_info
            fixed_prod = 1.0
            for t in R:
                if t != want:
                    fixed_prod *= R[t] ** self.weights[t]
            # R_want' = (k / fixed_prod)^(1/w_want)
            R_want_new = (self.k / fixed_prod) ** (1.0 / self.weights[want])
            real_out = R[want] - R_want_new
            if real_out < amount_out:
                # не хватит ликвидности
                order.status = "Canceled"
                return
            # корректируем: если трейдер хочет ровно amount_out, мы подбираем вход:
            # amount_in_before_fee = solution Δ so that real_out == amount_out
            # из уравнения: R_want_new = R[want] - amount_out
            R_want_target = R[want] - amount_out
            required_prod = self.k / fixed_prod
            # объём входящего токена:
            # решаем (R[give] + Δ)^{w_give} * R_want_target^{w_want} * ∏_{j≠want,give} R_j^{w_j} == k
            # => (R[give] + Δ) = (k / (R_want_target^{w_want} * ∏ others))^(1/w_give)
            prod_others = 1.0
            for t in R:
                if t not in (want, give):
                    prod_others *= R[t] ** self.weights[t]
            numerator = self.k / ( (R_want_target ** self.weights[want]) * prod_others )
            R_give_new = numerator ** (1.0 / self.weights[give])
            amount_in = R_give_new - R[give]
            # комиссия
            fee = amount_in * self.fee_rate
            amount_in_with_fee = amount_in + fee

            # Проверка баланса трейдера
            if order.trader.portfolio[give] < amount_in_with_fee:
                order.status = "Canceled"
                return

            # 2) Обновляем балансы
            # трейдер отдает
            order.trader.portfolio[give] -= amount_in_with_fee
            self.pool.tokens_info[give] += amount_in
            # трейдер получает
            order.trader.portfolio[want] += amount_out
            self.pool.tokens_info[want] -= amount_out

        else:  # SELL
            sell = order.token
            buy = [t for t in self.pool.tokens_info if t != sell][0]
            amount_in = order.token_volume

            # комиссия
            fee = amount_in * self.fee_rate
            net_in = amount_in - fee

            # обновлённые резервы по входу
            R = self.pool.tokens_info
            R_sell_new = R[sell] + net_in

            # фиксируем произведение других
            prod_others = 1.0
            for t in R:
                if t != sell:
                    prod_others *= R[t] ** self.weights[t]
            # находим новый резерв buy: R_buy' = (k / ∏_{j≠buy} R_j^{w_j})^(1/w_buy)
            fixed_prod = 1.0
            for t in R:
                if t != buy:
                    if t == sell:
                        fixed_prod *= R_sell_new ** self.weights[t]
                    else:
                        fixed_prod *= R[t] ** self.weights[t]
            R_buy_new = (self.k / fixed_prod) ** (1.0 / self.weights[buy])

            amount_out = R[buy] - R_buy_new
            if amount_out <= 0:
                order.status = "Canceled"
                return

            if order.trader.portfolio[sell] < amount_in:
                order.status = "Canceled"
                return

            # 2) Обновляем балансы
            order.trader.portfolio[sell] -= amount_in
            self.pool.tokens_info[sell] += net_in

            order.trader.portfolio[buy] += amount_out
            self.pool.tokens_info[buy] -= amount_out

        # Всё успешно
        order.status = "Succeed"

        # Пересчитываем инвариант (ресервы поменялись)
        self.k = self._compute_invariant(self.pool.tokens_info)

    def sort_orders(self):
        # Сохраняем тот же подход FIFO + приоритеты
        random.shuffle(self.pool.order_book)
        self.pool.order_book = sorted(
            self.pool.order_book,
            key=lambda o: (o.creation_timestamp, o.priority)
        )
