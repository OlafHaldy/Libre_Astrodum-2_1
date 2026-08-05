from core.rulerships import SIGN_RULER

def build_house_rulers(houses, positions):
    result = {}
    for house_number in range(1, 13):
        house = houses.get(house_number)
        if house is None:
            continue
        sign = house.get("sign")
        if sign is None:
            continue
        ruler = SIGN_RULER.get(sign)
        if ruler is None:
            continue
        planet = positions.get(ruler, {})
        result[house_number] = {
            "house": house_number,
            "sign": sign,
            "ruler": ruler,
            "planet_sign": planet.get("sign"),
            "planet_house": planet.get("house"),
            "planet_degree": planet.get("degree"),
            "retrograde": planet.get("retrograde", False),
        }
    return result