"""
The MIT License (MIT)

Copyright (c) 2016 Texas Department of Transportation
Author: Jason Kleinert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import math
import csv
import os
import sys

import arcpy
from arcpy import env
from geopy.distance import vincenty
from decimal import Decimal
import time


def print_hamster_slow():
    hamst = """
             (`-`;-"```"-;`-`)
              \.'         './
              [             ]
              ;   0     0   ;
             (( =         = ))
            ; \   '._Y_.'   / ;
           ;   `-._ \|/ _.-'   ;
          ;        `'"'`        ;
          ;    `""-.   .-""`    ;
          (;  '--._ \ / _.--   ;)
         (  `.   `/|| ||\`   .'  )
          '.  '-._       _.-'   .'
          (((-'`   `````    `'-)))
         welcome to curves hamster!\n
         """
    for l in hamst:
        sys.stdout.write(l)
        sys.stdout.flush()
        time.sleep(0.01)

def hamster_reveal():
    print """
             (`-`;-"```"-;`-`)
              \.'         './
              [             ]
              ;   0     0   ;
             (( =         = ))
            ; \   '._Y_.'   / ;
           ;   `-._ \|/ _.-'   ;
          ;        `'"'`        ;
          ;    `""-.   .-""`    ;
          (;  '--._ \ / _.--   ;)
         (  `.   `/|| ||\`   .'  )
          '.  '-._       _.-'   .'
          (((-'`   `````    `'-)))
         welcome to curves hamster!\n
         """

def unprojectify(in_proj_features):
    """
    Cast the input features to WGS84
    """
    print "Unprojectifying..."
    wgs84 = arcpy.SpatialReference(4326)
    projected_output = os.path.join(in_proj_features + "_projected")
    return arcpy.Project_management(in_proj_features, projected_output, wgs84,
                                    preserve_shape="PRESERVE_SHAPE")


def simplify_then_densify(input_features):
    """
    Simplify and densify the input features to normalize them for processing
    """
    if str(input_features).endswith("_projected"):
        processed_output = str(input_features).rstrip("_projected") + "_processed"
    else:
        processed_output = input_features + "_processed"
    print "Simplifying..."
    arcpy.SimplifyLine_cartography(input_features, processed_output, "BEND_SIMPLIFY",
                                   "100 Feet", collapsed_point_option="NO_KEEP")
    print "Densifying..."
    return arcpy.Densify_edit(processed_output, "Distance", "100 Feet")


def part_count(feat):
    """
    Check for multipart features
    """
    if feat.isMultipart:
        return 'Yes'
    else:
        return 'No'


def bearing(lat1, lon1, lat2, lon2):
    """
    Calculate bearing from coordinate pairs
    """
    dlon = abs(lon1 - lon2)
    # dLat = abs(lat1 - lat2)
    brng_y = math.sin(dlon) * math.cos(lat2)
    brng_x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    brng = math.atan2(brng_y, brng_x)
    brng_deg = math.degrees(brng)
    return brng_deg


def vincenty_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the vincenty distance between two points
    on the earth
    """
    vertex_1 = (lat1, lon1)
    vertex_2 = (lat2, lon2)
    return vincenty(vertex_1, vertex_2).miles


def curve_classifier(angle):
    """
    Check the assigned angle and determine the appropriate curve class
    """
    if angle < 3.5:
        return 'A'
    elif 3.5 < angle < 5.5:
        return 'B'
    elif 5.5 < angle < 8.5:
        return 'C'
    elif 8.5 < angle < 14.0:
        return 'D'
    elif 14.0 < angle < 28:
        return 'E'
    elif angle > 28:
        return 'F'


def hpms_class_buckets(hpms_linestring, output_file):
    """
    Organize the curves into "buckets" based on the total segment length and curve class
    """
    curve_class_dict = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'Unclassified': 0}
    total_measured_length = 0
    point_count = 0
    for i in hpms_linestring:
        point_count += 1
        if i['Curve_Class'] is not None:
            curve_class_assignment = i['Curve_Class']
            curve_length = i['Measured_Distance']
            curve_class_dict[curve_class_assignment] += curve_length
        else:
            curve_length = i['Measured_Distance']
            curve_class_dict['Unclassified'] += curve_length
        if point_count == 1:
            rte_id = i['Rte_ID']
            objectid = i['OBJECTID']
            from_dfo = "{0:.3f}".format(i['M'])
        elif point_count == len(hpms_linestring):
            to_dfo = "{0:.3f}".format(i['M'])
        total_measured_length += curve_length
    if curve_class_dict['Unclassified'] > 0:
        unclassified_length = curve_class_dict['Unclassified']
        key_list = curve_class_dict.keys()
        key_list.remove('Unclassified')
        for key in key_list:
            unclassified_proportion = curve_class_dict[key] / total_measured_length
            curve_class_dict[key] += (unclassified_length * unclassified_proportion)
            curve_class_dict['Unclassified'] -= (unclassified_length * unclassified_proportion)

    write_curve_event(output_file, objectid, rte_id, from_dfo, to_dfo, curve_class_dict)


