from datetime import datetime

import allure
import pytest
from sqlalchemy.orm import Session

from models.db_models.account_transaction_template import AccountTransactionTemplate
from models.db_models.movie import MovieDBModel
from utils.data_generator import DataGenerator


def transfer_money(session: Session, from_user: str, to_user: str, amount: int):
    """Имитация метода на беке - 1 транзакция"""
    from_acc = session.query(AccountTransactionTemplate).filter_by(user=from_user).with_for_update().one()
    to_acc = session.query(AccountTransactionTemplate).filter_by(user=to_user).with_for_update().one()

    if from_acc.balance < amount:
        raise ValueError("Недостаточно средств")

    from_acc.balance -= amount
    to_acc.balance += amount
    # commit делает вызывающий код, а не функция

@allure.epic("Database Transactions")
class TestTransaction:

    @allure.title("Успешный перевод денег между аккаунтами")
    def test_accounts_transaction_success(self, db_session: Session):
        # === Подготовка ===k
        stan_name = f"Stan_{DataGenerator.generate_random_int(10000)}"
        bob_name = f"Bob_{DataGenerator.generate_random_int(10000)}"

        stan = AccountTransactionTemplate(user=stan_name, balance=1000)
        bob = AccountTransactionTemplate(user=bob_name, balance=500)
        db_session.add_all([stan, bob])
        db_session.commit()

        try:
            # === До ===
            assert stan.balance == 1000
            assert bob.balance == 500

            # === Тест - успешный перевод ===
            transfer_money(db_session, stan_name, bob_name, 200)
            db_session.commit()

            # Обновляем из БД
            db_session.refresh(stan)
            db_session.refresh(bob)

            assert stan.balance == 800
            assert bob.balance == 700

        finally:
            # === Cleanup ===
            db_session.delete(stan)
            db_session.delete(bob)
            db_session.commit()

    @allure.title("Откат транзакции при недостатке средств - атомарность")
    def test_accounts_transaction_rollback_on_error(self, db_session: Session):
        # === Проверка атомарности: деньги не должны пропасть ===
        stan_name = f"Stan_{DataGenerator.generate_random_int(10000)}"
        bob_name = f"Bob_{DataGenerator.generate_random_int(10000)}"

        stan = AccountTransactionTemplate(user=stan_name, balance=100)
        bob = AccountTransactionTemplate(user=bob_name, balance=500)
        db_session.add_all([stan, bob])
        db_session.commit()

        try:
            # Пытаемся перевести больше чем есть
            with pytest.raises(ValueError, match="Недостаточно средств"):
                transfer_money(db_session, stan_name, bob_name, 200)
                db_session.commit()

            # Если ошибка - откатываем
            db_session.rollback()

            # Перечитываем и проверяем что балансы НЕ изменились
            db_session.refresh(stan)
            db_session.refresh(bob)

            assert stan.balance == 100, "Баланс списался хотя должен был откатиться"
            assert bob.balance == 500, "Баланс начислился хотя должен был откатиться"

        finally:
            db_session.query(AccountTransactionTemplate).filter(
                AccountTransactionTemplate.user.in_([stan_name, bob_name])
            ).delete()
            db_session.commit()

    @allure.title("Недостаточно средств - балансы остаются исходными")
    def test_accounts_transaction_insufficient_funds_keeps_original_balance(self, db_session: Session):
        """Когда у Stan недостаточно денег - балансы должны остаться исходными"""
        # === Подготовка ===
        stan_name = f"Stan_{DataGenerator.generate_random_int(10000)}"
        bob_name = f"Bob_{DataGenerator.generate_random_int(10000)}"

        stan = AccountTransactionTemplate(user=stan_name, balance=50)
        bob = AccountTransactionTemplate(user=bob_name, balance=500)
        db_session.add_all([stan, bob])
        db_session.commit()

        # Запоминаем оригинальные балансы ДО транзакции
        original_stan_balance = stan.balance
        original_bob_balance = bob.balance

        try:
            # === Тест - пытаемся перевести больше чем есть ===
            with pytest.raises(ValueError, match="Недостаточно средств"):
                transfer_money(db_session, stan_name, bob_name, 200)
                db_session.commit()  # не дойдет сюда

            # Важно: откатываем незавершенную транзакцию
            db_session.rollback()

            # === Проверка - балансы остались оригинальными ===
            db_session.refresh(stan)
            db_session.refresh(bob)

            assert stan.balance == original_stan_balance == 50, \
                f"Баланс Stan изменился после неуспешной транзакции: {stan.balance} != {original_stan_balance}"
            assert bob.balance == original_bob_balance == 500, \
                f"Баланс Bob изменился после неуспешной транзакции: {bob.balance} != {original_bob_balance}"

        finally:
            # === Cleanup ===
            db_session.query(AccountTransactionTemplate).filter(
                AccountTransactionTemplate.user.in_([stan_name, bob_name])
            ).delete()
            db_session.commit()

    @allure.title("Удаление фильма: проверка в БД, создание через session.add() если нет, удаление через API")
    def test_movie_delete_db_sync(self, super_admin, db_session, db_helper, created_genre):
        """
        Проверяет удаление фильма:
        1. Если фильма нет в БД - добавляет через session.add()
        2. Удаляет через API
        3. Проверяет что из БД тоже удалился
        """
        payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
        movie_name = payload["name"]
        movie_id = None

        try:
            # === 1. Проверка существования ===
            db_movie = db_helper.get_movie_by_name(movie_name)

            # === 2. Если нет - создаем через session.add() ===
            if db_movie is None:
                new_movie = MovieDBModel(
                    name=payload["name"],
                    price=payload["price"],
                    description=payload.get("description", "test description"),
                    image_url=payload.get("imageUrl") or payload.get("image_url") or "https://example.com/poster.jpg",
                    location=payload.get("location", "MSK"),
                    published=payload.get("published", True),
                    rating=float(payload.get("rating", 5.0)),  # FIX: было None
                    genre_id=created_genre,
                    created_at=datetime.utcnow(),
                )
                db_session.add(new_movie)
                db_session.commit()
                db_session.refresh(new_movie)
                movie_id = new_movie.id
            else:
                movie_id = db_movie.id

            # === 3. ДО удаления - должен существовать ===
            assert db_helper.movie_exists(movie_id) is True
            assert db_helper.get_movie_by_name(movie_name) is not None

            # === 4. Удаление через API ===
            super_admin.api.movies_api.send_request(
                "DELETE", f"/movies/{movie_id}", expected_status=200
            )
            db_session.expire_all()  # сбрасываем кеш сессии

            # === 5. ПОСЛЕ удаления - проверяем хелперами ===
            assert db_helper.get_movie_by_id(movie_id) is None, "Фильм остался в БД по id"
            assert db_helper.get_movie_by_name(movie_name) is None, "Фильм остался в БД по name"
            assert db_helper.movie_exists(movie_id) is False
            assert db_helper.movie_exists_by_name(movie_name) is False

        finally:
            # === 6. Cleanup через хелпер ===
            if movie_id and db_helper.movie_exists(movie_id):
                db_helper.delete_movie_by_id(movie_id)