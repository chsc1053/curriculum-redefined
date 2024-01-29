const dataContainer = document.getElementById("dataContainer");
const addDataButton = document.getElementById("addButton");

addDataButton.addEventListener("click", function (e) {
  e.preventDefault();

  const dataSection = document.createElement("div");
  dataSection.classList.add("data-section");

  const removeButton = document.createElement("button");
  removeButton.textContent = "Remove";
  removeButton.classList.add("remove-button");
  removeButton.addEventListener("click", function () {
    dataContainer.removeChild(dataSection);
  });

  dataSection.appendChild(removeButton);

  const titleLabel = document.createElement("label");
  titleLabel.textContent = "Title:";
  const titleInput = document.createElement("input");
  titleInput.classList.add("input-text");
  titleLabel.appendChild(titleInput);

  const syllabusLabel = document.createElement("label");
  syllabusLabel.textContent = "Syllabus:";
  const syllabusTextarea = document.createElement("textarea");
  syllabusTextarea.classList.add("input-textarea");
  syllabusTextarea.addEventListener("input", function () {
    autoResize(syllabusTextarea);
  });
  syllabusLabel.appendChild(syllabusTextarea);

  dataSection.appendChild(titleLabel);
  dataSection.appendChild(syllabusLabel);

  dataContainer.appendChild(dataSection);
});
addDataButton.click();

const submitButton = document.getElementById("submitButton");

submitButton.addEventListener("click", function (event) {
  event.preventDefault();

  // retrieve all the inputs from dataContainer
  const titles = document.querySelectorAll(".input-text");
  const textareas = document.querySelectorAll(".input-textarea");

  // create an array of objects
  const formData = [];
  for (let i = 0; i < titles.length; i++) {
    formData.push({
      title: titles[i].value,
      syllabus: textareas[i].value,
    });
  }

  // Make POST request
  fetch("/getPercentages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.text())
    .then((responseData) => {
      // Handle response
      const percentages = Object.values(JSON.parse(responseData));

      var percentagesArray = percentages.map((str) => parseInt(str));

      console.log("Percentages Array: " + percentagesArray);

      const sum = percentagesArray.reduce((acc, num) => acc + num, 0);
      const average = sum / percentagesArray.length;

      document.getElementById("percentage-average").innerHTML =
        "Curriculum viability: " + average.toFixed(2) + "%";

      document.getElementById("section2").style.visibility = "visible";

      var ctx = document.getElementById("bar-chart").getContext("2d");
      var myChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: [
            "Cluster 1",
            "Cluster 2",
            "Cluster 3",
            "Cluster 4",
            "Cluster 5",
          ],
          datasets: [
            {
              label: "Percentages",
              data: percentagesArray,
              backgroundColor: [
                "rgba(54, 162, 235, 0.2)",
                "rgba(54, 162, 235, 0.2)",
                "rgba(54, 162, 235, 0.2)",
                "rgba(54, 162, 235, 0.2)",
                "rgba(54, 162, 235, 0.2)",
              ],
              borderColor: [
                "rgba(54, 162, 235, 1)",
                "rgba(54, 162, 235, 1)",
                "rgba(54, 162, 235, 1)",
                "rgba(54, 162, 235, 1)",
                "rgba(54, 162, 235, 1)",
              ],
              borderWidth: 1,
            },
          ],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    })
    .catch((error) => {
      // Handle error
      console.error(error);
    });

  // Make POST request
  fetch("/getSuggestions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.text())
    .then((responseData) => {
      // Handle response
      let curriculaArray = JSON.parse(responseData);

      let old_curriculum = JSON.stringify(curriculaArray["old"]);
      console.log("Old Curriculum: " + old_curriculum);
      let new_curriculum = JSON.stringify(curriculaArray["new"]);
      console.log("New Curriculum: " + new_curriculum);

      document.getElementById("section3").style.visibility = "visible";

      const old_curriculum_div = document.getElementById("old-curriculum");
      curriculaArray["old"].forEach((item) => {
        const div = document.createElement("div");
        const titleElement = document.createElement("h4");
        const contentElement = document.createElement("p");

        titleElement.textContent = item.title;
        contentElement.textContent = item.syllabus;

        div.appendChild(titleElement);
        div.appendChild(contentElement);

        old_curriculum_div.appendChild(div);
      });

      const new_curriculum_div = document.getElementById("new-curriculum");
      curriculaArray["new"].forEach((item) => {
        const div = document.createElement("div");
        const titleElement = document.createElement("h4");
        const contentElement = document.createElement("p");

        titleElement.textContent = item.title;
        contentElement.textContent = item.content;

        div.appendChild(titleElement);
        div.appendChild(contentElement);

        new_curriculum_div.appendChild(div);
      });
    })
    .catch((error) => {
      // Handle error
      console.error(erro0r);
    });

  // Make POST request
  fetch("/getClusters", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.text())
    .then((responseData) => {
      // Handle response
      let clustersArray = JSON.parse(responseData);
      
    })
    .catch((error) => {
      // Handle error
      console.error(error);
    });
});

function autoResize(element) {
  element.style.height = "auto";
  element.style.height = element.scrollHeight + "px";
}
