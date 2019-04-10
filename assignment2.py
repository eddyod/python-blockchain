# 1) Create a list of “person” dictionaries with a name, age and list of hobbies for each person. Fill in any data you want.
persons = [{'name': 'Ann', 'age': 42, 'hobbies': ['eating', 'tv']},
                {'name': 'Edward', 'age': 58, 'hobbies': ['eating', 'drinking']}]

# 2) Use a list comprehension to convert this list of persons into a list of names (of the persons).
lp = [dict['name'] for dict in persons]
# 3) Use a list comprehension to check whether all persons are older than 20.
la = all([dict['age'] > 20 for dict in persons])
# 4) Copy the person list such that you can safely edit the name of the first person (without changing the original list).
# copied_persons = persons[:]
persons_copy = [dict.copy() for dict in persons]
print(persons)
persons_copy[0]['name'] = 'Gertruda'
print(persons)
print(persons_copy)
# 5) Unpack the persons of the original list into different variables and output these variables.
ann, eddy = persons
for k, v in ann.items():
    print(k, v)
