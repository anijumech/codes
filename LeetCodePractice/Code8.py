import requests
from bs4 import BeautifulSoup


def print_secret_message(url):

    #extract url and parse the table
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    data = []

    # go through every row and try to pull out x, char, y
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

    #grid size
    max_x = max(x for x, y, char in data)
    max_y = max(y for x, y, char in data)

    grid = [[" "] * (max_x + 1) for i in range(max_y + 1)]

    for x, y, char in data:
        grid[max_y - y][x] = char

    for row in grid:
        print("".join(row))

# get the url from user
url = input("Enter the google doc url ->")
print_secret_message(url)