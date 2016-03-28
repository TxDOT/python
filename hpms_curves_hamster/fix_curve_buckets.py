# -*- coding: utf-8 -*-
"""

The MIT License (MIT)

Copyright (c) 2014 Texas Department of Transportation

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

import os
import csv
from decimal import Decimal

def fix_curve_buckets(curve_csv):
    output_file = os.path.join(os.path.dirname(curve_csv), os.path.basename(curve_csv).split(".")[0] + "_cleaned.csv")
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
                    curves_array = [(k, Decimal(v)) for k, v in row.iteritems() if k.startswith("CURVES_")
                                    and Decimal(v) != 0]
                    curves_array.sort(key=lambda tup: tup[1], reverse=True)
                    if diff <> 0:
                        row[curves_array[0][0]] = Decimal(row[curves_array[0][0]]) + Decimal(diff)
                spamwriter.writerow(row)




if __name__ == '__main__':
    fix_curve_buckets("C:\\____HPMS_Curves2014\\Samples_2014_Final_Routes_Attr_Processed_Curves.csv")