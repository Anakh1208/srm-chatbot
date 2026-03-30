import json

# Load data
with open('../data/structured/campus_locations.json') as f:
    locations = json.load(f)

with open('../data/structured/departments.json') as f:
    departments = json.load(f)

print("="*70)
print("SRM CAMPUS DATA DEMO")
print("="*70)

# Show statistics
print(f"\nTotal Buildings: {len(locations['campus_locations'])}")
print(f"Total Departments: {len(departments['departments'])}")
print(f"Total Classrooms: {locations['important_statistics']['total_classrooms']}")

# Demo Query 1: Where is Tech Park?
print("\n" + "="*70)
print("Query 1: Where is Tech Park?")
print("="*70)

for loc in locations['campus_locations']:
    if 'tech park' in loc['name'].lower():
        print(f"\nAnswer: {loc['name']}")
        print(f"Campus: {loc['campus']}")
        print(f"Floors: {loc['floors']}")
        print(f"Area: {loc['area_sqft']:,} sq.ft")
        print(f"Departments: {', '.join(loc['departments'])}")
        if 'classrooms' in loc:
            print(f"Classrooms: {loc['classrooms']}")
        break

# Demo Query 2: Tell me about CSE
print("\n" + "="*70)
print("Query 2: Tell me about CSE department")
print("="*70)

for dept in departments['departments']:
    if dept['id'] == 'cse':
        print(f"\nAnswer: {dept['name']}")
        print(f"Building: {dept['building']}")
        print(f"Campus: {dept['campus']}")
        if 'total_classrooms' in dept:
            print(f"Classrooms: {dept['total_classrooms']}")
        print(f"Programs: {dept['programs'][0]['name']}")
        print(f"Facilities: {', '.join(dept['facilities'][:3])}...")
        break

# Demo Query 3: How many classrooms?
print("\n" + "="*70)
print("Query 3: How many classrooms does SRM have?")
print("="*70)

stats = locations['important_statistics']
print(f"\nAnswer: SRM has {stats['total_classrooms']} classrooms")
print(f"  - Main Campus: {stats['main_campus_classrooms']}")
print(f"  - Annexure-I: {stats['annexure_1_classrooms']}")
print(f"  - Annexure-II: {stats['annexure_2_classrooms']}")

print("\n" + "="*70)
print("DATA READY FOR INTEGRATION!")
print("="*70)
