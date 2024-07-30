import mongo_setup

def entry_point(request):
    mongo_setup.main()
    return 'Function executed successfully', 200

if __name__ == "__main__":
    mongo_setup.main()
