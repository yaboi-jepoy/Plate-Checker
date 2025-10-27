from checkPlate import check_plate

# Get both text results and structured data
results, data = check_plate("NDJ8975")

# Print the formatted results
for line in results:
    print(line)
    
for content in data:
    print(content{1})

# # Use the structured data
# print(f"This vehicle was released to: {data['released_to']}")
# print(f"Release date: {data['date_released']}")

# # Or use the old way (just gets text results)
# from checkPlate import checkPlate
# results = checkPlate("NDJ8975")