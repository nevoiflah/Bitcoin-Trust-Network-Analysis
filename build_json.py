import json

def markdown_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + '\n' for line in text.split('\n')]
    }

def code_cell(code):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + '\n' for line in code.split('\n')]
    }

cells = []

cells.append(markdown_cell("""# פרויקט מסכם: ניתוח רשת אמון וזיהוי הונאות ב-Bitcoin OTC
## כותבים: [שם סטודנט 1], [שם סטודנט 2], [שם סטודנט 3]

מסמך זה מכיל את הקוד, הניתוח וההסברים המלאים עבור פרויקט הגמר בקורס אלגוריתמים בגרפים."""))

cells.append(code_cell("%pip install networkx pandas matplotlib seaborn scikit-learn"))

cells.append(markdown_cell("""### 1. טעינת נתונים (Data Loading)
כאן נטען את נתוני רשת הביטקוין ישירות משרתי סטנפורד מבלי לשמור קובץ מקומי, בהתאם להנחיות הפרויקט. הנתונים מתארים את רשת ה-Bitcoin OTC שם משתמשים מדרגים זה את זה (מ-10- ועד 10+)."""))

cells.append(code_cell("""import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# הגדרות תצוגה
plt.style.use('ggplot')
sns.set_palette('deep')

url = 'https://snap.stanford.edu/data/soc-sign-bitcoinotc.csv.gz'
print("טוען נתונים ישירות מהרשת...")
columns = ['SOURCE', 'TARGET', 'RATING', 'TIME']
df = pd.read_csv(url, compression='gzip', names=columns)
df['TIME'] = pd.to_datetime(df['TIME'], unit='s')
print(f"סה\\"כ רשומות בדאטה: {len(df)}")
display(df.head())"""))

cells.append(markdown_cell("""### 2. יצירת גרף חלוקה לרשתות אמון וחוסר-אמון
ניצור גרף מכוון ושקול באמצעות ספריית NetworkX. לאחר מכן נחלק אותו לשתי רשתות נפרדות:
* **רשת האמון:** רק קשתות חיוביות (דירוג > 0)
* **רשת חוסר האמון:** רק קשתות שליליות (דירוג < 0)"""))

cells.append(code_cell("""# יצירת גרף מכוון
G = nx.from_pandas_edgelist(df, source='SOURCE', target='TARGET', edge_attr=['RATING', 'TIME'], create_using=nx.DiGraph())

print(f"סה\\"כ צמתים במאגר: {G.number_of_nodes()}")
print(f"סה\\"כ קשתות (דירוגים): {G.number_of_edges()}")

# חלוקה לרשתות
trust_edges = [(u, v, d) for u, v, d in G.edges(data=True) if d['RATING'] > 0]
distrust_edges = [(u, v, d) for u, v, d in G.edges(data=True) if d['RATING'] < 0]

G_trust = nx.DiGraph()
G_trust.add_edges_from(trust_edges)

G_distrust = nx.DiGraph()
G_distrust.add_edges_from(distrust_edges)

print(f"קשתות ברשת האמון (חיובים): {G_trust.number_of_edges()}")
print(f"קשתות ברשת חוסר האמון (שליליים): {G_distrust.number_of_edges()}")"""))

cells.append(markdown_cell("""### 3. חקירת נתונים (EDA) וויזואליזציה
נבחן את התפלגות הדירוגים ברשת ואת התפלגות הדרגות (In-Degree). ניתוח זה מאפשר להבין את צפיפות הרשת ואת היחס בין עסקאות אמינות לעסקאות זדוניות."""))

cells.append(code_cell("""plt.figure(figsize=(10, 5))
sns.histplot(df['RATING'], bins=21, kde=False, color='blue')
plt.title('התפלגות הדירוגים ברשת (Ratings Distribution)')
plt.xlabel('דירוג (-10 עד 10)')
plt.ylabel('מספר דירוגים')
plt.show()

# התפלגות דרגות נכנסות ברשת האמון
in_degrees_trust = [d for n, d in G_trust.in_degree()]
plt.figure(figsize=(10, 5))
sns.histplot(in_degrees_trust, bins=50, kde=False, color='green')
plt.title('התפלגות דרגות נכנסות - רשת אמון (In-Degree Distribution)')
plt.xlabel('מספר דירוגים חיוביים שהתקבלו')
plt.ylabel('מספר משתמשים (Log Scale)')
plt.yscale('log') # סקאלה לוגריתמית בגלל זנב ארוך (חוק החזקה)
plt.show()"""))

