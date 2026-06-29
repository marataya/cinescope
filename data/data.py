# Response codes
OK = 200
BAD_REQUEST = 400
UNAUTHORIZED = 401
NOT_FOUND = 404

# Authentication
USERNAME = 'api1@gmail.com'
PASSWORD = 'asdqwe123Q'

# Headers
HEADERS = {'content-type': 'application/json'}

# test_GetBookingIds
all_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
valid_first_name = 'Susan'
non_existing_first_name = 'Ffdan'
valid_last_name = 'Ericsson'
non_existing_last_name = 'Qfasga'
valid_checkin_date = '2016-09-21'
valid_checkout_date = '2020-03-23'
non_existing_date = '2222-09-21'
invalid_format_date = '27.3.1943.'

# test_GetBooking
valid_id = '1'
valid_id_2 = '8'
invalid_id = '56'