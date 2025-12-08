import re
import pandas as pd
def normalize_exercise(name: str) -> str:

    if not name or pd.isna(name):
        return name 
    

    cleaned = re.sub(r'\s+', " ", name.strip().lower())

    mapping = {
    # Normalised Squats
    "barbell back squats": "Barbell Back Squats",
    "barbell squats"     : "Barbell Back Squats",

    # Normalised Bench Press
    "barbell bench press"   : "Barbell Bench Press",
    "bench press"           : "Barbell Bench Press",

    # Normalised Bent Over Row
    "barbell bent-over rows" : "Barbell Bent Over Rows",
    "barbell rows"           : "Barbell Bent Over Rows",

    # Normalised Bicep Curl (Barbell)
    "barbell curls" : "Barbell Bicep Curls",

    # Normalised Good Morning
    "barbell good mornings": "Barbell Good Mornings",
    "good mornings"        : "Barbell Good Mornings",

    # Normalised Hammer Curl (Barbell)
    "barbell hammer curl": "Barbell Hammer Curls",

    # Normalised Overhead Press
    "barbell overhead press"   : "Barbell Overhead Press",
    "seated barbell ohp"       : "Seated Barbell Press",
    "overhead press"           : "Barbell Overhead Press",
    "over head press"          : "Barbell Overhead Press",
    "standing overhead press"  : "Barbell Overhead Press",
    "seated db shoulder press" : "Seated Dumbbell Press",
    "seated db press"          : "Seated Dumbbell Press",

    # Normalised Romanian Deadlift
    "barbell rdl" : "Barbell RDLs",
    "db rdl"      : "Dumbbell RDLs",

    # Normalised Shrugs
    "barbell shrugs"  : "Shrugs",
    "db shrugs"       : "Shrugs",
    "trap-bar shrugs" : "Shrugs",

    # Bulgarian Split Squat
    "bulgarian split squats": "Bulgarian Split Squats",

    # Cable Crunch
    "cable crunches": "Cable Crunches",

    # Cable Bicep Curl
    "cable curls": "Cable Bicep Curls",

    # Cable Tricep Kickback
    "cable kickback"        : "Cable Tricep Kickbacks",
    "cable triceps kickback": "Cable Tricep Kickbacks",
    "cable tricep kickback" : "Cable Tricep Kickbacks",

    # Cable Lateral Raise
    "cable lateral raises"     : "Cable Lateral Raises",
    "cable lateral raises"     : "Cable Lateral Raises",
    "db lateral raises"        : "Dumbbell Lateral Raises",
    "db lateral raises"        : "Dumbbell Lateral Raises",
    "incline db lateral raises": "Incline DB Lateral Raises",

    # Cable Tricep Pushdown
    "cable pushdowns"         : "Cable Tricep Pushdowns",
    "cable triceps pushdown"  : "Cable Tricep Pushdowns",
    "triceps cable push down" : "Cable Tricep Pushdowns",
    "triceps pushdown"        : "Cable Tricep Pushdowns",

    # Cable Seated Row
    "cable seated rows" : "Seated Cable Rows",
    "seated cable row"  : "Seated Cable Rows",
    "seated cable rows" : "Seated Cable Rows",
    "seated row"        : "Seated Cable Rows",

    # Chest Pec Fly / Pec Dec
    "chest pec dec"              : "Chest Pec Deck",
    "reverse pec dec"            : "Reverse Pec Deck",
    "single arm reverse pec dec" : "1-Arm Reverse Pec Deck",

    # Chest Supported DB Row
    "chest supported db row": "Chest Supported DB Rows",

    # Dumbbell Bench Press
    "db bench press"  : "Dumbbell Bench Press",
    "incline db press": "Incline Dumbbell Press",
    

    # Dumbbell Hammer Curl
    "db hammer curls"   : "Dumbbell Hammer Curls",
    "hammer curls"      : "Dumbbell Hammer Curls",
    "rope hammer curls" : "Cable Hammer Curls",

    # Dumbbell Preacher Curl
    "db preacher curls" : "Dumbbell Preacher Curls",
    "preacher curls"    : "Dumbbell Preacher Curls",

    # Deadlift
    "deadlift"  : "Deadlifts",
    "deadlifts" : "Deadlifts",

    # Decline Crunch
    "declined crunches" : "Decline Crunches",

    # EZ Bar Bicep Curl
    "ez bar curls"       : "EZ Bar Bicep Curls",
    "ez bar spider curls": "EZ Bar Spider Curls",

    # EZ Bar Skull Crusher
    "ez skull crusher"  : "EZ Bar Skull Crushers",
    "ez skull crushers" : "EZ Bar Skull Crushers",

    # Elbow-Supported Leg Raise
    "elbow supported leg raises" : "Elbow-Supported Leg Raises",
    "elbow supported leg rises"  : "Elbow-Supported Leg Raises",
    "elbow supported leg raises" : "Elbow-Supported Leg Raises",

    # Face Pull
    "face pulls" : "Face Pulls",

    # Farmer Carry
    "farmer carry db" : "Farmer Carry",

    # Finger Push-Up
    "finger push ups" : "Finger Push-Ups",

    # Front Squat
    "front squats"   : "Front Barbell Squats",
    "goblet squats"  : "Front Dumbbell Squats",

    # Front Wrist Curl
    "db front wrist curls": "Front Wrist Curls",
    "front wrist curl"    : "Front Wrist Curls",
    "front wrist curls"   : "Front Wrist Curls",
    "wrist curls"         : "Front Wrist Curls",

    # Hack Squat
    "hack squats": "Hack Squat",

    # Hanging Knee/Leg Raise
    "hanging knee raises" : "Hanging Knee Raises",
    "hanging knee rises"  : "Hanging Knee Raises",
    "hanging kneeraises"  : "Hanging Knee Raises",
    "hanging knee raises" : "Hanging Knee Raises",
    "hanging knee raises" : "Hanging Knee Raises",
    "hanging leg rises"   : "Hanging Leg Raises",

    # Incline Barbell Bench Press
    "incline barbell bench press" : "Incline Barbell Bench Press",
    "incline barbell press"       : "Incline Barbell Bench Press",
    "incline bench press"         : "Incline Barbell Bench Press",
    "inclined barbell press"      : "Incline Barbell Bench Press",
    "incline smith bench press"   : "Incline Smith Bench Press",

    # Incline Dumbbell Reverse Fly
    "incline db reverse flys"  : "Incline Dumbbell Reverse Fly",
    "incline reverse db flies" : "Incline Dumbbell Reverse Fly",
    "seated db reverse flys"   : "Seated Dumbbell Reverse Fly",
    "seated reverse flys"      : "Seated Dumbbell Reverse Fly",

    # L-Sit
    "l sit": "L-Sit",

    # Lat Pulldown
    "lat pulldown": "Lat Pulldown",
    "lat pulldown": "Lat Pulldown",

    # Leg Extension
    "leg extension"        : "Leg Extension",
    "seated leg extension" : "Leg Extension",
    "seated leg extension" : "Leg Extension",

    # Leg Press
    "leg press": "Leg Press",

    # Lying Hamstring Curl
    "lying hamstring curls": "Lying Hamstring Curls",

    # Overhead Cable Tricep Extension
    "over head cable tricep extensions" : "Overhead Cable Tricep Extension",
    "overhead cable extensions"         : "Overhead Cable Tricep Extension",
    "overhead cable triceps extensions" : "Overhead Cable Tricep Extension",
    "overhead cable extension"          : "Overhead Cable Tricep Extension",
    "overhead extension cable"          : "Overhead Cable Tricep Extension",
    "overhead triceps extensions"       : "Overhead Cable Tricep Extension",

    # Plank
    "plank"       : "Plank",
    "side planks" : "Side Plank",

    # Pull-Up / Chin-Up (Weighted)
    "pull-ups"          : "Weighted Pull-Ups",
    "pull-ups"          : "Weighted Pull-Ups",
    "pullups"           : "Weighted Pull-Ups",
    "weighted chinups"  : "Weighted Chin-Ups",
    "chinups"           : "Weighted Chin-Ups",
    "chinups"           : "Weighted Chin-Ups",
    "weighted pull-ups" : "Weighted Pull-Ups",

    # Push-Up
    "push ups": "Push-Ups",

    # Reverse Curl
    "reverse curls"        : "Reverse Curls",
    "reverse curls cable"  : "Reverse Cable Curls",
    "reverse ez bar curls" : "Reverse EZ Bar Curls",

    # Reverse Wrist Curl
    "db reverse wrist curls" : "Reverse Wrist Curls",
    "reverse wrist curls"    : "Reverse Wrist Curls",
    "reverse wrist curls"    : "Reverse Wrist Curls",

    # Seated Calf Raise
    "seated calf raises"   : "Seated Calf Raises",
    "seated calf raise"    : "Seated Calf Raises",
    "standing calf raises" : "Standing Calf Raises",

    # Straight-Arm Cable Pullover
    "stright arm cable pull over": "Straight-Arm Cable Pullover",

    # T-Bar Row
    "t-bar rows": "T-Bar Rows",

    # Triceps Dip (Weighted)
    "triceps dips": "Weighted Triceps Dips",
    "weighted dips": "Weighted Triceps Dips",
    "weighted triceps dips": "Weighted Triceps Dips",

    # Dead Hang
    "dead hang": "Dead Hangs",

    # Leg Compression Lift
    "leg compression lifts": "Leg Compression Lifts",

    # Lunges
    "lunges": "Lunges",
    }

    return mapping.get(cleaned, name)
    
