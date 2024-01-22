import cv2
import numpy as np

class Menu:
    def __init__(self):
        self.menu_items = {
            "Starters": {"Soup": {"Price": 15, "Color": "Blue", "Shape": "Square"},
                         "Cheese Plate": {"Price": 20, "Color": "Blue", "Shape": "Round"},
                         "Garlic Bread": {"Price": 10, "Color": "Blue", "Shape": "Triangle"}},

            "Appetizers": {"Crispy Chicken": {"Price": 25, "Color": "Green", "Shape": "Square"},
                           "Fish Chips": {"Price": 30, "Color": "Green", "Shape": "Round"},
                           "Omelette": {"Price": 18, "Color": "Green", "Shape": "Triangle"}},

            "Main Course": {"Meatballs": {"Price": 40, "Color": "Yellow", "Shape": "Square"},
                            "Casserole": {"Price": 35, "Color": "Yellow", "Shape": "Round"},
                            "Fajita": {"Price": 45, "Color": "Yellow", "Shape": "Triangle"}},

            "Desserts": {"Souffle": {"Price": 22, "Color": "Red", "Shape": "Square"},
                         "Tiramisu": {"Price": 28, "Color": "Red", "Shape": "Round"},
                         "Cheesecake": {"Price": 30, "Color": "Red", "Shape": "Triangle"}}
        }

        

    def show_menu(self, menu_category):
        dishes = self.menu_items.get(menu_category)

        if dishes is not None:
            print(f"{menu_category} Menu:")
            for dish, details in dishes.items():
                color_and_shape_info = f"Color: {details['Color']}, Shape: {details['Shape']}"
                print(f"  {dish}: {details['Price']} TL - {color_and_shape_info}")
            print()
        else:
            print(f"No {menu_category} Menu found.")

    def take_order_from_camera(self, menu_category):
        dishes = self.menu_items.get(menu_category)

        if dishes is not None:
            cap = cv2.VideoCapture(0)
            order_taken = False
            order = {}

            while True:
                ret, frame = cap.read()

                if not ret:
                    print("Unable to open the camera.")
                    break

                # Determine current color and shape
                color_and_shape = self.current_color_and_shape(frame)
                if color_and_shape:
                    color_str = color_and_shape['Color']
                    shape_str = color_and_shape['Shape']
                    cv2.putText(frame, f"Color: {color_str}, Shape: {shape_str}", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.imshow("Camera View", frame)

                key = cv2.waitKey(1)
                if key == 27:  # Exit when the ESC key is pressed
                    break
                elif key == ord('s') and not order_taken:  # Take order only if not taken before
                    order = self.choose_dish(frame, dishes)
                    if order:
                        order_taken = True
                        selected_dish = list(order.keys())[0]
                        print(f"Order you choose: {selected_dish}")
                        print("Is this your order? ('Y' for Yes, 'N' for No)")
                elif key == ord('y') and order_taken:
                    print("Your order has been confirmed.")
                    break
                elif key == ord('n') and order_taken:
                    print("Your order has been cancelled.")
                    order_taken = False
                elif key == ord('n') and not order_taken:
                    print("You can choose another product.")
                    order = {}
                    print(f"{menu_category} Menu:")
                    for dish, details in dishes.items():
                        print(f"  {dish}: {details['Price']} TL")
                    print()
                elif key == ord('s') and order_taken:  # Inform if the order has already been taken
                    print("Order already taken. Cannot take another order.")

            cv2.waitKey(1)
            cv2.destroyAllWindows()
            cap.release()

            return order
        else:
            print(f"No {menu_category} Menu found.")



    def choose_dish(self, frame, dishes):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = self.detect_color_and_shape(frame)
        if mask is None:
            print("Color and shape distinctions could not be made.")
            return {}

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        order = {}
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                # Apply Convex Hull
                hull = cv2.convexHull(contour)
                epsilon = 0.02 * cv2.arcLength(hull, True)
                approx = cv2.approxPolyDP(hull, epsilon, True)

                # Determine the shape more precisely
                if len(approx) == 3:
                    shape = "Triangle"
                elif len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(hull)
                    aspect_ratio = float(w) / h

                    # Compare aspect ratio with predefined values for each shape
                    if 0.8 <= aspect_ratio <= 1.2:
                        shape = "Square"
                    elif aspect_ratio < 0.8:
                        shape = "Triangle"
                    else:
                        shape = "Round"
                else:
                    shape = "Round"

                for dish, details in dishes.items():
                    if details["Shape"] == shape:
                        order[dish] = details

                        
                        color_and_shape = self.current_color_and_shape(frame)
                        if color_and_shape:
                            color_str = color_and_shape['Color']
                            shape_str = color_and_shape['Shape']
                            cv2.putText(frame, f"Color: {color_str}, Shape: {shape_str}", (50, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            cv2.putText(frame, f"Your Order: {dish}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                            cv2.imshow("Camera View", frame)
                            cv2.waitKey(500)  # Wait for 0.5 seconds to capture the image

        return order


    def detect_color_and_shape(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        
        colors = {
            "Red": ((0, 100, 100), (10, 255, 255)),
            "Yellow": ((20, 100, 100), (40, 255, 255)),
            "Green": ((40, 100, 100), (80, 255, 255)),
            "Blue": ((100, 100, 100), (140, 255, 255))
        }

        for color, (lower_color, upper_color) in colors.items():
            mask = cv2.inRange(hsv, np.array(lower_color), np.array(upper_color))

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:
                    # Apply Convex Hull
                    hull = cv2.convexHull(contour)
                    epsilon = 0.02 * cv2.arcLength(hull, True)
                    approx = cv2.approxPolyDP(hull, epsilon, True)

                    # Determine the shape
                    if len(approx) == 3:
                        shape = "Triangle"
                    elif len(approx) == 4:
                        x, y, w, h = cv2.boundingRect(hull)
                        aspect_ratio = float(w) / h
                        shape = "Square" if 0.95 <= aspect_ratio <= 1.05 else "Rectangle"
                    else:
                        shape = "Round"

                    return mask

        return None
        

    def place_order(self, orders):
        total_price = 0
        print("Orders:")
        for dish, details in orders.items():
            print(f"  {dish}: {details['Price']} TL")
            total_price += details['Price']

        print(f"Total Price: {total_price} TL")

    def current_color_and_shape(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Color and shape definitions
        colors = {
            "Red": ((0, 100, 100), (10, 255, 255)),
            "Yellow": ((20, 100, 100), (40, 255, 255)),
            "Green": ((40, 100, 100), (80, 255, 255)),
            "Blue": ((100, 100, 100), (140, 255, 255))
        }

        for color, (lower_color, upper_color) in colors.items():
            mask = cv2.inRange(hsv, np.array(lower_color), np.array(upper_color))

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:
                    # Apply Convex Hull
                    hull = cv2.convexHull(contour)
                    epsilon = 0.02 * cv2.arcLength(hull, True)
                    approx = cv2.approxPolyDP(hull, epsilon, True)

                    # Determine the shape more precisely
                    if len(approx) == 3:
                        shape = "Triangle"
                    elif len(approx) == 4:
                        x, y, w, h = cv2.boundingRect(hull)
                        aspect_ratio = float(w) / h
                        shape = "Square"
                    else:
                        shape = "Round"

                    return {"Color": color, "Shape": shape}

        return None