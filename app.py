import json, openai, os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("openAI_API_Key")


def extract_keywords(data):
    system_intel = "The given data is AICTE syllabus for AIML course. Generate important keywords from the given Syllabus. The keyword count must be restricted to 15-20 only. These 15-20 keywords must be of high IMPORTANCE among all keywords. GIVE HIGH PRIORITY TO TECHNOLOGICAL KEYWORDS. DO NOT GENERATE ANY EXTRA TEXT OTHER THAN KEYWORDS. YOUR RESPONSE MUST CONTAIN ONLY COMMA SEPARATED KEYWORDS."

    input = ""
    keywords = []

    for course in data:
        title = course["title"]
        syllabus = course["syllabus"]
        input += "Title:" + title + "\nSylabus: " + syllabus + "\n\n"

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_intel},
            {"role": "user", "content": input},
        ],
    )
    response = result["choices"][0]["message"]["content"]
    # print(course, end="\n\n")
    # print(response, end="\n\n\n")

    keywords_ = response.split(", ")
    for keyword in keywords_:
        keywords.append(keyword)

    # print("All keywords:", keywords)

    return keywords


def cluster_keywords(keywords):
    system_intel = "You are an NLP model. Your will be given a list of keywords. Your job is to analyze the keywords given to you with the help of your NLP abilities, and generate a number (for each pair) in the range of [0,1] which defines how closely those keywords are related to each other. YOUR RESPONSE SHOULD BE IN THE FOLLOWING FORMAT. 1. DISPLAY NO REASONS OR ANY OTHER EXTRA WORDS. 2. FOR EACH PAIR, Keyword1, Keyword2, Relatedness Score SEPERATED BY COMMA. 3. SEPARATE EACH PAIR DATA WITH A NEWLINE."

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_intel},
            {"role": "user", "content": "Keywords : " + str(keywords)},
        ],
    )
    response = result["choices"][0]["message"]["content"]
    # print("Response:\n", response, sep="")

    output = response.split("\n")

    n = len(output)
    i = 0
    while i < n:
        if len(output[i]) == 0:
            output.pop(i)
            n -= 1
            i -= 1
        i += 1
    for i in range(len(output)):
        output[i] = output[i].split(",")
        output[i][0] = output[i][0].strip()
        output[i][1] = output[i][1].strip()
        output[i][2] = output[i][2].strip()
        if output[i][2][-1] == "\\":
            output[i][2] = output[i][2][:-1]
        output[i][2] = float(output[i][2])

    # print("\n\n\n", output)

    def get_index_of_cluster_containing_k(k):
        for i in range(len(clusters)):
            if k in clusters[i]:
                return i

    clusters = []
    inserted_keywords = []

    for i in range(len(output)):
        k1 = output[i][0]
        k2 = output[i][1]
        score = output[i][2]
        if score >= 0.6:
            if k1 in inserted_keywords and k2 in inserted_keywords:
                # search for k1
                j1 = get_index_of_cluster_containing_k(k1)
                # print("j1:",j1,end=" ")
                j2 = get_index_of_cluster_containing_k(k2)
                if len(clusters[j1]) == 1:
                    clusters[j1].remove(k1)
                    clusters[j2].append(k1)
                elif len(clusters[j2]) == 1:
                    clusters[j2].remove(k2)
                    clusters[j1].append(k2)
                # print('0',end="")
            elif k1 in inserted_keywords:
                # search for k1 and insert k2 in that cluster
                j = get_index_of_cluster_containing_k(k1)
                clusters[j].append(k2)
                inserted_keywords.append(k2)
                # print('1',end="")
            elif k2 in inserted_keywords:
                # search for k2 and insert k1 in that cluster
                j = get_index_of_cluster_containing_k(k2)
                clusters[j].append(k1)
                inserted_keywords.append(k1)
                # print('2',end="")
            else:
                clusters.append([k1, k2])
                inserted_keywords.append(k1)
                inserted_keywords.append(k2)
                # print('3',end="")
        else:
            if k1 not in inserted_keywords:
                clusters.append([k1])
                inserted_keywords.append(k1)
                # print('4',end="")
            if k2 not in inserted_keywords:
                clusters.append([k2])
                inserted_keywords.append(k2)
                # print('5',end="")
        # print(clusters,";",inserted_keywords)

    print("Clusters:", clusters)

    keywords_x = []
    clusters_y = []
    for i in range(len(clusters)):
        for keyword in clusters[i]:
            keywords_x.append(keyword)
            clusters_y.append(i + 1)
    # print(keywords_x, "\n", clusters_y, sep="")

    unique_clusters = []
    for i in range(len(clusters_y)):
        clusters_y[i] = str(clusters_y[i])
        if str(clusters_y[i]) not in unique_clusters:
            unique_clusters.append(str(clusters_y[i]))

    import plotly.express as px

    data = dict(
        character=["Clusters"] + unique_clusters + keywords_x,
        parent=[""] + ["Clusters"] * len(unique_clusters) + clusters_y,
        value=[1] * (len(unique_clusters) + len(keywords_x) + 1),
    )

    fig = px.sunburst(
        data,
        names="character",
        parents="parent",
        values="value",
    )

    fig.update_traces(insidetextorientation="radial")

    fig.update_layout(
        autosize=False,
        width=900,
        height=900,
        font=dict(family="Comic Sans MS", size=18),
    )

    fig.show()

    if not os.path.exists("static/images"):
        os.mkdir("static/images")
    fig.write_image("static/images/clusters.png")

    return clusters


