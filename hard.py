# Libraries used

import json
from operator import contains
from posixpath import split
import re
from pyparsing import nestedExpr

#--------------------------------------------------------------------------------------------

# Determines if this string is a course code
# Returns a bool
def is_course_code(word):
    # Try and match 4 letters followed by
    # 1 number between 1-9 (since course code can't be level 0) and then 
    # 3 more numbers
    p = re.compile(r"[A-Z]{4}[1-9][0-9]{3}")
    return len(word) == 8 and bool(p.match(word))

# Determines if this string is a faculty code
# Returns a bool
def is_faculty_code(word):
    # Try and match 4 letters
    p = re.compile(r"[A-Z]{4}")
    return len(word) == 4 and bool(p.match(word))

# Janky workaround for the requirement to COMP4952/4953, since the course
# code doesn't have the faculty name with it
def is_bad_course_code(word):
    p = re.compile(r"[1-9][0-9]{3}")
    return len(word) == 4 and bool(p.match(word))

# Decide if we want to prune this word from the condition list
def wanted_word(word):
    if word == 'OR' or word == 'AND':
        # It's a condition, keep it
        return True
    elif is_course_code(word):
        # It's a course code, keep it
        return True
    elif word.isdigit() or word == 'UNITS' or word == 'LEVEL' or is_faculty_code(word):
        # It's needed for a UOC requirement, keep it
        return True
    else:
        # Don't want it
        return False

# Cleans the word list by making everything uppercase, pruning
# unwanted words and fixing bad course codes
def clean_word_list(word_list):
    # Is there a better way of doing this without a gross double loop?
    # Problem is, I'm modifying this list within the loop and would
    # have issues if I just got rid of the outermost while loop?
    # Probably a better way... Had to do this same grossness later on as well
    clean = False
    while not clean:
        clean = True
        for i, item in enumerate(word_list):
            if type(item) is str:
                # It's a string, clean it up.
                # For each word, only keep alphanumeric characters
                word_list[i] = ''.join(filter(str.isalnum, word_list[i]))
                word_list[i] = word_list[i].upper()

                # If it's just a course code written badly, ie without the
                # faculty at the start like COMP or MATH, assume they meant
                # to put COMP
                if is_bad_course_code(word_list[i]):
                    word_list[i] = 'COMP' + word_list[i]

                # If it's the word prerequisite then remove it and skip
                if not wanted_word(word_list[i]):
                    # Remove the item if it's prereq
                    word_list = word_list[:i] + word_list[i + 1:]
                    clean = False
                    break
            else:
                # It's a list, go deeper
                word_list[i] = clean_word_list(item)
    
    return word_list

# Takes in a target course, gets the conditions in conditions.json,
# deconstructs it into individual words and returns a cleaned
# list of words. If brackets are present, the returned list will
# represent this by having another list in it. See examples below for
# more details about the brackets
def get_target_conditions(target):
    with open("./conditions.json") as f:
        all_conditions = json.load(f)

        # Get the target string and add brackets around it
        # so we can use a library in a moment
        target_condition = f"({all_conditions[target]})"
        f.close()
    
    # Use library function to split it up based on brackets
    # This line is gross and unreadable. Basically it's using this library function
    # to deconstruct the brackets and remove whitespace.
    # For example, target_condition = '(COMP1511    or DPST1091 or COMP1911 or COMP1917)',
    # target_as_words = ['COMP1511', 'or', 'DPST1091', 'or', 'COMP1911', 'or', 'COMP1917'].

    # More complicated example with brackets, target_condition = (MATH1081 and ((COMP1531 or COMP2041) or (COMP1927 or COMP2521)))
    # target_as_words = ['MATH1081', 'and', [['COMP1531', 'or', 'COMP2041'], 'or', ['COMP1927', 'or', 'COMP2521']]]
    target_condition_words = nestedExpr('(',')').parseString(target_condition).asList()[0]

    # Clean it up and return this list
    return clean_word_list(target_condition_words)

# Takes in a list of requirements and returns
# the first faculty name it finds.
# If no faculty is found, None is returned
def find_first_faculty(requirements):
    for requirement in requirements:
        if type(requirement) is str and is_faculty_code(requirement):
            return requirement

    return None

# Takes in a list and returns True
# if this list contains another list
def contains_list(requirements):
    for requirement in requirements:
        if type(requirement) is list:
            return True

