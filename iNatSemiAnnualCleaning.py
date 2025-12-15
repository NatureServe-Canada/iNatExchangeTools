import io
import csv

#encoding = 'mbcs' # mbcs encoding is Windows ANSI, which is the default for param_data_file_encoding
encoding = 'utf8'
infile = io.open("D:\\GIS\\iNatExchange\\Input\\inaturalist-canada-5\\inaturalist-canada-5-observations.csv", 'r', encoding=encoding)
outfile = io.open("D:\\GIS\\iNatExchange\\Input\\inaturalist-canada-5\\inaturalist-canada-5-observations-nopriv-first10.csv", 'w', encoding=encoding, newline='')
#outfile = io.open("D:\\GIS\\iNatExchange\\Input\\inaturalist-canada-5\\inaturalist-canada-5-observations-nopriv.csv", 'w', encoding=encoding, newline='')
reader = csv.DictReader(infile)
writer = csv.DictWriter(outfile, reader.fieldnames)
writer.writeheader()

count = 0
skipped = 0
for file_line in reader:
    count += 1
    if count % 10000 == 0:
        print('Processing ' + str(count))
    if file_line['geoprivacy'] == 'private':
        skipped += 1
        if skipped % 100 == 0:
            print('Skipped ' + str(skipped))
    else:
        writer.writerow(file_line)
    if count == 10:
        break

print('Processed ' + str(count))
print('Skipped ' + str(skipped))
outfile.close()
infile.close()
