import pygame
from ui_classes import Display, Frame, Rect, Circle, Polygon, Ellipse, Shape, Text, Bar, Placement, DisplayObject


display_window = Display((800, 800), 'testing')

rectangle = Rect(20, 70, 130, 200, border=3)
circle = Circle(155, 275, 80, {Placement.TOP_LEFT: False}, color=(0, 150, 255), border=10)

polygon1 = Polygon([(80, 398), (100, 410), (100, 430), (80, 442), (60, 430), (60, 410)], color=(50, 0, 100))
polygon2 = Polygon([(100, 428), (120, 440), (120, 460), (100, 472), (80, 460), (80, 440)], color=(100, 0, 50))

ellipse1 = Ellipse(300, 50, 100, 200, color=(150, 0, 150), border=10)
ellipse2 = Ellipse(275, 75, 200, 100, color=(0, 150, 150), border=10)

text_single = Text('Double line test...', 400, 370, (50, 0, 200), alignment=Placement.LEFT, resize_max_width=250,
                   resize_max_height=100)

text = Text(
    """Testing Text DML:
- Use 1 to dec the bar and circle r
- Use 2 to inc the bar and circle r
- Use 7 to add poly corners
  and dec ellipse sizes
- Use 8 to remove poly corners
  and inc ellipse sizes
- Use 9 to swap ellipse colors""",
    400, 400, (0, 125, 255), alignment=Placement.TOP_LEFT, resize_max_width=250, resize_max_height=250,
    dynamic_multi_line=True, margin=20)
text_surround_rect = Rect(400, 400, 250, 250, color=(200, 200, 200))

bar = Bar(rectangle, bar_color=(255, 125, 0), bar_closed=True, start_fill_side=Placement.BOTTOM)


def update_window():
    display_window.fill((255, 255, 255))
    circle.render()
    polygon1.render()
    polygon2.render()
    ellipse1.render()
    ellipse2.render()
    bar.render()

    text_surround_rect.render()
    text.render()
    text_single.render()

    Bar.process_all_bar_movement()
    display_window.update()


def main():
    run = True
    bar.set_percentage(circle.radius - 30, set_instant=True)

    while run:
        Display.tick_frame()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

                if event.key == pygame.K_1:
                    circle.radius = max(circle.radius - 10, 30)
                    bar.modify_value(-10)

                elif event.key == pygame.K_2:
                    circle.radius = min(circle.radius + 10, 130)
                    bar.modify_value(10)

                elif event.key == pygame.K_3:
                    bar.modify_value(-10, set_bottom=True)
                    print(f'{bar.display_range} -> {bar.target_range}')

                elif event.key == pygame.K_4:
                    bar.modify_value(10, set_bottom=True)
                    print(f'{bar.display_range} -> {bar.target_range}')

                elif event.key == pygame.K_5:
                    bar.modify_value(-10)
                    print(f'{bar.display_range} -> {bar.target_range}')

                elif event.key == pygame.K_6:
                    bar.modify_value(10)
                    print(f'{bar.display_range} -> {bar.target_range}')

                elif event.key == pygame.K_7:
                    polygon1.insert_point((100, 398), 1)
                    polygon2.insert_point((80, 472), 4)

                    ellipse2.width = max(ellipse2.width - 10, 100)
                    ellipse1.height = max(ellipse1.height - 10, 100)

                elif event.key == pygame.K_8:
                    polygon1.remove_point((100, 398))
                    polygon2.remove_point((80, 472))

                    ellipse2.width = min(ellipse2.width + 10, 300)
                    ellipse1.height = min(ellipse1.height + 10, 300)

                elif event.key == pygame.K_9:
                    ellipse1.color, ellipse2.color = ellipse2.color, ellipse1.color

                elif event.key == pygame.K_i:
                    print(f'{bar.display_range} -> {bar.target_range}')

        update_window()


if __name__ == "__main__":
    main()