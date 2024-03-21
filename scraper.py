import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

load_dotenv()

url = os.environ.get("URL")
SCOPES = [os.environ.get("SCOPES")]
SAMPLE_RANGE_NAME = os.environ.get("RANGE")
SAMPLE_SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")


def main():
    creds = Credentials.from_service_account_file("creds.json", scopes=SCOPES)

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        while True:
            exchangeRateUpdater = []
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")

            table_data = soup.find("table", {"id": "content_table"})
            if table_data != None:
                first_row = table_data.find("tbody").find_all("tr")[0]
                first_td = first_row.find_all("td")[1]

                div_ca = first_td.find("div", class_="ca")

                if div_ca:
                    colU_N = div_ca.text.strip()
                else:
                    colU_N = first_row.find_all("td")[1].text.strip()

                colU_val = first_row.find_all("td")[3].text.strip().split()[0]
                firstRowRate = round(((1 / float(colU_val)) * 500) + 1, 2)
                colUR_val = first_row.find_all("td")[4].text.strip()

                firstRowDict = {
                    "name": colU_N,
                    "rate": firstRowRate,
                    "reserve": colUR_val,
                    "range": "Calculator!B17:B19",
                }

                exchangeRateUpdater.append(firstRowDict)
            else:
                print("Data not Found")

            rowU_data = soup.find("tr", onclick="ccl(1023, 10, 40, 0)")
            if rowU_data != None:
                div_ca = rowU_data.find_all("td")[1].find("div", class_="ca")

                if div_ca:
                    colU_N = div_ca.text.strip()
                else:
                    colU_N = rowU_data.find_all("td")[1].text.strip()

                colU_val = rowU_data.find_all("td")[3].text.strip().split()[0]
                UniChng = round(((1 / float(colU_val)) * 500) + 1, 2)

                colUR_val = rowU_data.find_all("td")[4].text.strip()

                UnionDict = {
                    "name": colU_N,
                    "rate": UniChng,
                    "reserve": colUR_val,
                    "range": "Calculator!D17:D19",
                }
                exchangeRateUpdater.append(UnionDict)
            else:
                print("UnioExchange Not Found")

            rowH_data = soup.find("tr", onclick="ccl(372, 10, 40, 0)")
            if rowH_data != None:

                div_ca = rowH_data.find_all("td")[1].find("div", class_="ca")

                if div_ca:
                    colH_N = div_ca.text.strip()
                else:
                    colH_N = rowH_data.find_all("td")[1].text.strip()

                colH_val = rowH_data.find_all("td")[3].text.strip().split()[0]
                HotExg = round(((1 / float(colH_val)) * 500) + 1, 2)

                colHR_val = rowH_data.find_all("td")[4].text.strip()

                HotDict = {
                    "name": colH_N,
                    "rate": HotExg,
                    "reserve": colHR_val,
                    "range": "Calculator!F17:F19",
                }
                exchangeRateUpdater.append(HotDict)
            else:
                print("Hot Exchange not Found")

            rowM_data = soup.find("tr", onclick="ccl(521, 10, 40, 0)")
            if rowM_data != None:

                div_ca = rowM_data.find_all("td")[1].find("div", class_="ca")

                if div_ca:
                    colM_N = div_ca.text.strip()
                else:
                    colM_N = rowM_data.find_all("td")[1].text.strip()

                colM_val = rowM_data.find_all("td")[3].text.strip().split()[0]
                Mine = round(((1 / float(colM_val)) * 500) + 1, 2)

                colMR_val = rowM_data.find_all("td")[4].text.strip()

                MineDict = {
                    "name": colM_N,
                    "rate": Mine,
                    "reserve": colMR_val,
                    "range": "Calculator!H17:H19",
                }
                exchangeRateUpdater.append(MineDict)
            else:
                print("Mine is not Found")

            payload = []
            cells_updated = 0

            for i in exchangeRateUpdater:
                payload = [i["name"]], [i["rate"]], [i["reserve"]]
                result = (
                    sheet.values()
                    .update(
                        spreadsheetId=SAMPLE_SPREADSHEET_ID,
                        range=i["range"],
                        valueInputOption="USER_ENTERED",
                        body={"values": payload},
                    )
                    .execute()
                )

                cells_updated += result.get("updatedCells")
                payload = []

            print(
                "{0} cells updated - time: {1}".format(
                    cells_updated,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                )
            )

            cells_updated = 0
            time.sleep(10)

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
