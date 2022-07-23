import requests
from bs4 import BeautifulSoup
import argparse

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
gddtDaNang = 4
gddtBinhdinh = 37
gddtPhuYen = 39
gddtVungTau = 52
sbdEnds = {
    gddtDaNang: 4013000,
    # gddtDaNang: 4000010,
    gddtBinhdinh: 37019000,
    gddtPhuYen: 39011000,
    gddtVungTau: 52013000,
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
        print(singleResult)
        results.append(singleResult)

    return results


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gddt", type=int, help="Ma so gddt")

    args = parser.parse_args()
    print(args.gddt)

    sbdStart, sbdEndMax = generateSBD(args.gddt)
    sbdEnd = sbdEnds.get(args.gddt, sbdEndMax)
    print(
        "sbdStart",
        sbdStart,
        "sbdEnd",
        sbdEnd,
    )

    results = getListFromVietnamnet(sbdStart, sbdEnd)
    writeCSVVietnamnet(str(args.gddt) + ".csv", results)


if __name__ == "__main__":
    main()
