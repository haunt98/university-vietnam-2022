import argparse
import sqlite3

# Khoi B = toan + hoa + sinh

# Copy from main.py
gddtsName = {
    1: "ha_noi",
    2: "hcm",
    3: "hai_phong",
    4: "da_nang",
    32: "quang_tri",
    33: "hue",
    34: "quang_nam",
    35: "quang_ngai",
    36: "kon_tum",
    37: "binh_dinh",
    38: "gia_lai",
    39: "phu_yen",
    40: "dak_lak",
    41: "khanh_hoa",
    42: "lam_dong",
    43: "binh_phuoc",
    44: "binh_duong",
    45: "ninh_thuan",
    46: "tay_ninh",
    47: "binh_thuan",
    48: "dong_nai",
    49: "long_an",
    50: "dong_thap",
    51: "an_giang",
    52: "vung_tau",
    53: "tien_giang",
    54: "kien_giang",
    55: "can_tho",
    56: "ben_tre",
    57: "vinh_long",
    58: "tra_vinh",
    59: "soc_trang",
    60: "bac_lieu",
    61: "ca_mau",
    63: "dak_nong",
    64: "hau_giang",
}

gddtsMienNam = {
    2,
    4,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    63,
    64,
}

gddtsDiemKhuVuc = {
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    32: 0.25,
    33: 0.25,
    34: 0.25,
    35: 0.25,
    36: 0.75,
    37: 0.25,
    38: 0.75,
    39: 0.25,
    40: 0.75,
    41: 0.25,
    42: 0.75,
    43: 0.5,
    44: 0.25,
    45: 0.25,
    46: 0.25,
    47: 0.25,
    48: 0.25,
    49: 0.25,
    50: 0.25,
    51: 0.25,
    52: 0.25,
    53: 0.25,
    54: 0.25,
    55: 0,
    56: 0.25,
    57: 0.25,
    58: 0.25,
    59: 0.5,
    60: 0.25,
    61: 0.25,
    63: 0.75,
    64: 0.25,
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

    totalRow = cur.execute(
        """SELECT COUNT(*) FROM university_vietnam_2022"""
    ).fetchone()
    if not totalRow or len(totalRow) != 1:
        print("WARNING: failed to count total", gddt)
        return False, 0, 0
    # print("totalRow", totalRow)

    equalOrGreaterRow = cur.execute(
        """SELECT COUNT(*) FROM university_vietnam_2022 WHERE (toan + hoa + sinh) >= ?""",
        (sumPoint,),
    ).fetchone()
    if not equalOrGreaterRow or len(equalOrGreaterRow) != 1:
        print("WARNING: failed to count", gddt)
        return False, 0, 0
    # print("equalOrGreaterRow", equalOrGreaterRow)

    conn.close()
    return True, int(totalRow[0]), int(equalOrGreaterRow[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sbd", type=int, help="So bao danh")

    args = parser.parse_args()
    print("sbd", args.sbd)

    exist, sumPoint = getSumPoint(args.sbd)
    if not exist:
        return
    print("sumPoint", sumPoint)

    print(
        "gddt",
        "gddt_name",
        "equal_or_greater_count",
    )
    sumEqualOrGreaterCount = 0
    for gddt in gddtsMienNam:
        exist, totalCount, equalOrGreaterCount = countEqualOrGreaterWithSQLite(
            gddt, sumPoint
        )
        if not exist:
            continue

        sumEqualOrGreaterCount += equalOrGreaterCount
        print(
            gddt,
            gddtsName[gddt],
            equalOrGreaterCount,
        )
    print("all", sumEqualOrGreaterCount)
    print("---")

    # Diem cong vung mien
    print("XXX", args.sbd % 1000000)
    sumPointVungMien = sumPoint + gddtsDiemKhuVuc.get(args.sbd // 1000000, 0)
    print("sumPointVungMien", sumPointVungMien)

    print(
        "gddt",
        "gddt_name",
        "cong_vung_mien",
        "equal_or_greater_count",
    )
    sumEqualOrGreaterCount = 0
    for gddt in gddtsName:
        vungMienOfGDDT = gddtsDiemKhuVuc.get(gddt, 0)

        exist, totalCount, equalOrGreaterCount = countEqualOrGreaterWithSQLite(
            gddt, sumPointVungMien - vungMienOfGDDT
        )
        if not exist:
            continue

        sumEqualOrGreaterCount += equalOrGreaterCount
        print(
            gddt,
            gddtsName[gddt],
            vungMienOfGDDT,
            equalOrGreaterCount,
        )
    print("all", sumEqualOrGreaterCount)


if __name__ == "__main__":
    main()
