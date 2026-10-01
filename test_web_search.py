from web_search import web_search

query = input("Enter search topic: ")

result = web_search(query)

print("\n==============================")
print("WEB SEARCH RESULTS")
print("==============================")

print(result)