def getPercentages_API(data, clusters):
    system_intel = (
        "Here are the 5 keyword clusters as per the standard AICTE recommended curriculum: "
        + str(clusters)
        + ". Your job is to analyze the given curriculum with respect to these keyword clusters and generate the inclusiveness scores (% of topics included) corresponding to each cluster. YOUR RESPONSE MUST ONLY CONTAIN THE VALUES IN A COMMA SEPARATED FORMAT. THE VALUES MUST BE WHOLE NUMBERS AND SHOULD NOT CONTAIN DECIMALS. DO NOT PROVIDE ANY OTHER INFORMATION OTHER THAN THE VALUES."
    )

    input = ""
    keywords = []

    for course in data:
        title = course.get("title")
        syllabus = course.get("syllabus")
        input += "Title:" + title + "\nSyllabus: " + syllabus + "\n\n"

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_intel},
            {"role": "user", "content": input},
        ],
    )
    response = result["choices"][0]["message"]["content"]
    # print(course, end="\n\n")
    # print(response, end="\n\n\n")

    percentages = []
    percentages_ = response.split(",")
    for percentage in percentages_:
        percentages.append(percentage.strip())

    return percentages


def getSuggestions_API(data, clusters):
    system_intel = (
        "Here are the 5 keyword clusters as per the standard AICTE recommended curriculum: "
        + str(clusters)
        + ". Your job is to analyze the given curriculum with respect to these keyword clusters and Generate a modified curriculum. The modified curriculum MUST include every single topic from the AICTE keyword clusters. Treat each cluster as a chapter and mention detailed explanations of topics included in each chapter. The modified syllabus MUST be in same format (title, content) as the given syllabus. YOUR RESPONSE MUST BE IN STRICT JSON FORMAT. NO OTHER STATEMENTS OTHER THAN THE JSON ARRAY MUST BE RETURNED."
    )

    input = ""
    keywords = []

    for course in data:
        title = course.get("title")
        syllabus = course.get("syllabus")
        input += "title:" + title + "\ncontent: " + syllabus + "\n\n"

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_intel},
            {"role": "user", "content": input},
        ],
    )
    response = result["choices"][0]["message"]["content"]
    # print(course, end="\n\n")
    # print(response, end="\n\n\n")

    return response


app = Flask(__name__)
app.debug = True


@app.route("/")
def index():
    return render_template("index.html")


aicte_clusters = [
    [
        "Machine Learning",
        "Supervised Learning",
        "Unsupervised Learning",
        "Deep Learning",
    ],
    [
        "Artificial Intelligence",
        "Problem Solving Techniques",
        "Logic",
        "Knowledge Representation",
        "Planning",
    ],
    [
        "Activation Functions",
        "Auto-encoders",
        "Regularization",
        "Deep Learning Models",
    ],
    [
        "Bayesian Learning",
        "Decision Trees",
        "Reinforcement Learning",
        "Ensemble Methods",
    ],
    [
        "Optimization Techniques",
        "Machine Learning Strategy",
        "Responsible Machine Learning",
        "Machine Learning in Production",
        "Feeding of Machine Learning Model",
    ],
]

@app.route("/getClusters", methods=["POST"])
def getClusters():
    # print("\n\nAICTE clusters:\n", aicte_clusters)

	clusters_dict = {}
	for i in range(len(aicte_clusters)):
		clusters_dict[i] = aicte_clusters[i]
	# print(clusters_dict)
	clusters_json = jsonify(clusters_dict)

	return clusters_json


@app.route("/getPercentages", methods=["POST"])
def getPercentages():
    form_data = request.get_json()
    # print("Form data: ", form_data)

    # print("\n\nAICTE clusters:\n", aicte_clusters)

    percentages = getPercentages_API(form_data, aicte_clusters)
    # print(percentages)

    percentages_dict = {}
    for i in range(len(percentages)):
        percentages_dict[i] = percentages[i]
    print(percentages_dict)
    percentages_json = jsonify(percentages_dict)

    return percentages_json


@app.route("/getSuggestions", methods=["POST"])
def getSuggestions():
    form_data = request.get_json()
    # print("Form data: ", form_data)

    # print("\n\nAICTE clusters:\n", aicte_clusters)

    response = getSuggestions_API(form_data, aicte_clusters)
    print("Response: ", response)

    curricula_dict = {"old": form_data, "new": json.loads(response)}
    curricula_json = jsonify(curricula_dict)
    # print("JSON: ", curricula_dict)

    return curricula_json


if __name__ == "__main__":
    app.run()
