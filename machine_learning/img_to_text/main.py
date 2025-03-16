from img_handler import ImgHandler

IMG_PATH = 'C:/Users/Ale z17/Desktop/z17-MITRANS/machine_learning/img_to_text/imgs_test/messenger_light.jpg'
IMG_PATH_DARK = 'C:/Users/Ale z17/Desktop/z17-MITRANS/machine_learning/img_to_text/imgs_test/messenger_dark.jpg'
CONFIG = {
    'LIGHT_IMG_TEXT_BG': {
        'hex': '#f1f2f6',
        'tolerance-lower-b': 20,
        'tolerance-lower-g': 20,
        'tolerance-lower-r': 20,
        'tolerance-upper-b': 13,
        'tolerance-upper-g': 13,
        'tolerance-upper-r': 13,
    },
    'DARK_IMG_TEXT_BG': {
        'hex': '#333333',
        'tolerance-lower-b': 13,
        'tolerance-lower-g': 13,
        'tolerance-lower-r': 13,
        'tolerance-upper-b': 20,
        'tolerance-upper-g': 20,
        'tolerance-upper-r': 20,
    },
}


def img_to_text():
    img = ImgHandler(IMG_PATH_DARK)
    is_dark_mode = img.is_dark_mode()
    mode = 'DARK_IMG_TEXT_BG' if is_dark_mode else 'LIGHT_IMG_TEXT_BG'

    img.hex_to_rgb_color(CONFIG[mode]['hex'] if
                         is_dark_mode else CONFIG['LIGHT_IMG_TEXT_BG']['hex']
                         )

    img.set_color_tolerance(tolerance_lower_r=CONFIG[mode]['tolerance-lower-r'],
                            tolerance_lower_g=CONFIG[mode]['tolerance-lower-g'],
                            tolerance_lower_b=CONFIG[mode]['tolerance-lower-b'],
                            tolerance_upper_r=CONFIG[mode]['tolerance-upper-r'],
                            tolerance_upper_g=CONFIG[mode]['tolerance-upper-g'],
                            tolerance_upper_b=CONFIG[mode]['tolerance-upper-b'])
    img.create_mask()
    img.create_result()
    img.save_results()


def main():
    img_to_text()

if __name__ == '__main__':
    main()
