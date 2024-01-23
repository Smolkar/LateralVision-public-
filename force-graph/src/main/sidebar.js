const removeNodesButton = document.getElementById("remove-nodes");
removeNodesButton.addEventListener("click", () => {
  console.log("Remove nodes");
  // Add functionality to remove nodes
});

const restartSimulationButton = document.getElementById("restart-simulation");
restartSimulationButton.addEventListener("click", () => {
  console.log("Restart simulation");
  // Add functionality to restart the simulation
});

const startTimeInput = document.getElementById("start-time");
startTimeInput.addEventListener("change", (event) => {
  console.log(`Start time: ${event.target.value}`);
  // Add functionality to handle start time change
});

const endTimeInput = document.getElementById("end-time");
endTimeInput.addEventListener("change", (event) => {
  console.log(`End time: ${event.target.value}`);
  // Add functionality to handle end time change
});
