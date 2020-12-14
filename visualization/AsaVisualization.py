import os
from PIL import Image, ImageDraw
from PIL import ImageFont

from ASA import ASA
from dotenv import load_dotenv


class ASADrawer:
    draw_number = 0

    def __init__(self, font_path, window_size=(2800, 1080)):
        self.font_path = font_path
        self.width, self.height = window_size

        self.asa_height = 120
        self.asa_half_width = 40

        self.node_width = 50
        self.node_height = 140
        self.asa_margin_in_node = 10

        self.asa_keys_and_cords = {}

    def draw_asa_element(self, dr, center_elem, counter, key):
        main_left = (center_elem[0] - self.asa_half_width, center_elem[1])
        main_right = (center_elem[0] + self.asa_half_width, center_elem[1] + self.asa_height)

        counter_margin = 2
        counter_left = (main_left[0] + counter_margin, main_left[1] + 2)
        counter_right = (main_right[0] - counter_margin, center_elem[1] + self.asa_half_width)

        c_font = ImageFont.truetype(self.font_path, 32)
        counter_font_offset = c_font.getsize(str(counter))[0] // 2
        c_text_cord = [center_elem[0] - counter_font_offset, center_elem[1]]

        # TODO check if font with given size will fit into the asa element
        k_font = ImageFont.truetype(self.font_path, 60)
        main_text_offset = k_font.getsize(str(key))[0] // 2
        k_text_cord = [center_elem[0] - main_text_offset, center_elem[1] + self.asa_half_width]

        dr.rectangle([main_left, main_right], outline='black', width=3)
        dr.rectangle([counter_left, counter_right], outline='grey', width=2)

        dr.text(c_text_cord, str(counter), font=c_font, fill='black')
        dr.text(k_text_cord, str(key), font=k_font, fill='black')

        return {
            'upper_left': main_left,
            'middle_left': (main_left[0], main_left[1] + self.asa_height//2),
            'down_left': (main_left[0], main_right[1]),

            'upper_right': (main_right[0], main_left[1]),
            'middle_right': (main_right[0], main_left[1] + self.asa_height//2),
            'down_right': main_right
        }

    def draw_node_overlay(self, dr, center, width_delta):
        left = (center[0] - width_delta, center[1])
        right = (center[0] + width_delta, center[1] + self.node_height)
        dr.rectangle([left, right], outline='black', width=3)

        return left, right

    def draw_node(self, dr, node, center):
        asa_cords = []
        keys = node.keys

        if len(keys) == 1:
            width_delta = self.node_width
            left, right = self.draw_node_overlay(dr, center, width_delta)
            elem = keys[0]
            new_center = [center[0], center[1] + self.asa_margin_in_node]
            new_cords = self.draw_asa_element(dr, new_center, elem.count, elem.key)
            asa_cords.append(new_cords)
            self.asa_keys_and_cords[elem.key] = new_cords

        else:
            width_delta = 2 * self.node_width
            left, right = self.draw_node_overlay(dr, center, width_delta)
            for i, elem in enumerate(keys):
                new_center = [center[0] - self.node_width + width_delta * i, center[1] + self.asa_margin_in_node]
                new_cords = self.draw_asa_element(dr, new_center, elem.count, elem.key)
                asa_cords.append(new_cords)
                self.asa_keys_and_cords[elem.key] = new_cords

        return {
            'node_anchors':
                {
                    'upper_left': left,
                    'upper_middle': (left[0] + width_delta, left[1]),
                    'upper_right': (right[0], left[1]),

                    'down_left': (left[0], right[1]),
                    'down_middle': (left[0] + width_delta, right[1]),
                    'down_right': right
                },
            'asa_anchors': asa_cords
        }

    def draw_tree(self, draw, node, center, t_heigh, up_connection_point=None, connect_to=None):
        node_data = self.draw_node(draw, node, center)
        if up_connection_point and connect_to:
            draw.line([node_data['node_anchors'][connect_to], up_connection_point], fill='black', width=6)

        if node.children:
            ch_len = len(node.children)
            if ch_len == 0:
                return

            off = self.node_width + self.asa_margin_in_node

            offsets = [-1 * 2*off, 2*off]
            up_connection_points = [
                node_data['node_anchors']['down_left'],
                node_data['node_anchors']['down_right']
            ]
            connect_to_points = [
                'upper_right' if len(node.children[0].keys) < 2 else 'upper_middle',
                'upper_left' if len(node.children[1].keys) < 2 else 'upper_middle'
            ]

            if ch_len == 3:
                offsets = [-1 * 4*off, 0, 4*off]
                up_connection_points.insert(1, node_data['node_anchors']['down_middle'])
                connect_to_points = [
                    'upper_right' if len(node.children[0].keys) < 2 else 'upper_middle',
                    'upper_middle',
                    'upper_left' if len(node.children[2].keys) < 2 else 'upper_middle'
                ]

            for i, ch in enumerate(node.children):
                self.draw_tree(
                    draw, ch,
                    (center[0] + offsets[i] * t_heigh ** 2, center[1] + 180),
                    t_heigh - 1, up_connection_points[i], connect_to_points[i]
                )

    def draw_d_queue(self, draw, asa):
        curr = asa.sorted_d_queue.min

        while curr:
            key = curr.key
            cords = self.asa_keys_and_cords[key]

            suc = curr.successor
            if not suc:
                break

            s_key = suc.key
            s_cords = self.asa_keys_and_cords[s_key]

            if cords['upper_left'][1] == s_cords['upper_left'][1]:
                draw.line([cords['middle_right'], s_cords['middle_left']], fill='blue', width=4)

            elif cords['upper_left'][1] < s_cords['upper_left'][1]:
                draw.line([cords['down_right'], s_cords['upper_left']], fill='blue', width=4)

            else:
                draw.line([cords['upper_right'], s_cords['down_left']], fill='blue', width=4)

            curr = suc

    def draw_asa(self, asa):
        root = asa.root
        curr = root

        h = 0
        while curr.children:
            h += 1
            curr = curr.children[0]

        img = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        middle_up = (self.width // 2, 0)

        self.draw_tree(draw, root, middle_up, h)
        self.draw_d_queue(draw, asa)
        img.save(f'test_{self.draw_number}.jpg', format='JPEG')
        self.draw_number += 1


if __name__ == '__main__':
    load_dotenv()

    font_path = os.getenv('FONT_PATH')
    drawer = ASADrawer(font_path, (2800, 700))
    asa = ASA()
    asa.insert(1)
    asa.insert(1)
    asa.insert(1)
    asa.insert(1)

    drawer.draw_asa(asa)

    asa.insert(3)
    drawer.draw_asa(asa)

    asa.insert(5)
    drawer.draw_asa(asa)

    asa.insert(2)
    drawer.draw_asa(asa)
    #
    asa.insert(7)
    drawer.draw_asa(asa)
    #
    asa.insert(4)
    drawer.draw_asa(asa)

    asa.insert(8)
    drawer.draw_asa(asa)

    asa.insert(9)
    drawer.draw_asa(asa)

    asa.insert(4.5)
    drawer.draw_asa(asa)

    asa.insert(4.2)
    drawer.draw_asa(asa)

    asa.insert(4.3)
    drawer.draw_asa(asa)

    asa.insert(4.4)
    drawer.draw_asa(asa)

    asa.insert(10)
    drawer.draw_asa(asa)

    asa.insert(11)
    drawer.draw_asa(asa)

    asa.insert(4.5)
    drawer.draw_asa(asa)

    asa.insert(4.6)
    drawer.draw_asa(asa)

    asa.insert(4.7)
    drawer.draw_asa(asa)

    asa.insert(4.8)
    drawer.draw_asa(asa)

    asa.insert(6.9)
    drawer.draw_asa(asa)

    asa.insert(9.1)
    drawer.draw_asa(asa)

    asa.insert(13)
    drawer.draw_asa(asa)

    asa.insert(3.2)
    drawer.draw_asa(asa)
