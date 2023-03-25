import ujson
import csv
import pyfpgrowth
import codecs

from collections import defaultdict

from values import SURVEY_PATH, RELATIONSHIPS_PATH, RELATIONSHIPS_WITH_METRICS_PATH, COAUTHOR_RELATIONSHIPS_RESULTS_PATH, TEAM_RELATIONSHIPS_RESULTS_PATH

with codecs.open(SURVEY_PATH, mode='r', encoding='utf8', errors='ignore') as f:
    papers = ujson.load(f)
    transactions = [paper["authors"] for paper in papers]

min_support = 5
patterns = pyfpgrowth.find_frequent_patterns(transactions, min_support)

min_confidence = 0.5
rules = pyfpgrowth.generate_association_rules(patterns, min_confidence)

relationships = defaultdict(list)

for rule in rules.items():
    antecedent, (consequent, confidence) = rule
    if len(antecedent) == 1 and len(consequent) == 1:
        relationships["coauthors"].append({
            "author1": antecedent[0],
            "author2": consequent[0],
            "confidence": confidence
        })
    elif len(antecedent) + len(consequent) > 2:
        relationships["teams"].append({
            "team_members": list(antecedent) + list(consequent),
            "confidence": confidence
        })

publications = defaultdict(int)

for paper in papers:
    for author in paper["authors"]:
        publications[author] += 1

with open(RELATIONSHIPS_PATH, "w") as f:
    ujson.dump(relationships, f, indent=4)

def calculate_lift(num_antecedent, num_consequent, num_relationship, num):
    return (num_relationship * num) / (num_antecedent * num_consequent)

def calculate_cosine(num_antecedent, num_consequent, num_relationship):
    return num_relationship / ((num_antecedent * num_consequent) ** 0.5)

def calculate_full_confidence(num_antecedent, num_consequent, num_relationship):
    return min(num_relationship / num_antecedent, num_relationship / num_consequent)

def calculate_max_confidence(num_antecedent, num_consequent, num_relationship):
    return max(num_relationship / num_antecedent, num_relationship / num_consequent)

def calculate_kulc(num_antecedent, num_consequent, num_relationship):
    return 0.5 * (num_relationship / num_antecedent + num_relationship / num_consequent)

def calculate_all_metrics(item, patterns, antecedent, consequent):
    num_antecedent = patterns.get(antecedent, 0)
    num_consequent = patterns.get(consequent, 0)
    num_relationship = patterns.get(antecedent + consequent, 0)
    
    check_nonzero = num_antecedent == 0 or num_consequent == 0

    item["support"] = float(0) if check_nonzero else (num_relationship / len(transactions))
    item["lift"] = float(0) if check_nonzero else calculate_lift(num_antecedent, num_consequent, num_relationship, len(transactions))
    item["cosine"] = float(0) if check_nonzero else calculate_cosine(num_antecedent, num_consequent, num_relationship)
    item["full_confidence"] = float(0) if check_nonzero else calculate_full_confidence(num_antecedent, num_consequent, num_relationship)
    item["max_confidence"] = float(0) if check_nonzero else calculate_max_confidence(num_antecedent, num_consequent, num_relationship)
    item["kulc"] = float(0) if check_nonzero else calculate_kulc(num_antecedent, num_consequent, num_relationship)

for coauthor in relationships["coauthors"]:
    num_relationship = patterns.get((coauthor["author1"], coauthor["author2"]), 0)
    num_author1 = publications[coauthor["author1"]]
    num_author2 = publications[coauthor["author2"]]
    antecedent = (coauthor["author1"],)
    consequent = (coauthor["author2"],)
    activity_score = num_relationship / (num_author1 + num_author2 - num_relationship)
    coauthor["activity_score"] = activity_score
    calculate_all_metrics(coauthor, patterns, antecedent, consequent)

for team in relationships["teams"]:
    antecedent = tuple(sorted(team["team_members"][:-1]))
    consequent = (team["team_members"][-1],)

    calculate_all_metrics(team, patterns, antecedent, consequent)

with open(RELATIONSHIPS_WITH_METRICS_PATH, "w") as f:
    ujson.dump(relationships, f, indent=4)

with open(COAUTHOR_RELATIONSHIPS_RESULTS_PATH, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(["Author1", "Author2", "Confidence", "Activity Score", "Support", "Lift", "Cosine", "Full Confidence", "Max Confidence", "Kulc"])

    for coauthor in relationships["coauthors"]:
        writer.writerow(list(coauthor.values()))

with open(TEAM_RELATIONSHIPS_RESULTS_PATH, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(["Members", "Confidence", "Support", "Lift", "Cosine", "Full Confidence", "Max Confidence", "Kulc"])
    for team in relationships["teams"]:
        team_members = ', '.join(map(str, team["team_members"]))
        writer.writerow([team_members] + list(team.values())[1:])
