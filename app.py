import json, openai, os
import google.generativeai as google_ai
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("openAI_API_Key")

google_ai.configure(api_key=os.getenv("gemini_API_Key"))


def getKeywords_API(data):
    input = ""
    keywords = []

    for course in data:
        title = course["title"]
        syllabus = course["syllabus"]
        input += "Title:" + title + "\nContent: " + syllabus + "\n\n"

    # system_intel = "I am working on a project which evaluates a university's curriculum based on the topics included from the Standard syllabus. You will be given the Standard syllabus. Your task is extract the important topics as keywords from the given data. THE KEYWORDS MUST BE UNIQUE AND OF HIGH IMPORTANCE. SINCE YOUR RESPONSE THROUGH API WILL BE USED IN AN APPLICATION DIRECTLY, IT IS VERY IMPORTANT TO STICK TO THE FORMAT. DO NOT GENERATE ANY EXTRA TEXT OTHER THAN THE KEYWORDS SEPARATED BY COMMAS."

    # result = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": system_intel},
    #         {"role": "user", "content": input},
    #     ],
    # )
    # response = result["choices"][0]["message"]["content"]
    # # print(course, end="\n\n")
    # # print(response, end="\n\n\n")

    gemini_prompt = "You will be provided with a syllabus of a computer science related program. Your task is to extract the most important topics from the syllabus as keywords. The keywords must be non-repetitive and computer science related, DO NOT INCLUDE GENERAL TERMS. YOUR RESPONSE THROUGH API WILL BE USED IN AN APPLICATION DIRECTLY. Hence, STRICTLY FOLLOW THE FORMAT. DO NOT GENERATE ANY EXTRA TEXT OTHER THAN THE KEYWORDS SEPARATED BY COMMAS. STRICTLY DO NOT GENERATE MORE THAN 80 KEYWORDS AT ANY COST."

    model = google_ai.GenerativeModel('gemini-pro')
    response = model.generate_content(gemini_prompt + "Data : " + input)
    
    # print(response, end="\n\n\n")

    keywords_ = response.text.split(", ")
    for keyword in keywords_:
        keywords.append(keyword)

    # print("All keywords:\n", keywords)

    return keywords


def getClusters_API(keywords):
    # system_intel = "You are a model which gives relatedness score of two words. Your Job is to analyze the keywords and generate a relatedness score (for each pair) in the range of [0,1]. FORMAT SHOULD BE STRICTLY FOLLOWED AS IT IS THE MOST IMPORTANT PART AND THE FORMAT IS AS FOLLOWS : index of Keyword1, index of Keyword2, relatedness score SEPERATED BY COMMAS FOR EACH PAIR, DO NOT USE PARANTHESIS. DO NOT GENERATE ANY EXTRA TEXT.PUT EACH PAIR DATA IN TO A NEWLINE.ONLY FLOAT VALUES SHOULD BE GIVEN IN PLACE OF RELATEDNESS SCORE.GENERATE COMPLETE ANSWER, DO NOT STOP AT ANY COST. ALWAYS CONTINUE GENERATING TILL YOU COMPLETE THE TASK OF GENERATING RELATEDNESS SCORES FOR ALL THE PAIRS."

    # result = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": system_intel},
    #         {"role": "user", "content": "Keywords : " + str(keywords)},
    #     ],
    # )
    # response = result["choices"][0]["message"]["content"]
    # # print("Response:\n", response, sep="")

    # output = response.split("\n")

    # print("\n\nNewline separated GPT Response in getClusters for ",len(keywords),":\n", output)

    # n = len(output)
    # i = 0
    # while i < n:
    #     if len(output[i]) == 0:
    #         output.pop(i)
    #         n -= 1
    #         i -= 1
    #     i += 1
    # for i in range(len(output)):
    #     output[i] = output[i].split(",")
    #     output[i][0] = keywords[int(output[i][0].strip())]
    #     output[i][1] = keywords[int(output[i][1].strip())]
    #     output[i][2] = output[i][2].strip()
    #     if output[i][2][-1] == "\\":
    #         output[i][2] = output[i][2][:-1]
    #     output[i][2] = float(output[i][2])

    gemini_prompt = "You will be given a primary keyword followed by an array of terms, your Job is to generate a relatedness score between the primary keyword and each of the terms in the range of [0,1]. THE FOLLOWING FORMAT MUST BE STRICTLY FOLLOWED: term of the array, relatedness score between primary keyword and the term SEPERATED BY COMMAS. PUT EACH PAIR DATA IN A NEWLINE. RELATEDNESS SCORE MUST BE FLOAT VALUE ROUNDED TO TWO DECIMALS. DO NOT GENERATE ANY EXTRA TEXT."

    relatedness_scores = []
    model = google_ai.GenerativeModel('gemini-pro')
    print(len(keywords))
    for i in range(len(keywords)-1):
        response = model.generate_content(gemini_prompt + "Primary Keyword : " + keywords[i] + "\nKeywords : " + str(keywords[i+1:]))
        # print(gemini_prompt + "Primary Keyword : " + keywords[i] + "\nKeywords : " + str(keywords[i+1:]))
        processed_response = response.text.split("\n")
        print(i, "-", keywords[i], ":", str(processed_response), "\n")
        for x in processed_response:
            if(not x):
               continue
            x = x.split(",")
            # print([keywords[i], x[0].strip(), x[1].strip()])
            relatedness_scores.append([keywords[i], x[0].strip(), float(x[1].strip())])
        
    print("\n\nGemini Response in getClusters for ",len(keywords),":\n", relatedness_scores)

    output = relatedness_scores

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
        if score >= 0.5:
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

    clusters = list(filter(None, clusters))

    # print("Clusters:\n", clusters)

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

    # fig.show()

    if not os.path.exists("static/images"):
        os.mkdir("static/images")
    fig.write_image("static/images/clusters.png")

    return clusters