def write_curve_event(output_file, objectid, route_id, from_m, to_m, curve_class_dict):
    """
    Write the curve records to an output csv file
    """
    spamWriter = csv.DictWriter(open(output_file, 'ab'), ['OBJECTID', 'RTE_ID', 'FROM_DFO', 'TO_DFO',
                                                          'CURVES_A', 'CURVES_B', 'CURVES_C', 'CURVES_D',
                                                          'CURVES_E', 'CURVES_F'])
    row = {}
    row['OBJECTID'] = objectid
    row['RTE_ID'] = route_id
    row['FROM_DFO'] = from_m
    row['TO_DFO'] = to_m
    row['CURVES_A'] = "{0:.3f}".format(curve_class_dict['A'], 3)
    row['CURVES_B'] = "{0:.3f}".format(curve_class_dict['B'], 3)
    row['CURVES_C'] = "{0:.3f}".format(curve_class_dict['C'], 3)
    row['CURVES_D'] = "{0:.3f}".format(curve_class_dict['D'], 3)
    row['CURVES_E'] = "{0:.3f}".format(curve_class_dict['E'], 3)
    row['CURVES_F'] = "{0:.3f}".format(curve_class_dict['F'], 3)

    print row
    spamWriter.writerow(row)


def fix_curve_buckets(curve_csv):
    """
    Remove small gaps and overlaps from the original output file
    that may be created by the machine during processing
    """
    output_file = os.path.join(os.path.dirname(curve_csv),
                               os.path.basename(curve_csv).split(".")[0] + "_cleaned.csv")
    with open(curve_csv, 'rb') as read_csv:
        spamreader = csv.DictReader(read_csv)
        with open(output_file, 'wb') as write_csv:
            spamwriter = csv.DictWriter(write_csv, spamreader.fieldnames)
            spamwriter.writeheader()
            for row in spamreader:
                sample_len = Decimal(row['TO_DFO']) - Decimal(row['FROM_DFO'])
                curve_values = [Decimal(row[col]) for col in row.keys() if col.startswith("CURVES_")]
                curves_total = sum(curve_values)
                if sample_len == curves_total:
                    pass
                else:
                    diff = sample_len - curves_total
                    curves_array = [(k, Decimal(v)) for k, v in row.iteritems() if
                                    k.startswith("CURVES_") and Decimal(v) != 0]
                    curves_array.sort(key=lambda tup: tup[1], reverse=True)
                    if diff != 0:
                        row[curves_array[0][0]] = Decimal(row[curves_array[0][0]]) + Decimal(diff)
                spamwriter.writerow(row)


