from sqlalchemy.orm import Session

from models.db_models.movie import MovieDBModel
from models.db_models.user import UserDBModel


class DBHelper:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    """Класс с методами для работы с БД в тестах"""

    def create_test_user(self, user_data: dict) -> UserDBModel:
        """Создает тестового пользователя"""
        user = UserDBModel(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def get_user_by_id(self, user_id: str):
        """Получает пользователя по ID"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    def get_user_by_email(self, email: str):
        """Получает пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    def get_movie_by_name(self, name: str) -> MovieDBModel | None:
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

    def get_movie_by_id(self, movie_id: int) -> MovieDBModel | None:
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()

    def movie_exists(self, movie_id: int) -> bool:
        return self.get_movie_by_id(movie_id) is not None

    def movie_exists_by_name(self, name: str) -> bool:
        return self.get_movie_by_name(name) is not None

    def delete_movie(self, movie: MovieDBModel):
        """Удаляет объект фильма"""
        if movie:
            self.db_session.delete(movie)
            self.db_session.commit()

    def delete_movie_by_id(self, movie_id: int) -> bool:
        """Удаляет фильм по ID. Возвращает True если удалил"""
        movie = self.get_movie_by_id(movie_id)
        if movie:
            self.delete_movie(movie)
            return True
        return False

    def delete_movie_by_name(self, name: str) -> bool:
        """Удаляет фильм по имени"""
        movie = self.get_movie_by_name(name)
        if movie:
            self.delete_movie(movie)
            return True
        return False
'''
Пример хелпера для movies
def get_movie_by_id(self, movie_id: str):
    """Получает фильм по ID"""
    return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()
'''
