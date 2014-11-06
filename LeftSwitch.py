__author__ = 'DHICKMA'


import arcpy

table = "C:\\_GRID\\__V15\\V15_Final\\V15_FinalDatasets.gdb\\BAXYCRFCFDRSTLMP_ROADWAY_SUMMARY"
rows = arcpy.UpdateCursor(table)

for row in rows:
    if str(row.RTE_ORDER_ID).count("-") < 2:
        pass
    elif str(row.RTE_ORDER_ID).split("-")[1] not in ['LG', 'MG', 'XG', 'PG', 'YG']:
        pass
    else:
        road_from = row.ROADWAYS_FROM
        road_to = row.ROADWAYS_TO

        road_cal_from = row.ROADWAYS_CALIBRATE_FROM
        road_cal_to = row.ROADWAYS_CALIBRATE_TO

        rhino_from = row.RHINO_FROM
        rhino_to = row.RHINO_TO

        rhino_cal_from = row.RHINO_CALIBRATE_FROM
        rhino_cal_to = row.RHINO_CALIBRATE_TO

        if road_from > road_to:
            to = road_from
            frm = road_to
            row.ROADWAYS_TO = to
            row.ROADWAYS_FROM = frm

        if road_cal_from < road_cal_to:
            to = road_cal_from
            frm = road_cal_to
            row.ROADWAYS_CALIBRATE_TO = to
            row.ROADWAYS_CALIBRATE_FROM = frm
        
        if rhino_from > rhino_to:
            to = rhino_from
            frm = rhino_to
            row.RHINO_TO = to
            row.RHINO_FROM = frm

        if rhino_cal_from < rhino_cal_to:
            to = rhino_cal_from
            frm = rhino_cal_to
            row.RHINO_CALIBRATE_TO = to
            row.RHINO_CALIBRATE_FROM = frm
    rows.updateRow(row)