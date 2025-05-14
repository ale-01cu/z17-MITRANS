RESOLUTIONS_AVILABLES = [
    '1920x1080',
    '1360x768',
]


BOT_CONFIG = {
    "1920x1080": {
        "FIND_CHATS_REFERENCE": {
            'min_width': 12,
            'max_width': 20,
            'min_height': 12,
            'max_height': 20,
        },
        "FIND_TEXT_AREA_CONTOURS": {
            'chat_limit_x_porcent': 0.6,
            'chat_start_x_porcent': 0.3,
            'chat_limit_x_porcent_in_message_requests_view': 0.5,
            'min_height': 40,
        },
        "GET_TEXTS_DID_NOT_WATCHED": {
            'x_start_offset': 10,
            'y_start_offset': 15,
            'scroll_move': 35,
        },
        "REVIEW_CHAT": {
            'scroll_move': 45,
        },
        "FIND_CURRENT_CHAT_ID": {
            'roi_x_start_porcent': 0.285,
        },
        "EXTRACT_CHAT_ID": {
            'y_sub': 25,
            'y_plus': 10,
            'x_sub': 313
        },
    },
    "1360x768": {
        "FIND_CHATS_REFERENCE": {
            'min_width': 10,
            'max_width': 20,
            'min_height': 10,
            'max_height': 20,
        },
        "FIND_TEXT_AREA_CONTOURS": {
            'chat_limit_x_porcent': 1,
            'chat_start_x_porcent': 0.4,
            'chat_limit_x_porcent_in_message_requests_view': 0.30,
            'min_height': 20,
        },
        "GET_TEXTS_DID_NOT_WATCHED": {
            'x_start_offset': 10,
            'y_start_offset': 10,
            'scroll_move': 25,
        },
        "REVIEW_CHAT": {
            'scroll_move': 35,
        },
        "FIND_CURRENT_CHAT_ID": {
            'roi_x_start_porcent': 0.32,
        },
        "EXTRACT_CHAT_ID": {
            'y_sub': 12,
            'y_plus': 10,
            'x_sub': 240
        },
    }
}