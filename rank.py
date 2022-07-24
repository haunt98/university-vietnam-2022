import argparse
import sqlite3

# Khoi B = toan + hoa + sinh

# Copy from main.py
gddts = {
    2: "hcm",
    4: "da_nang",
    33: "hue",
    37: "binh_dinh",
    38: "gia_lai",
    39: "phu_yen",
    41: "khanh_hoa",
    43: "lam_dong",
    44: "binh_phuoc",
    47: "binh_duong",
    48: "dong_nai",
    51: "an_giang",
    52: "vung_tau",
    55: "can_tho",
    57: "vinh_long",
    58: "tra_vinh",
    59: "soc_trang",
    60: "bac_lieu",
    61: "ca_mau",
    63: "dak_nong",
    64: "hau_giang",
}

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
    print("sumPoint", sumPoint)

    totalCount = 0
    for gddt in gddts:
        exist, count = countEqualOrGreaterWithSQLite(gddt, sumPoint)
        if not exist:
            continue
        totalCount += count
        print(gddt, gddts[gddt], count)
    print("all", totalCount)


if __name__ == "__main__":
    main()