def is_uoc_satisfied(courses_done, requirement):
    # There are 4 cases
    # - Simple min UOC requirement, e.g. ['102', 'UNITS']
    # - Min UOC requirement in faculty e.g. ['36', 'UNITS', 'COMP']
    # - Min UOC requirement in faculty with level x, e.g. ['18', 'UNITS', 'LEVEL', '2', 'COMP']
    # - Min UOC requirement from a list of courses, e.g. ['12', 'UNITS', ['COMP6443', 'COMP6843', 'COMP6445', 'COMP6845', 'COMP6447']]

    # First thing will always be a number of UOC
    try:
        uoc_required = int(requirement[0])
    except:
        print('Something went wrong, assume uoc_required is 0 as a bad fix')
        uoc_required = 0

    # Check what case it's in
    faculty = find_first_faculty(requirement)    
    uoc_done = 0
    if len(requirement) == 2:
        # Simple min UOC requirement, e.g. ['102', 'UNITS']
        uoc_done = 6 * len(courses_done)
    elif faculty != None:
        # Min UOC requirement in faculty e.g. ['36', 'UNITS', 'COMP']
        for course_done in courses_done:
            if course_done[:4] == faculty:
                uoc_done += 6
    elif faculty != None and requirement.contains('LEVEL'):
        # Min UOC requirement in faculty with level x, e.g. ['18', 'UNITS', 'LEVEL', '2', 'COMP']
        level_index = requirement.index('LEVEL')
        
        # Assume the item after the word level is the level number we want
        level_needed = int(requirement[level_index + 1])
        for course_done in courses_done:
            if course_done[:4] == faculty and int(course_done[4]) == level_needed:
                uoc_done += 6
    elif contains_list(requirement):
        # Min UOC requirement from a list of courses, e.g. ['12', 'UNITS', ['COMP6443', 'COMP6843', 'COMP6445', 'COMP6845', 'COMP6447']]
        possible_courses = requirement[-1]
        for course in possible_courses:
            if course in courses_done:
                uoc_done += 6
    else:
        # Something went wrong ;_;
        # For now, I've just made it print something but would probably raise some kind of
        # exception handling if this was a real project
        print(f"Something went wrong with requirement = {requirement}")
    
    return uoc_done >= uoc_required

def satisfies_requirements(courses_done, requirements):    
    if len(requirements) == 0:
        return True
    
    everything_checked = False
    while not everything_checked:
        everything_checked = True
        for i, item in enumerate(requirements):
            if type(item) is str:
                if item == 'OR' or item == 'AND':
                    # Don't need to do anything to these for now
                    continue
                elif is_course_code(item):
                    # Decide whether this item should be True or False.
                    # True -> student has done this course.
                    # False -> student hasn't done this course.
                    requirements[i] = (item in courses_done)
                else:
                    # Must be some UOC requirement.
                    # First thing is always the number of UOC, at least in examples given
                    #uoc_required = int(item)

                    # Need to figure out how long this UOC requirement is
                    lo = i
                    hi = lo
                    while hi + 1 < len(requirements) and requirements[hi + 1] != 'OR' and requirements[hi + 1] != 'AND':
                        hi += 1
                    
                    # Isolate just the UOC requirement bit to simplify
                    uoc_requirement = requirements[lo:hi + 1]

                    # Figure out if this should be True or False
                    requirements[hi] = is_uoc_satisfied(courses_done, uoc_requirement)

                    # Get rid of the wacky bits and break so that the enumeration doesn't break
                    requirements = requirements[:lo] + requirements[hi:]
                    everything_checked = False
                    break
            elif type(item) is bool:
                # Do nothing
                continue
            else:
                # It's a list, go deeper
                requirements[i] = satisfies_requirements(courses_done, item)
    
    # Once we've gone through the entire list, decide if everything is satisfied or not
    is_satisfied = requirements[0]
    for i in range(0, len(requirements)):
        if i % 2 == 0:
            continue
        
        # requirements[i] is either 'AND' or 'OR' since I'm only taking i to be odd
        if requirements[i] == 'AND':
            # Do an and with the next item
            is_satisfied = is_satisfied and requirements[i + 1]
        elif requirements[i] == 'OR':
            # Do an or with the next item
            is_satisfied = is_satisfied or requirements[i + 1]
        else:
            print(f"There is a problem. This item is {requirements[i]} i is {i}")
    
    return is_satisfied

"""
Given a list of course codes a student has taken, return true if the target_course 
can be unlocked by them.

You do not have to do any error checking on the inputs and can assume that
the target_course always exists inside conditions.json

You can assume all courses are worth 6 units of credit
"""
def is_unlocked(courses_list, target_course):
    conditions = get_target_conditions(target_course)    

    # Go through and check if we've satisfied each part.
    # If we are, replace it with True. If not, replace it with False.
    # This is recursive by the nature that I've set it up
    return satisfies_requirements(courses_list, conditions)

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':
    with open("./conditions.json") as f:
        all_conditions = json.load(f)

        for key in all_conditions.keys():
            print(f"{key}: {is_unlocked(['MATH1081'], key)}")
        f.close()