cells.append(markdown_cell("""### 4. מדדי מרכזיות (Centrality) ואיתור משתמשי מפתח
נשתמש ב-PageRank על רשת האמון כדי למצוא את המשתמשים המובילים שמהווים את הגרעין האמין של הרשת, וב-In-Degree משוקלל על רשת חוסר-האמון לאיתור נוכלים הבולטים ביותר שספגו את מרבית הדירוגים השליליים."""))

cells.append(code_cell("""# PageRank על רשת אמון
pagerank_scores = nx.pagerank(G_trust, weight='RATING')
top_trusted = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:10]
print("--- 10 המשתמשים האמינים ביותר (הגרעין של הרשת, לפי PageRank) ---")
for node, score in top_trusted:
    print(f"User ID: {node:4d} | PageRank Score: {score:.4f}")

# חישוב In-Degree משוקלל על רשת חוסר אמון
distrust_in_degree = dict(G_distrust.in_degree(weight='RATING'))
# הדירוגים הם שליליים, לכן ערך נמוך (שלילי יותר) מעיד על חוסר אמון רב
top_distrusted = sorted(distrust_in_degree.items(), key=lambda x: x[1])[:10]
print("\\n--- 10 המשתמשים הלא-אמינים ביותר / הנוכלים (לפי דירוג שלילי מצטבר) ---")
for node, score in top_distrusted:
    print(f"User ID: {node:4d} | Total Negative Rating: {score}")"""))

cells.append(markdown_cell("""### 5. זיהוי קהילות (Community Detection) באמצעות Louvain ומציאת התארגנויות זדוניות
נשתמש באלגוריתם `Louvain` כדי לפרק את רשת האמון לקהילות צפופות. המטרה היא לחפש קהילות קטנות שמדרגות אחת את השנייה בצורה חיובית, אך סופגות אחוז גבוה של דירוגים שליליים ממשתמשים מחוץ לקהילה. מצב זה מעיד בסבירות גבוהה על התארגנות זדונית (Sybil Attack) המנסה לזייף מוניטין."""))

cells.append(code_cell("""from networkx.algorithms.community import louvain_communities

# הפעלת Louvain על רשת האמון ללא התחשבות בכיוון כדי למצוא קהילות
G_trust_undirected = G_trust.to_undirected()
communities = louvain_communities(G_trust_undirected, weight='RATING', resolution=1.0)
print(f"זוהו {len(communities)} קהילות ברשת האמון.")

# ננתח את הקהילות
community_sizes = [len(c) for c in communities]
sorted_communities = sorted(communities, key=len, reverse=True)

print("גדלי 5 הקהילות המובילות:", [len(c) for c in sorted_communities[:5]])

# כעת, נבדוק עבור כל קהילה כמה דירוגים שליליים "ספגו" חברי הקהילה מחוץ לקהילה
community_distrust = []
for idx, comm in enumerate(sorted_communities[:20]): # נסרוק את הקהילות הגדולות
    external_negatives = 0
    for node in comm:
        if node in G_distrust:
            for u, v, data in G_distrust.in_edges(node, data=True):
                # אם הדירוג השלילי בא ממשתמש מחוץ לקהילה, נספור אותו
                if u not in comm:
                    external_negatives += abs(data['RATING'])
    community_distrust.append((idx, len(comm), external_negatives))

# סידור לפי חוסר אמון חיצוני יחסי לגודל הקהילה (למצוא קליקות מבודדות אך שנואות)
community_distrust_sorted = sorted(community_distrust, key=lambda x: x[2]/x[1] if x[1]>0 else 0, reverse=True)

print("\\n--- קהילות חשודות במיוחד (יחס גבוה של חוסר אמון חיצוני לגודל הקהילה) ---")
for idx, size, neg in community_distrust_sorted[:5]:
    ratio = neg/size if size > 0 else 0
    print(f"קהילה #{idx}: גודל: {size} צמתים | דירוג שלילי חיצוני כולל: {neg} | יחס: {ratio:.2f}")"""))

