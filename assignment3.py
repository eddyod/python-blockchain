def transform_data(fn, *args):
    for arg in args:
        print(fn(arg))

transform_data(lambda x: x * 1,2,3,4,5)
