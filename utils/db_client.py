# import psycopg2
# from psycopg2.extras import RealDictCursor
# from resources.db_creds import DBCreds
#
# class DBClient:
#     def __init__(self):
#         self.conn = None
#
#     def connect(self):
#         self.conn = psycopg2.connect(**DBCreds.get_psycopg_dict())
#         return self.conn
#
#     def close(self):
#         if self.conn:
#             self.conn.close()
#
#     def execute(self, query: str, params=None, fetch=False):
#         """Универсальный метод"""
#         conn = self.connect()
#         try:
#             with conn.cursor(cursor_factory=RealDictCursor) as cur:
#                 cur.execute(query, params)
#                 if fetch:
#                     result = cur.fetchall()
#                 else:
#                     conn.commit()
#                     result = None
#             return result
#         finally:
#             self.close()
#
#     def get_user_by_email(self, email: str):
#         return self.execute(
#             "SELECT * FROM users WHERE email = %s",
#             (email,),
#             fetch=True
#         )