def getPercentages_API(data, clusters):
    # print("getPercentages_API:\ndata:", data, "\nclusters:", clusters)
    system_intel = (
        "You will be provided with a set of topics as a benchmark. Your task is to compare the given syllabus against the benchmark topics and determine the percentage of topics that are included directly or indirectly in the syllabus. YOUR RESPONSE MUST ONLY CONTAIN THE NUMBER. THE VALUE MUST BE A WHOLE NUMBER AND SHOULD NOT CONTAIN DECIMALS. DO NOT PROVIDE ANY OTHER INFORMATION OTHER THAN THE VALUE.\nStandard Keywords:"+ str(clusters) + "\n\n"
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
        "Here are some topics as per industry standards and recommended curriculum: "
        + str(clusters)
        + ". You will be given a university syllabus. Your job is to analyze the given syllabus with respect to the standard topics and generate a new syllabus by including all the missing topics. The new syllabus MUST include every single topic from the standards. Mention detailed explanations of topics which are newly added. The new syllabus MUST be in same format (title, content) as the given syllabus. Content part must directly contain a string without any inner objects. Add new title, content pairs to accomodate missing keywords if necessary. YOUR RESPONSE MUST BE IN STRICT JSON FORMAT. NO OTHER STATEMENTS OTHER THAN THE JSON ARRAY MUST BE RETURNED. DO NOT INCLUDE WORDS LIKE json IN THE RESPONSE."
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
            {"role": "user", "content": "Old syllabus:\n" + input},
        ],
    )
    response = result["choices"][0]["message"]["content"]
    # print(course, end="\n\n")
    # print(response, end="\n\n\n")

    return response


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'ieufvbqduviblreiufdxacbcjwdf'


@app.route("/")
def index():
    return render_template("page1.html")

@app.route("/page2")
def page2():
    return render_template("page2.html")


# standard_clusters = [
#     [
#         "Machine Learning",
#         "Supervised Learning",
#         "Unsupervised Learning",
#         "Deep Learning",
#     ],
#     [
#         "Artificial Intelligence",
#         "Problem Solving Techniques",
#         "Logic",
#         "Knowledge Representation",
#         "Planning",
#     ],
#     [
#         "Activation Functions",
#         "Auto-encoders",
#         "Regularization",
#         "Deep Learning Models",
#     ],
#     [
#         "Bayesian Learning",
#         "Decision Trees",
#         "Reinforcement Learning",
#         "Ensemble Methods",
#     ],
#     [
#         "Optimization Techniques",
#         "Machine Learning Strategy",
#         "Responsible Machine Learning",
#         "Machine Learning in Production",
#         "Feeding of Machine Learning Model",
#     ],
# ]


@app.route("/getKeywords", methods=["POST"])
def getKeywords():
    form_data = request.get_json()
    # print("Form data: ", form_data)

    keywords = getKeywords_API(form_data)
    print("\n\nOutput of getKeywords_API:\n",keywords)

    keywords_dict = {}
    for i in range(len(keywords)):
        keywords_dict[i] = keywords[i]
    # print(keywords_dict)
    keywords_json = jsonify(keywords_dict)

    return keywords_json


@app.route("/getClusters", methods=["POST"])
def getClusters():
    keywords = request.get_json()
    # print("Keywords: ", keywords)

    standard_clusters = getClusters_API(keywords)

    session['standard_clusters'] = standard_clusters
    
    print("\n\nOutput of getClusters_API:\n", standard_clusters)

    clusters_dict = {}
    for i in range(len(standard_clusters)):
        clusters_dict[i] = standard_clusters[i]
    # print(clusters_dict)
    clusters_json = jsonify(clusters_dict)

    return clusters_json


@app.route("/getPercentages", methods=["POST"])
def getPercentages():
    form_data = request.get_json()
    # print("Form data: ", form_data)

    standard_clusters = session.get('standard_clusters', [])

    # print("\n\nStandard clusters:\n", standard_clusters)

    percentages = getPercentages_API(form_data, standard_clusters)
    
    print("\n\nOutput of getPercentages_API:\n", percentages)

    percentages_dict = {}
    for i in range(len(percentages)):
        percentages_dict[i] = percentages[i]
    print("Percentages: ", percentages_dict)
    percentages_json = jsonify(percentages_dict)

    return percentages_json


@app.route("/getSuggestions", methods=["POST"])
def getSuggestions():
    form_data = request.get_json()
    # print("Form data: ", form_data)

    standard_clusters = session.get('standard_clusters', [])

    # print("\n\nStandard clusters:\n", standard_clusters)

    response = getSuggestions_API(form_data, standard_clusters)
    
    print("\n\nOutput of getSuggestions_API:\n", response)

    curricula_dict = {"old": form_data, "new": json.loads(response)}
    curricula_json = jsonify(curricula_dict)
    # print("JSON: ", curricula_dict)

    return curricula_json


if __name__ == "__main__":
    app.run()
