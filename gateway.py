class Gateway:
    def __init__(self) -> None:
        pass

    def water_pump(self):
        print("water pump on")

    def open_lid(self, open):
        if open:
            print("open lid")
        else:
            print("close lid")

    def fan(self, open):
        if open:
            print("fan on")
        else:
            print("fan off")

    def light(self, open):
        if open:
            print("light on")
        else:
            print("light off")

    def tank_light(self, open):
        if open:
            print("tank light on")
        else:
            print("tank light off")

            