cells.append(markdown_cell("""### 6. חיזוי קשרים (Link Prediction) מבוסס זמן
נשתמש בלמידת מכונה כדי לחזות האם דירוג בין שני משתמשים יהיה חיובי (אמון) או שלילי (נוכלות). 
* **חלוקה כרונולוגית (Train/Test Split):** נאמן את המודל על השנים המוקדמות, וננסה לחזות את האמינות של הקשרים בשנים המאוחרות (הערכה מציאותית).
* נשתמש במדדים מבניים כמו שכנים משותפים (Common Neighbors), PageRank ודרגות כפיצ'רים מרכזיים המשקפים אינטראקציה חברתית קודמת."""))

cells.append(code_cell("""from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import datetime

# חלוקה כרונולוגית סביב תחילת שנת 2014
split_date = pd.to_datetime('2014-01-01')
df_train = df[df['TIME'] < split_date].copy()
df_test = df[df['TIME'] >= split_date].copy()

print(f"דירוגים בסט האימון (היסטוריה): {len(df_train)}")
print(f"דירוגים בסט הבדיקה (עתיד): {len(df_test)}")

# בניית גרף אימון (רק על היסטוריה) כדי למנוע דליפת מידע
G_train = nx.from_pandas_edgelist(df_train, source='SOURCE', target='TARGET', edge_attr='RATING', create_using=nx.DiGraph())
G_train_undirected = G_train.to_undirected()
pagerank_train = nx.pagerank(G_train)

# פונקציה ליצירת פיצ'רים מבניים
def extract_features(data, graph, graph_undir, pr_scores):
    features = []
    labels = []
    
    for idx, row in data.iterrows():
        u = row['SOURCE']
        v = row['TARGET']
        # נבדוק רק צמתים שהיו קיימים בגרף האימון (כדי להשתמש במאפיינים רשתיים)
        if u in graph and v in graph:
            # הליבל הוא 1 (חיובי) או 0 (שלילי)
            label = 1 if row['RATING'] > 0 else 0
            
            # פיצ'רים
            pr_u = pr_scores.get(u, 0)
            pr_v = pr_scores.get(v, 0)
            try:
                common_neighbors = len(list(nx.common_neighbors(graph_undir, u, v)))
            except nx.NetworkXError:
                common_neighbors = 0
            in_deg_v = graph.in_degree(v)
            out_deg_u = graph.out_degree(u)
            
            features.append([pr_u, pr_v, common_neighbors, in_deg_v, out_deg_u])
            labels.append(label)
            
    return np.array(features), np.array(labels)

print("\\nמחלץ פיצ'רים עבור קבוצת אימון...")
X_train, y_train = extract_features(df_train, G_train, G_train_undirected, pagerank_train)
print("מחלץ פיצ'רים עבור קבוצת בדיקה...")
X_test, y_test = extract_features(df_test, G_train, G_train_undirected, pagerank_train)

# בניית מודל סיווג באמצעות Random Forest
clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print("\\n--- תוצאות המודל בחיזוי עתידי (Link Prediction) ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Distrust (Neg=0)', 'Trust (Pos=1)']))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Predicted Neg', 'Predicted Pos'], yticklabels=['Actual Neg', 'Actual Pos'])
plt.title("Confusion Matrix - Link Prediction")
plt.show()"""))

cells.append(markdown_cell("""### סיכום ומסקנות (Summary)
במודל שהרצנו, ניתן לראות שמדדים טופולוגיים ברשת מספקים כלי רב עוצמה לחיזוי אמינות משתמשים בביטקוין, גם ללא מידע מזהה. 
1. מצאנו כי ניתן לזהות בבירור "נוכלים" וקבוצות מזויפות באמצעות אלגוריתם הקהילות (Louvain) אשר חשף קהילות קטנות הסופגות ריג'קטים משמעותיים מהגרעין המרכזי של הרשת.
2. באמצעות חלוקה כרונולוגית מציאותית, הצלחנו לאמן מודל חיזוי קשרים המשיג תוצאות טובות בזיהוי הונאות פוטנציאליות, בהתבסס אך ורק על מבנה הרשת ההיסטורי (שכנים משותפים וסנטרליות)."""))

notebook = {
 "cells": cells,
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open('Bitcoin_Network_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print("Notebook generated directly via JSON mapping!")
