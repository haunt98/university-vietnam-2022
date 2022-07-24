import argparse
import sqlite3

# Khoi B = toan + hoa + sinh

# Copy from main.py
gddts = [
    2,
    4,
    33,
    37,
    38,
    39,
    41,
    43,
    44,
    47,
    48,
    51,
    52,
    55,
    64,
]

# Copy from main.py
def convertSBDToStr(sbd):
    sbdStr = str(sbd)
    if len(sbdStr) == 7:
        sbdStr = "0" + sbdStr

    return sbdStr


def getSumPoint(sbd):
    sbdStr = convertSBDToStr(sbd)
    gddt = sbdStr[:2]

    conn = sqlite3.connect(gddt + ".sqlite3")
    cur = conn.cursor()

    row = cur.execute(
        """SELECT sbd, (toan + hoa + sinh) FROM university_vietnam_2022 WHERE sbd = ?""",
        (sbd,),
    ).fetchone()
    if not row:
        print("WARNING: not found sbd", sbd)
        return False, 0

    if str(row[0]) != sbdStr:
        print("WARNING: sbd not match", sbd, row[0])
        return False, 0
    # print(row)

    conn.close()
    return True, float(row[1])


# Return gddt, count
def countEqualOrGreaterWithSQLite(gddt, sumPoint):
    conn = sqlite3.connect(str(gddt) + ".sqlite3")
    cur = conn.cursor()

    row = cur.execute(
        """SELECT COUNT(*) FROM university_vietnam_2022 WHERE (toan + hoa + sinh) >= ?""",
        (sumPoint,),
    ).fetchone()
    if not row or len(row) != 1:
        print("WARNING: failed to count", gddt)
        return False, 0

    conn.close()
    return True, int(row[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sbd", type=int, help="So bao danh")

    args = parser.parse_args()
    print("sbd", args.sbd)

    exist, sumPoint = getSumPoint(args.sbd)
    if not exist:
        return
    print(sumPoint)

    totalCount = 0
    for gddt in gddts:
        exist, count = countEqualOrGreaterWithSQLite(gddt, sumPoint)
        if not exist:
            continue
        totalCount += count
        print(gddt, count)
    print("all", totalCount)


if __name__ == "__main__":
    main()
