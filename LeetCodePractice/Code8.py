import requests
from bs4 import BeautifulSoup


def print_secret_message(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    data = []

    for row in table.find_all("tr"):
        cells = row.find_all("td")

        if len(cells) == 3:
            try:
                x = int(cells[0].text.strip())
                char = cells[1].text.strip()
                y = int(cells[2].text.strip())
                data.append((x, y, char))
            except ValueError:
                pass

    if not data:
        return

    max_x = max(x for x, y, char in data)
    max_y = max(y for x, y, char in data)

    grid = [[" "] * (max_x + 1) for _ in range(max_y + 1)]

    for x, y, char in data:
        grid[max_y - y][x] = char

    for row in grid:
        print("".join(row))


print_secret_message(
    "https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub"
)