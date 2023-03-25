import os

IN_DIR = "inputs"
JOURNS_PATH = os.path.join(IN_DIR, "conf_journ.csv")
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "dblp.xml")
OUT_DIR = "outputs"
SURVEY_PATH = os.path.join(OUT_DIR, "dblp_survey.json")
RELATIONSHIPS_PATH = os.path.join(OUT_DIR, "relationships.json")
RELATIONSHIPS_WITH_METRICS_PATH = os.path.join(OUT_DIR, "relationships_with_metrics.json")
COAUTHOR_RELATIONSHIPS_RESULTS_PATH = os.path.join(OUT_DIR, "coauthor_relationships_with_metrics.csv")
TEAM_RELATIONSHIPS_RESULTS_PATH = os.path.join(OUT_DIR, "team_relationships_with_metrics.csv")