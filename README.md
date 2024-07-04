# Curriculum Redefined

In the age of Industry 4.0, the field of computer science education faces significant challenges in keeping pace with emerging technologies such as AI, IoT, Blockchain, and Data Sciences. "Curriculum Redefined" aims to evaluate existing curricula in AI & ML, Data Sciences, and Cyber Security programs. This evaluation assesses their alignment with industry demands by exploring institutions, courses, student outcomes, and curriculum impact. Input is gathered from alumni, recruiters, and educators to bridge curriculum gaps and empower educational institutions to better prepare students for the tech-driven job market. Practical recommendations are offered for curriculum improvement based on these findings.

## Project Description

"Curriculum Redefined" is a Python-based project that utilizes the Flask framework for web page display and integrates OpenAI's GPT API. The project consists of a website with two main pages:

1. **Standards Input Page:** Users input standards which include AICTE recommended curriculum, industry-demanded skills sourced from industry professionals, alumni feedback, experienced educators' insights, and relevant research articles.
2. **Curriculum Comparison Page:** Users input specific university curricula to compare against the standards entered in the first page. The page displays:

   - **Viability Score:** A score indicating how well the university curriculum aligns with the input standards.
   - **Modified Curriculum:** Recommendations for changes to the university curriculum, including incorporation of missing topics and adjustments to better meet current industry demands.

Key functionalities implemented through the GPT API include:

- **Keyword Extraction:** Identifying key topics from input standards and university curriculum.
- **Topic Clustering:** Grouping related topics for deeper analysis.
- **Curriculum Comparison:** Assessing the alignment between university curriculum and industry standards to derive the viability score and recommend modifications.

## Features

- **Python-based:** Utilizes Python for backend processing and integration with OpenAI's GPT API.
- **Flask Framework:** Provides a lightweight yet powerful web framework for rendering the project's two main web pages.
- **GPT Integration:** Leverages OpenAI's GPT API for natural language processing tasks such as keyword extraction, clustering, and curriculum comparison.
- **User-friendly Interface:** Designed to be intuitive, with clear prompts and easy-to-understand outputs for users.

## Getting Started

To get started with "Curriculum Redefined", follow these steps:

1. **Clone the Repository:**

   ```
   git clone https://github.com/chsc1053/curriculum-redefined.git
   cd curriculum-redefined
   ```
2. **Install Dependencies:**

   ```
   pip install openai
   ```
3. **Run the Application:**

   ```
   python app.py
   ```
4. **Open Your Web Browser:**
   Open your web browser and go to `http://localhost:5000` to access the application.
