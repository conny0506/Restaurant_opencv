from menu import Menu
if __name__ == "__main__":
    menu = Menu()

    categories = ["Starters", "Appetizers", "Main Course", "Desserts"]
    orders = {}
    for category in categories:
        menu.show_menu(category)
        order = menu.take_order_from_camera(category)
        if order:
            orders.update(order)

    menu.place_order(orders)
