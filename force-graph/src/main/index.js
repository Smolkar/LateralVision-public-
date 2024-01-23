// import Highcharts from "highcharts";
// import HighchartsMore from "highcharts/highcharts-more"; // Optional, if you need additional chart types
// import HighchartsAccessibility from "highcharts/modules/accessibility"; // Optional, if you need accessibility features
// import HighchartsExporting from "highcharts/modules/exporting"; // Optional, if you need exporting functionality
import DirectedGraph from "./scripts/directedgraph";
import "./style.css";
import "./dashboard.css";

// const chartContainer = document.getElementById("chart-container");

// Create the Highcharts chart object
// Highcharts.chart(chartContainer, {
//   navigator: {
//     enabled: true,
//     height: 50,
//     xAxis: {
//       type: "datetime",
//       labels: {
//         format: "{value:%H:%M:%S}",
//       },
//     },
//     series: [
//       {
//         data: [1, 2, 3, 4, 5, 6, 7, 8, 9],
//         type: "line",
//       },
//     ],
//   },
//   // Add your chart options here
//   handles: {
//     backgroundColor: "#fff",
//     borderColor: "#ccc",
//     borderWidth: 1,
//     height: 10,
//     width: 10,
//     symbols: ["square", "square"],
//     enabled: true,
//   },
// });

document.addEventListener("DOMContentLoaded", function () {
  const uploadTrigger = document.getElementById("upload-trigger");
  const uploadPopup = document.getElementById("upload-popup");
  const closePopup = document.getElementById("close-popup");
  const fileInput = document.getElementById("file-input");
  const fileInfo = document.getElementById("file-info");
  uploadTrigger.addEventListener("click", function () {
    uploadPopup.style.display = "block";
  });

  closePopup.addEventListener("click", function () {
    uploadPopup.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target == uploadPopup) {
      uploadPopup.style.display = "none";
    }
  });
  fileInput.addEventListener("change", (event) => {
    const selectedFile = event.target.files[0];
    const fileName = selectedFile ? selectedFile.name : "No file selected";
    const fileSize = selectedFile ? selectedFile.size : "N/A";
    const fileType = selectedFile ? selectedFile.type : "N/A";
    const fileCreationDate = selectedFile
      ? selectedFile.lastModifiedDate
      : "N/A";

    fileInfo.innerHTML = `
      <p>Selected file: ${fileName}</p>
      <p>Type: ${fileType}</p>
      <p>Size: ${fileSize} bytes</p>
      <p>Created on: ${fileCreationDate}</p>
    `;
  });
  document.getElementById("remove-nodes").addEventListener("click", () => {
    console.log("Remove nodes");
    // Add functionality to remove nodes
  });

  document
    .getElementById("restart-simulation")
    .addEventListener("click", () => {
      console.log("Restart simulation");
      // Add functionality to restart the simulation
    });

  document.getElementById("start-time").addEventListener("change", (event) => {
    console.log(`Start time: ${event.target.value}`);
    // Add functionality to handle start time change
  });

  document.getElementById("end-time").addEventListener("change", (event) => {
    console.log(`End time: ${event.target.value}`);
    // Add functionality to handle end time change
  });
});
document.getElementById("dashboard").addEventListener("click", () => {
  window.location.href = "dashboard.html";
});
function getRandomData() {
  return fetch("http://127.0.0.1:5000/LatVis/connections")
    .then((response) => response.json())
    .then((data) => {
      const graphData = {
        nodes: data.nodes,
        relationships: data.relationships,
      };

      return graphData;
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

let b = new DirectedGraph(".content", {
  arrowSize: 7.5,
  relationshipWidth: 2,
  nodeRadius: 30,
  nodeCaption: true,
  relationshipCaption: false,
  icons: {
    Device: "fas fa-desktop",
    User: "fas fa-street-view",
    Domain: "fas fa-solid fa-network-wired",
  },
  colors: { Device: "#1A3A6D", User: "#FAA21C", Domain: "#14111C" },
  sizes: { Device: 30, User: 20, Domain: 0 },
});

getRandomData().then((graphData) => {
  b.drawGraph(graphData);
});
