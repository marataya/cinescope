import allure


@allure.epic("DB Test")
class TestDB:
    # def test_user_in_db(self, db_client, registered_user):
    #     rows = db_client.get_user_by_email(registered_user["email"])
    #     assert len(rows) == 1
    #     assert rows[0]["email"] == registered_user["email"]
    #     assert rows[0]["verified"] is True

    @allure.title("Пользователь в БД после регистрации")
    def test_registered_user_in_db(self, registered_user, db_helper):
        # registered_user у тебя dict, email достаем так
        user_db = db_helper.get_user_by_email(registered_user["email"])
        assert user_db is not None
        assert user_db.email == registered_user["email"]
        assert user_db.verified is True  # или False, смотря что делает /register
        assert "USER" in user_db.roles