"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge. 
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""
import json
from posixpath import split
import re

#--------------------------------------------------------------------------------------------

def is_course_code(string):
    # Try and match 4 letters followed by
    # 1 number between 1-9 (since course code can't be level 0) and then 
    # 3 more numbers
    p = re.compile(r"[A-Z]{4}[1-9][0-9]{3}")
    return len(string) == 8 and bool(p.match(string))

def is_faculty_code(string):
    # Try and match 4 letters
    p = re.compile(r"[A-Z]{4}")
    return len(string) == 4 and bool(p.match(string))

def is_bad_course_code(string):
    # Just figure out if it's meant to be a course code.
    # What I mean by this is '4951' and '4952' are
    # just written as numbers without the COMP bit

    # How to do this properly??
    p = re.compile(r"[1-9][0-9]{3}")
    return len(string) == 4 and bool(p.match(string))

def is_and(string):
    return string == 'AND'

def is_or(string):
    return string == 'OR'

def is_prereq(string):
    # Just checks that the start of the string
    # is 'PREREQ'
    return string.find('PRE') == 0

def string_to_words(string):
    # Split the string into words
    words = string.split(' ')

    # For each word, only keep alphanumeric characters
    for i in range(len(words)):
        words[i] = ''.join(filter(str.isalnum, words[i]))
        words[i] = words[i].upper()

    # Filter out the empty words caused by multiple spaces in the original string
    words = list(filter(lambda word: word != '', words))
    
    return words

def get_target_conditions(target):
    with open("./conditions.json") as f:
        all_string_conditions = json.load(f)
        target_string_conditions = all_string_conditions[target]
        f.close()

    return string_to_words(target_string_conditions)

def has_uoc_condition(conditions):
    return 'UNITS' in conditions and ('OF' in conditions or 'OC' in conditions) and 'CREDIT' in conditions

def split_on_ands(list):
    split_list = []

    while list.count('AND') != 0:
        index = list.index('AND')
        if list[:index] != []:
            split_list.append(list[:index])
        list = list[index + 1:]
    split_list.append(list)

    return split_list

def are_all_course_codes(list):
    for item in list:
        if not is_course_code(item):
            return False
    
    return True

def find_first_faculty(list):
    for item in list:
        if is_faculty_code(item):
            return item

# Problem courses:
# 2121
# 3151
# 3900?
# 9417

