import os
import sys

sys.path.append('/geometric_lib')

from circle import area as circle_area, perimeter as circle_perimeter
from square import area as square_area, perimeter as square_perimeter

def main():
    figure = os.getenv('FIGURE', 'circle')
    param1 = os.getenv('PARAM1')

    if not param1:
        print("Ошибка: не задан PARAM1")
        sys.exit(1)
    
    try:
        param1 = float(param1)
    except ValueError:
        print("Ошибка: PARAM1 должен быть числом")
        sys.exit(1)
    
    if figure == 'circle':
        print(f"Круг радиусом {param1}:")
        print(f"  Площадь = {circle_area(param1)}")
        print(f"  Периметр (длина окружности) = {circle_perimeter(param1)}")
    elif figure == 'square':
        print(f"Квадрат со стороной {param1}:")
        print(f"  Площадь = {square_area(param1)}")
        print(f"  Периметр = {square_perimeter(param1)}")
    else:
        print(f"Неизвестная фигура: {figure}. Допустимо: circle, square")
        sys.exit(1)

if __name__ == "__main__":
    main()