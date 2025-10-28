from checkPlate import check_plate

plate_number = input("Enter plate number: ")
results, data = check_plate(plate_number)
print("\nTo na yung sa test.py")

# print buong text result
# for line in results:
#     print(line)

# print yung values lang
values = list(data.values())
for value in values:
    print(value)

# Alternatively, you can do it in one line:
# values = [value for value in data.values()]