import csv

# lst = {}
# with open('eggs.csv', 'r') as csvfile:
#     reader = csv.reader(csvfile)
#     for row in reader:
#         lst[row[0]] = eval(row[1])


# print(lst)

with open('eggs.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
    spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])