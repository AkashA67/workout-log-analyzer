import re


# 1) Raw text extraction

gym_log = '10_07_25 Torso A.txt'

with open(gym_log, 'r', encoding= 'UTF-8') as logs:
    original_list = [line.strip() for line in logs]


lines = [item for item in original_list if item != '' ]


# 2) REGEX Pattens


date_pattern = re.compile(r"^(\d{1,2}.\d{1,2}.\d{2,4})\s+(.+)$")

not_exercise_pattern = re.compile(r"^(S\d:|.*:|^(\d{1,2}.\d{1,2}.\d{2,4})\s+(.+)$)")

set_pattern = re.compile(r"^(S\d+):\s*(.+)$", re.IGNORECASE)

note_pattern = re.compile(r"\(([)]*)\)") 


# for line in lines:
#     match = date_pattern.match(line)
#     if match:
#         print(match.group(0))

# exercise_names = []
# for line in lines:
#     if not not_exercise_pattern.match(line):
#         names = re.sub(r"^\d+\.\s+", "", line).strip()
        
#         if names:
#             exercise_names.append(names.lower())

# print(exercise_names[:10])

for line in lines:
    match = note_pattern.match(line)
    if match:
        print(match)