import "@fortawesome/fontawesome-free/js/fontawesome";
import "@fortawesome/fontawesome-free/js/solid";
import "@fortawesome/fontawesome-free/js/regular";
import "@fortawesome/fontawesome-free/js/brands";
import * as d3 from "d3";
// import * as tool from "d3-context-menu";

export function getMenuDomain(nodes) {
  // Check if any frame is visible
  const anyFrameVisible = Array.from(document.querySelectorAll(".frame")).some(
    (frame) => frame.getAttribute("data-visible") === "true"
  );

  const toggleDomainsTitle = anyFrameVisible ? "Remove Domains" : "Add Domains";

  return [
    {
      title: toggleDomainsTitle,
      action: function (d, i) {
        toggleDomains();

        console.log("Action 1 clicked:", d, i);
      },
    },
    {
      title: "Action 2",
      action: function (d, i) {
        console.log("Action 2 clicked:", d, i);
      },
    },
    { divider: true },
    {
      title: "Submenu",
      children: [
        {
          title: "Submenu Action 1",
          action: function (d, i) {
            console.log("Submenu Action 1 clicked:", d, i);
          },
        },
        {
          title: "Submenu Action 2",
          action: function (d, i) {
            console.log("Submenu Action 2 clicked:", d, i);
          },
        },
      ],
    },
  ];
  function toggleDomains() {
    // Get all the unique domains
    const uniqueDomains = Array.from(
      new Set(nodes.map((node) => node.properties.domain))
    );

    // Check if any frame is visible
    const anyFrameVisible = Array.from(
      document.querySelectorAll(".frame")
    ).some((frame) => frame.getAttribute("data-visible") === "true");
    console.log(anyFrameVisible);
    uniqueDomains.forEach((domain, index) => {
      const frameId = `frame-${index}`;
      const frame = document.getElementById(frameId);
      if (!frame) {
        // updateFrame(frameId, domain, nodes);
      } else {
        if (anyFrameVisible) {
          frame.style.display = "none";
          frame.setAttribute("data-visible", "false");
        } else {
          frame.style.display = "";
          frame.setAttribute("data-visible", "true");
        }
      }
      const nodesForDomainInSimulation = d3.selectAll(
        `g.node[data-domain="${domain}"]`
      );
      nodesForDomainInSimulation.style(
        "display",
        anyFrameVisible ? "none" : "block"
      );
    });

    // Re-initialize the simulation with the updated nodes array
    //initSimulation();
  }
}
