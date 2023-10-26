from requests import put

def get_rgb_to_xy(color):
    # For the hue bulb, the corners of the triangle are:
    # - Red: 0.675, 0.322
    # - Green: 0.4091, 0.518
    # - Blue: 0.167, 0.04
    normalized_to_one = [0.0, 0.0, 0.0]
    cred, cgreen, cblue = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
    normalized_to_one[0] = cred
    normalized_to_one[1] = cgreen
    normalized_to_one[2] = cblue

    def adjust_color_channel(channel):
        if channel > 0.04045:
            return (channel + 0.055) / (1.0 + 0.055) ** 2.4
        else:
            return channel / 12.92

    red = adjust_color_channel(normalized_to_one[0])
    green = adjust_color_channel(normalized_to_one[1])
    blue = adjust_color_channel(normalized_to_one[2])

    X = red * 0.649926 + green * 0.103455 + blue * 0.197109
    Y = red * 0.234327 + green * 0.743075 + blue * 0.022598
    Z = red * 0.0000000 + green * 0.053077 + blue * 1.035763

    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)

    return [x, y]

# Example usage:
color = (128, 0, 128)  # Red color
xy_values = get_rgb_to_xy(color)

print(put(url=f"http://172.31.0.237/api/4eVBkbzkRPQOT-lpLqDfUjr6AjR7f3nGi857IG88/lights/4/state", json={"xy": xy_values, "bri": 255}).text)
