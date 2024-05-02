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

function showLoadingAnimation() {
  document.getElementById("loadingOverlay").style.display = "flex";
}

function hideLoadingAnimation() {
  document.getElementById("loadingOverlay").style.display = "none";
}

hideLoadingAnimation();

const submitButton = document.getElementById("submitButton");

submitButton.addEventListener("click", function (event) {
  event.preventDefault();

  showLoadingAnimation();

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
  fetch("/getKeywords", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.text())
    .then((responseData) => {
      hideLoadingAnimation();

      // Handle response
      var keywords = Object.values(JSON.parse(responseData));

      console.log("Keywords Array: " + keywords);

      // document.getElementById("keywords").innerHTML = keywords.join(", ");

      // document.getElementById("section2").style.visibility = "visible";

      showLoadingAnimation();

      // Make POST request
      fetch("/getClusters", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(keywords),
      })
        .then((response) => response.text())
        .then((responseData) => {
          hideLoadingAnimation();

          // Handle response
          const clustersObject = JSON.parse(responseData);

          let clustersString = "";

          for (const key in clustersObject) {
            if (clustersObject.hasOwnProperty(key)) {
              const value = clustersObject[key];
              if (Array.isArray(value) && value.length === 0) {
                delete clustersObject[key];
              } else {
                clustersString += value.join(", ") + "\n";
              }
            }
          }

          // clustersString = JSON.stringify(clustersObject);

          // console.log("Clusters String: " + clustersString);

          // document.getElementById("clusters").textContent = clustersString;

          // document.getElementById("section3").style.visibility = "visible";
          document.getElementById("section4").style.visibility = "visible";
        })
        .catch((error) => {
          hideLoadingAnimation();

          // Handle error
          console.error(error);
        });
    })
    .catch((error) => {
      hideLoadingAnimation();

      // Handle error
      console.error(error);
    });
});

function autoResize(element) {
  element.style.height = "auto";
  element.style.height = element.scrollHeight + "px";
}