def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """

    print(target_course)
    conditions = get_target_conditions(target_course)

    # Get rid of the word prerequisite at the start
    if len(conditions) > 0 and is_prereq(conditions[0]):
        conditions = conditions[1:]

    # For course codes that're just numbers, assume they mean COMP and fix them
    for i, condition in enumerate(conditions):
        if is_bad_course_code(condition):
            conditions[i] = 'COMP' + condition
    
    # Check the UOC first
    # There are 3 cases:
    #  - Need some courses OR some amount of UOC
    #  - Need some courses AND some amount of UOC
    #  - Need some amount of UOC in a list
    # COMP3900 [, 'AND', '102', 'UNITS', 'OF', 'CREDIT']
    # COMP3901 ['12', 'UNITS', 'OF', 'CREDIT', 'IN', 'LEVEL', '1', 'COMP', 'COURSES', 'AND', '18', 'UNITS', 'OF', 'CREDIT', 'IN', 'LEVEL', '2', 'COMP', 'COURSES']
    # COMP3902 [, 'AND', '12', 'UNITS', 'OF', 'CREDIT', 'IN', 'LEVEL', '3', 'COMP', 'COURSES']
    # COMP4128 [, 'AND', '12', 'UNITS', 'OF', 'CREDIT', 'IN', 'LEVEL', '3', 'COMP', 'COURSES']
    # COMP4161 ['COMPLETION', 'OF', '18', 'UNITS', 'OF', 'CREDIT']
    # COMP4601 [, 'AND', 'COMPLETION', 'OF', '24', 'UNITS', 'OF', 'CREDIT']
    # COMP4951 ['36', 'UNITS', 'OF', 'CREDIT', 'IN', 'COMP', 'COURSES']
    # COMP9301 ['12', 'UNITS', 'OF', 'CREDIT', 'IN', 'COMP6443', 'COMP6843', 'COMP6445', 'COMP6845', 'COMP6447']
    # COMP9302 [, 'AND', '12', 'UNITS', 'OF', 'CREDIT', 'IN', 'COMP6443', 'COMP6843', 'COMP6445', 'COMP6845', 'COMP6447']
    # COMP9491 ['18', 'UNITS', 'OC', 'CREDIT', 'IN', 'COMP9417', 'COMP9418', 'COMP9444', 'COMP9447']
    if has_uoc_condition(conditions):
        lo_index = conditions.index('UNITS')
        while lo_index != 0 and not is_course_code(conditions[lo_index - 1]):
            lo_index -= 1
        
        uoc_conditions = conditions[lo_index:]
        uoc_requirements = split_on_ands(uoc_conditions)

        # Remove the conditions relating to uoc now that we're done with it        
        conditions = conditions[:lo_index]

        for requirement in uoc_requirements:
            units_index = requirement.index('UNITS')
            uoc_required = int(requirement[units_index - 1])
            try:
                in_index = requirement.index('IN')
                after_in = requirement[in_index + 1:]

                # At this point, we know it specifies courses for the UOC requirement.
                # This could either be of the form 'in level x COMP courses'
                # or 'in <COURSE1>, <COURSE2>, ...'
                uoc_in_requirement = 0

                # Check if all the contents of after_in are course codes
                if are_all_course_codes(after_in):
                    for course_done in courses_list:
                        if course_done in after_in:
                            uoc_in_requirement += 6
                else:                    
                    # Count how many COMP courses in courses done.
                    # Assumes that the courses_done is a valid list of courses
                    if requirement.count('LEVEL') == 1:
                        level_index = requirement.index('LEVEL')
                        level_required = requirement[level_index - 1]

                        for course_done in courses_list:
                            if course_done[4] == level_required:
                                uoc_in_requirement += 6
                    else:
                        faculty = find_first_faculty(requirement)

                        for course_done in courses_list:
                            if course_done[:4] == faculty:
                                uoc_in_requirement += 6
                if uoc_in_requirement < uoc_required:
                    return False
            except:
                # There is no conditions saying 'IN' a specific
                # list of courses or faculty. So just see if
                # overall uoc > required uoc
                if len(courses_list) * 6 < uoc_required:
                    return False
            
    # Iterate through the conditions and make a kind of structure to show how these conditions
    # fit together
    requirements = []
    #print(target_course)
    #print(conditions)
    #print()
    first_code = True
    for i, condition in enumerate(conditions):
        # Check if it's a course code
        if is_course_code(condition):
            # Add the code to the requirements.
            # The spot in which it goes depends on
            # the previous condition. If the previous was 'OR',
            # it goes on the same level as the previous code.
            # If it's an 'AND', it goes on the next level.
            # If this is the first code, start a level.            
            if first_code or is_or(conditions[i - 1]):
                # Add to this current level
                if len(requirements) == 0:
                    requirements.append([])
                requirements[-1].append(condition)
            elif is_and(conditions[i - 1]):
                # Start a new level and add to it
                requirements.append([condition])
            
            first_code = False
        elif is_prereq(condition):
            # Do nothing
            continue
        
    for requirement in requirements:
        satisfied_requirement = False
        for course_done in courses_list:
            if course_done in requirement:
                satisfied_requirement = True
                break
        if not satisfied_requirement:
            return False
    return True

#--------------------------------------------------------------------------------------------

if __name__ == '__main__':
    with open("./conditions.json") as f:
        all_conditions = json.load(f)

        for key in all_conditions.keys():
            print(is_unlocked([], key))
        f.close()