def get_curvy(linework, id_fieldname):
    start_time = time.time()
    print "Start Time: {0}".format(time.ctime(start_time))

    # hamster_reveal()
    print_hamster_slow()

    # Set ESRI geodatabase environment variables
    env.workspace = os.path.dirname(linework)
    env.overwriteOutput = True

    # Get the name of the linework feature class from the input path
    original_linework = os.path.basename(linework)

    print "Feature class properties"

    # Check the geometry for m-values
    if not arcpy.Describe(original_linework).hasM:
        sys.exit("The geometry must contain m-values!")
    else:
        print "m-value enabled: True"

    # Get the coordinate system type and name
    coord_type = str(arcpy.Describe(original_linework).spatialReference.type)
    coord_name = str(arcpy.Describe(original_linework).spatialReference.name)
    print "coordinate system type: " + coord_type
    print "coordinate system: " + coord_name

    print "\nBegin process"
    # Cast to gcs if necessary, simplify, then densify
    if coord_type != "Geographic":
        projected_linework = str(unprojectify(original_linework))
        processed_linework = str(simplify_then_densify(projected_linework))
        arcpy.Delete_management(projected_linework)
    else:
        processed_linework = str(simplify_then_densify(original_linework))

    # Create the output csv files
    output_file = os.path.join(os.path.split(os.path.dirname(linework))[0], original_linework + "_Curves.csv")
    output_log = os.path.join(os.path.split(os.path.dirname(linework))[0], original_linework + "_Curves_log.csv")
    if os.path.isfile(output_file):
        os.remove(output_file)
    if os.path.isfile(output_log):
        os.remove(output_log)

    # Write headers into the output csv files
    with open(output_file, 'ab') as csvfile_header:
        spamwriter = csv.writer(csvfile_header)
        spamwriter.writerow(['OBJECTID', 'RTE_ID', 'FROM_DFO', 'TO_DFO', 'CURVES_A', 'CURVES_B', 'CURVES_C',
                             'CURVES_D', 'CURVES_E', 'CURVES_F'])
    with open(output_log, 'ab') as csvlog_header:
        spamwriter_log = csv.writer(csvlog_header)
        spamwriter_log.writerow(['OBJECTID', 'Rte_ID', 'point_ID', 'X', 'Y', 'M', 'Bearing', 'Distance',
                                 'Measured_Distance', 'Deflection', 'Curve_Class'])

    # Create in_memory copy of the linework for quicker processing, I think
    in_memory_linework = arcpy.CopyFeatures_management(
            processed_linework, os.path.join("in_memory",
                                             os.path.basename(processed_linework) + "_inMemory"))

    # Begin process
    print "\nCalculating curve class..."
    counter = 0
    for row in arcpy.da.SearchCursor(in_memory_linework, ["OID@", "SHAPE@", id_fieldname]):
        counter += 1
        print counter
        objectid = str(row[0])
        feat = row[1]
        rte_id = str(row[2])
        num_vertices = feat.pointCount
        line_string = []
        pnt_count = 0
        partnum = 0
        spamWriter_log = csv.DictWriter(open(output_log, 'ab'), ['OBJECTID', 'Rte_ID', 'point_ID', 'X', 'Y', 'M',
                                                                 'Bearing', 'Distance', 'Measured_Distance',
                                                                 'Deflection', 'Curve_Class'])
        for part in feat:
            for pnt in feat.getPart(partnum):
                if pnt:
                    pnt_count += 1
                    pnt_id = "Point_{0}".format(pnt_count)
                    if pnt_count > 1:
                        # Bearing Calculation
                        brng = bearing(previous_y, previous_x, pnt.Y, pnt.X)
                        # distance = vincenty_distance(pnt.Y, pnt.X, previous_y, previous_x)
                        distance = 0
                        measured_distance = abs(pnt.M - previous_m)
                        if pnt_count == 2:
                            # This is the second vertex, this segment is automatically class A
                            deflection = 0
                            curve_class = 'A'
                        elif pnt_count > 2:
                            # There may be a change in bearing, so let's check for it
                            deflection = abs(brng - previous_brng)
                            curve_class = curve_classifier(deflection)
                        elif pnt_count == 2 and num_vertices == 2:
                            # If the sample has only two vertices, it is automatically class A
                            deflection = 0
                            curve_class = 'A'
                    else:
                        # This is the first vertex
                        deflection = None
                        brng = None
                        distance = 0
                        measured_distance = 0
                        curve_class = None
                point_dict = {'OBJECTID': objectid, 'Rte_ID': rte_id,
                              'point_ID': pnt_id, 'X': pnt.X, 'Y': pnt.Y,
                              'M': pnt.M, 'Bearing': brng, 'Distance': distance,
                              'Measured_Distance': measured_distance,
                              'Deflection': deflection, 'Curve_Class': curve_class}
                spamWriter_log.writerow(point_dict)
                previous_brng = brng
                previous_x = pnt.X
                previous_y = pnt.Y
                previous_m = pnt.M
                line_string.append(point_dict)
            partnum += 1
        hpms_class_buckets(line_string, output_file)
    fix_curve_buckets(output_file)
    arcpy.Delete_management("in_memory")

    stop_time = time.time()
    print "\nStop Time: {0}".format(time.ctime(stop_time))
    run_time = round((stop_time - start_time)/60, 2)
    print "Run Time: {0} {1}".format(run_time, "minutes")

if __name__ == '__main__':
    get_curvy("C:\\_HPMS\\2015\\____HPMS_Curves2014\\Samples_2014.gdb\\Samples_2013_100recs_tsms", "OBJECTID")
    # features_path = raw_input("Features path :")
    # id_field = raw_input("ID field: ")
    # get_curvy(features_path, id_field)