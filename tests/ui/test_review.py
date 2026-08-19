import random

import allure
import pytest
from playwright.sync_api import Page, expect


@allure.title("UI: Создание и удаление отзыва")
@pytest.mark.slow
def test_add_and_delete_movie_review(login_page, movie_page, page: Page, common_user, created_movie):

    login_page.login(common_user.email, common_user.password)

    movie_page.open(created_movie)

    review_text = f"review_{random.randint(1000,9999)} awesome movie!"
    rng = random.Random()  # без seed = системное время
    rating = rng.randint(1,5)

    movie_page.add_review(text=review_text, rating=rating)

    # 1. Проверяем ТОЛЬКО наш отзыв, а не рейтинг 1/5
    expect(movie_page.get_review_by_text(review_text)).to_be_visible(timeout=10000)

    # 2. Удаляем
    movie_page.delete_review(review_text)

    # 3. Проверяем что пропал
    expect(movie_page.get_review_by_text(review_text)).not_to_be_visible(timeout=10000)