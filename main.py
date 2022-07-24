import requests
from bs4 import BeautifulSoup
import argparse
import sqlite3

subjectToan = "Toán"
subjectLi = "Lí"
subjectHoa = "Hóa"
subjectSinh = "Sinh"
subjectVan = "Văn"
subjectSu = "Sử"
subjectDia = "Địa"
subjectNgoaiNgu = "Ngoại ngữ"
subjectGDCD = "GDCD"

# http://thptbacthanglong.edu.vn/ma-so-giao-duc-tat-ca-tinh-thanh-tren-ca-nuoc-bid1576.html
sbdEnds = {
    2: 2090000,
    4: 4013000,
    33: 33014000,
    37: 37019000,
    38: 38015000,
    39: 39011000,
    41: 41015000,
    43: 43011000,
    44: 44013000,
    47: 47013000,
    48: 48032000,
    51: 51019000,
    52: 52013000,
    55: 55013000,
    57: 57011000,
    58: 58010000,
    59: 59011000,
    60: 60007000,
    61: 61011000,
    63: 63007000,
    64: 64007000,
}


def convertSBDToStr(sbd):
    sbdStr = str(sbd)
    if len(sbdStr) == 7:
        sbdStr = "0" + sbdStr

    return sbdStr


# sbd aka so bao danh
# return exist, mapReuslt
# Example 39000001
def getSingleFromVietnamnet(sbd):
    rsp = requests.get(
        "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-thi-tot-nghiep-thpt/2022/"
        + convertSBDToStr(sbd)
        + ".html"
    )
    # print(rsp.content)

    if rsp.status_code != 200:
        print(
            "WARNING: status code not ok",
            rsp.status_code,
        )
        return False, None

    soup = BeautifulSoup(rsp.content, "html.parser")
    # print(soup.prettify())

    divResult = soup.find("div", "resultSearch__right")
    if not divResult:
        return False, None
    # print(divResult)

    tdResults = divResult.find_all("td")
    # print(tdResults)

    # Always divisible by 2
    if len(tdResults) % 2 != 0:
        print("WARNING: invalid number of tdResults", tdResults)
        return False, None

    # tdResults is a list of td mixed with names and result
    mapResult = {}
    for i in range(len(tdResults) // 2):
        subject = tdResults[i * 2].text.strip()
        point = tdResults[i * 2 + 1].text.strip()
        if point == "":
            point = "0"
        mapResult[subject] = float(point)
    # print(mapResult)

    return True, mapResult


def getListFromVietnamnet(sbdStart, sbdEnd):
    results = []

    for sbd in range(sbdStart, sbdEnd + 1):
        exist, mapResult = getSingleFromVietnamnet(sbd)
        if not exist:
            print("WARNING: sbd not exist", sbd)
            continue

        # Ma so gddt
        gddtWhere = convertSBDToStr(sbd)[:2]

        singleResult = [convertSBDToStr(sbd), gddtWhere, mapResult]
        # print(singleResult)
        results.append(singleResult)

    return results


# Same as getListFromVietnamnet but with SQlite
def writeSQLiteListFromVietnamnetThen(conn, sbdStart, sbdEnd):
    cur = conn.cursor()

    for sbd in range(sbdStart, sbdEnd + 1):
        rows = cur.execute(
            """SELECT * FROM university_vietnam_2022 WHERE sbd = ?""",
            (convertSBDToStr(sbd),),
        ).fetchall()
        if len(rows) >= 1:
            print("WARNING: sbd already exist in SQLite", sbd)
            continue

        exist, mapResult = getSingleFromVietnamnet(sbd)
        if not exist:
            print("WARNING: sbd not exist", sbd)
            continue

        # Ma so gddt
        gddtWhere = convertSBDToStr(sbd)[:2]

        cur.execute(
            """INSERT INTO university_vietnam_2022 (sbd, gddt, toan, li, hoa, sinh, van, su, dia, ngoai_ngu, gdcd) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                convertSBDToStr(sbd),
                gddtWhere,
                mapResult.get(subjectToan, 0),
                mapResult.get(subjectLi, 0),
                mapResult.get(subjectHoa, 0),
                mapResult.get(subjectSinh, 0),
                mapResult.get(subjectVan, 0),
                mapResult.get(subjectSu, 0),
                mapResult.get(subjectDia, 0),
                mapResult.get(subjectNgoaiNgu, 0),
                mapResult.get(subjectGDCD, 0),
            ),
        )

        conn.commit()


def generateSBD(gdtt):
    sbdStart = gdtt * 1000000 + 1
    sbdEndMax = (gdtt + 1) * 1000000 - 1

    return sbdStart, sbdEndMax


def writeCSVVietnamnet(filename, results):
    with open(filename, "w") as f:
        f.write(
            ",".join(
                [
                    "sbd",
                    "gddt",
                    subjectToan,
                    subjectLi,
                    subjectHoa,
                    subjectSinh,
                    subjectVan,
                    subjectSu,
                    subjectDia,
                    subjectNgoaiNgu,
                    subjectGDCD,
                ]
            )
            + "\n"
        )

        for result in results:
            sbd = result[0]
            gddt = result[1]
            mapResult = result[2]
            # print(mapResult)

            if not sbd or not gddt or not mapResult:
                print("WARNING: invalid result", result)
                continue

            f.write(
                ",".join(
                    [
                        str(sbd),
                        str(gddt),
                        str(mapResult.get(subjectToan, 0)),
                        str(mapResult.get(subjectLi, 0)),
                        str(mapResult.get(subjectHoa, 0)),
                        str(mapResult.get(subjectSinh, 0)),
                        str(mapResult.get(subjectVan, 0)),
                        str(mapResult.get(subjectSu, 0)),
                        str(mapResult.get(subjectDia, 0)),
                        str(mapResult.get(subjectNgoaiNgu, 0)),
                        str(mapResult.get(subjectGDCD, 0)),
                    ]
                )
                + "\n"
            )


def initSQLite(filename):
    conn = sqlite3.connect(filename)

    cur = conn.cursor()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS university_vietnam_2022 (sbd text, gddt text, toan real, li real, hoa real, sinh real, van real, su real, dia real, ngoai_ngu real, gdcd real)"""
    )

    conn.commit()

    return conn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gddt", type=int, help="Ma so gddt")

    args = parser.parse_args()
    print("gddt", args.gddt)

    sbdStart, sbdEndMax = generateSBD(args.gddt)
    sbdEnd = sbdEnds.get(args.gddt, sbdEndMax)
    print(
        "sbdStart",
        sbdStart,
        "sbdEnd",
        sbdEnd,
    )

    # Write CSV
    # results = getListFromVietnamnet(sbdStart, sbdEnd)
    # writeCSVVietnamnet(str(args.gddt) + ".csv", results)

    # Write SQLite
    csvFilename = str(args.gddt) + ".sqlite3"
    conn = initSQLite(csvFilename)
    writeSQLiteListFromVietnamnetThen(conn, sbdStart, sbdEnd)
    conn.close()


if __name__ == "__main__":
    main()
