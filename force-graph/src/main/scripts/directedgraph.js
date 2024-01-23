import "@fortawesome/fontawesome-free/js/brands";
import "@fortawesome/fontawesome-free/js/fontawesome";
import "@fortawesome/fontawesome-free/js/regular";
import "@fortawesome/fontawesome-free/js/solid";
import * as d3 from "d3";
import * as tool from "d3-context-menu";
import "d3-context-menu/css/d3-context-menu.css";
import { ArcArrow } from "./components/links/ArcArrow";
import { LoopArrow } from "./components/links/LoopArrow";
import { StraightArrow } from "./components/links/StraightArrow";
import { getMenuDomain } from "./components/menus/MenuDomain";

export default function DirectedGraph(_selector, _options) {
  let data = {},
    nodes = [],
    relationships = [],
    node,
    relationship,
    // eslint-disable-next-line no-unused-vars
    relationshipOutline,
    relationshipOverlay,
    relationshipText,
    selector,
    simulation,
    svg,
    g,
    svgNodes,
    svgRelationships,
    classes2colors = {},
    numClasses = 0;

  let options = {
    arrowSize: 7.5,
    relationshipWidth: 1.5,
    nodeRadius: 23,
    zoomScale: [0.1, 10],
    colors: {},
    icons: {},
    nodeCaption: true,
    relationshipCaption: true,
    sizes: {},
  };

  // ----- init

  init(_selector, _options);

  //---

  function init(_selector, _options) {
    selector = _selector;
    options = { ...options, ..._options };

    appendGraph(d3.select(selector));

    simulation = initSimulation();
  }

  function drawGraph(_data) {
    data = _data;
    showData(data);
  }

  // components/graph
  function findNode(id, nodes) {
    return nodes.find((node) => node.id === id);
  }

  function showData(d) {
    mapData(d);
    updateContent(d.nodes, d.relationships);
  }

  function mapData(d) {
    d.relationships = d.relationships.map((r) => {
      const source = findNode(r.startNode, d.nodes);
      const target = findNode(r.endNode, d.nodes);

      return {
        ...r,
        source,
        target,
        naturalAngle: 0,
        isLoop() {
          return this.source === this.target;
        },
      };
    });
  }
  function class2icon(cls) {
    return options.icons[cls];
  }

  function class2color(cls) {
    let color = options.colors[cls] || classes2colors[cls];

    if (!color) {
      color = randomColors()[numClasses % randomColors().length];
      classes2colors[cls] = color;
      numClasses++;
    }

    return color;
  }

  // eslint-disable-next-line no-unused-vars
  function class2darkenColor(cls) {
    return d3.rgb(class2color(cls)).darker(1);
  }
  function class2size(cls) {
    if (options.sizes && options.sizes[cls]) {
      return options.sizes[cls];
    } else {
      return options.radius; // default size
    }
  }
  function randomColors() {
    return [
      "rgb(255, 187, 120)",
      "rgb(148, 103, 189)",
      "rgb(174, 199, 232)",
      "rgb(31, 119, 180)",
      "rgb(152, 223, 138)",
      "rgb(84, 202, 116)",
      "rgb(227, 67, 67)",
      "rgb(121, 110, 255)",
      "rgb(242, 246, 251)",
    ];
  }

  //---

  function zoom() {
    return d3.zoom().scaleExtent(options.zoomScale).on("zoom", zoomed);
  }

  // eslint-disable-next-line no-unused-vars
  function transform() {
    return d3.zoomIdentity.translate(0, 0).scale(2);
  }

  function updateContent(n, r) {
    updateRelationships(r);
    updateNodes(n);

    simulation.nodes(nodes);
    simulation.force("link").links(relationships);
  }

  // ---utils

  class NodePair {
    constructor(node1, node2) {
      this.relationships = [];

      if (node1.id < node2.id) {
        this._nodeA = node1;
        this._nodeB = node2;
      } else {
        this._nodeA = node2;
        this._nodeB = node1;
      }
    }

    get nodeA() {
      return this._nodeA;
    }

    get nodeB() {
      return this._nodeB;
    }

    isLoop() {
      return this.nodeA === this.nodeB;
    }

    toString() {
      return `${this.nodeA.id}:${this.nodeB.id}`;
    }
  }

  //---utils

  function appendGraph(container) {
    svg = container
      .append("svg")
      .attr("width", "100%")
      .attr("height", "100%")
      .attr("class", "directed-graph")
      .call(zoom())
      .on("dblclick.zoom", null);

    g = svg.append("g").attr("width", "100%").attr("height", "100%");

    svgRelationships = g.append("g").attr("class", "relationships");

    svgNodes = g.append("g").attr("class", "nodes");
  }
  function calculateDistance(link) {
    const minLength = 0.1;
    const lengthMultiplier = 0.1;
    const sourceRadius = class2size(link.source.labels[0]);
    console.log(link.source.labels[0]);
    const targetRadius = class2size(link.target.labels[0]);
    const avgRadius = (sourceRadius + targetRadius) / 1;
    const sizeDifferenceFactor =
      1 +
      Math.abs(sourceRadius - targetRadius) /
        Math.min(sourceRadius, targetRadius);
    const maxLength = 200;
    const length = Math.min(
      maxLength,
      minLength + (avgRadius * lengthMultiplier) / sizeDifferenceFactor
    );
    return length;
  }
  // function avoidEdgeOverlap(alpha) {
  //   const padding = 1000;
  //   return function (d) {
  //     const nodeBBox = {
  //       x1: d.x - options.nodeRadius - padding,
  //       y1: d.y - options.nodeRadius - padding,
  //       x2: d.x + options.nodeRadius + padding,
  //       y2: d.y + options.nodeRadius + padding,
  //     };
  //     d3.selectAll("line").each(function (l) {
  //       const sourceBBox = {
  //         x1: l.source.x - options.nodeRadius - padding,
  //         y1: l.source.y - options.nodeRadius - padding,
  //         x2: l.source.x + options.nodeRadius + padding,
  //         y2: l.source.y + options.nodeRadius + padding,
  //       };
  //       const targetBBox = {
  //         x1: l.target.x - options.nodeRadius - padding,
  //         y1: l.target.y - options.nodeRadius - padding,
  //         x2: l.target.x + options.nodeRadius + padding,
  //         y2: l.target.y + options.nodeRadius + padding,
  //       };
  //       if (
  //         bboxOverlap(nodeBBox, sourceBBox) ||
  //         bboxOverlap(nodeBBox, targetBBox)
  //       ) {
  //         const dx = l.target.x - l.source.x;
  //         const dy = l.target.y - l.source.y;
  //         const length = Math.sqrt(dx * dx + dy * dy);
  //         const moveDist = (alpha * (length - calculateDistance(l))) / 2;
  //         d.x += moveDist * (dx / length);
  //         d.y += moveDist * (dy / length);
  //       }
  //     });
  //   };
  // }

  // function bboxOverlap(box1, box2) {
  //   return (
  //     box1.x1 <= box2.x2 &&
  //     box1.x2 >= box2.x1 &&
  //     box1.y1 <= box2.y2 &&
  //     box1.y2 >= box2.y1
  //   );
  // }
  function initSimulation() {
    return d3
      .forceSimulation()
      .velocityDecay(0.8)
      .force(
        "collide",
        d3
          .forceCollide()
          .radius(function () {
            return options.nodeRadius * 3;
          })
          .iterations(16)
          .strength(0.9)
      )
      .force(
        "link",
        d3
          .forceLink()
          .id(function (d) {
            return d.id;
          })
          .distance(() => {
            return 1.5;
          })
          .strength(1)
      )
      .force(
        "center",
        d3.forceCenter(
          svg.node().parentElement.parentElement.clientWidth / 2,
          svg.node().parentElement.parentElement.clientHeight / 2
        )
      )
      .force(
        "charge",
        d3
          .forceManyBody()
          .strength(-3000) // Increase the strength of repulsive forces
          .distanceMax(200)
          .distanceMin(options.nodeRadius * 20)
      )
      .force("x", d3.forceX().strength(0.1))
      .force("y", d3.forceY().strength(0.01)) // Lower y-strength to reduce vertical movement
      .alphaDecay(0.03)
      .alphaTarget(0.5)
      .on("tick", function () {
        tick();
      });
  }
  function layoutRelationships() {
    const nodePairs = groupedRelationships();
    computeGeometryForNonLoopArrows(nodePairs);
    distributeAnglesForLoopArrows(nodePairs, data.relationships);

    for (const nodePair of nodePairs) {
      for (const relationship of nodePair.relationships) {
        delete relationship.arrow;
      }

      const middleRelationshipIndex = (nodePair.relationships.length - 1) / 2;
      const defaultDeflectionStep = 30;
      const maximumTotalDeflection = 100;
      const numberOfSteps = nodePair.relationships.length - 1;
      const totalDeflection = defaultDeflectionStep * numberOfSteps;

      const deflectionStep =
        totalDeflection > maximumTotalDeflection
          ? maximumTotalDeflection / numberOfSteps
          : defaultDeflectionStep;

      for (let i = 0; i < nodePair.relationships.length; i++) {
        const relationship = nodePair.relationships[i];
        const nodeRadius = options.nodeRadius;
        const shaftWidth = options.relationshipWidth;
        const headWidth = options.arrowSize;
        const headHeight = headWidth;

        if (nodePair.isLoop()) {
          relationship.arrow = new LoopArrow(
            nodeRadius,
            40,
            defaultDeflectionStep,
            shaftWidth,
            headWidth,
            headHeight,
            relationship.captionHeight || 11
          );
        } else {
          if (i === middleRelationshipIndex) {
            relationship.arrow = new StraightArrow(
              nodeRadius,
              nodeRadius,
              relationship.centreDistance,
              shaftWidth,
              headWidth,
              headHeight,
              relationship.captionLayout || "external"
            );
          } else {
            let deflection = deflectionStep * (i - middleRelationshipIndex);

            if (nodePair.nodeA !== relationship.source) {
              deflection *= -1;
            }

            relationship.arrow = new ArcArrow(
              nodeRadius,
              nodeRadius,
              relationship.centreDistance,
              deflection,
              shaftWidth,
              headWidth,
              headHeight,
              relationship.captionLayout || "external"
            );
          }
        }
      }
    }

    return nodePairs;
  }

  //FIXME:DONT HAVE TO REPEAT
  function values(obj) {
    return Object.values(obj);
  }

  function groupedRelationships() {
    const groups = {};
    for (const relationship of Array.from(data.relationships)) {
      let nodePair = new NodePair(relationship.source, relationship.target);
      nodePair = groups[nodePair] != null ? groups[nodePair] : nodePair;
      nodePair.relationships.push(relationship);
      groups[nodePair] = nodePair;
    }
    return values(groups);
  }

  function computeGeometryForNonLoopArrows(nodePairs) {
    const square = (distance) => distance * distance;

    const updatedNodePairs = nodePairs.map((nodePair) => {
      if (!nodePair.isLoop()) {
        const dx = nodePair.nodeA.x - nodePair.nodeB.x;
        const dy = nodePair.nodeA.y - nodePair.nodeB.y;
        const angle = ((Math.atan2(dy, dx) / Math.PI) * 180 + 360) % 360;
        const centreDistance = Math.sqrt(square(dx) + square(dy));

        nodePair.relationships.forEach((relationship) => {
          relationship.naturalAngle =
            relationship.target === nodePair.nodeA
              ? (angle + 180) % 360
              : angle;
          relationship.centreDistance = centreDistance;
        });
      }

      return nodePair;
    });

    const nodePairsWithoutLoops = updatedNodePairs.filter(
      (nodePair) => !nodePair.isLoop()
    );

    distributeAnglesForLoopArrows(nodePairsWithoutLoops, data.relationships);

    return updatedNodePairs;
  }
  function distributeAnglesForLoopArrows(nodePairs, relationships) {
    return nodePairs.map((nodePair) => {
      if (nodePair.isLoop()) {
        let angles = [];
        const node = nodePair.nodeA;

        relationships.forEach((relationship) => {
          if (!relationship.isLoop()) {
            if (relationship.source === node) {
              angles.push(relationship.naturalAngle);
            }
            if (relationship.target === node) {
              angles.push(relationship.naturalAngle + 180);
            }
          }
        });

        angles = angles.map((a) => (a + 360) % 360).sort((a, b) => a - b);
        let separation;

        if (angles.length > 0) {
          let biggestGap = {
            start: 0,
            end: 0,
          };

          for (let i = 0; i < angles.length; i++) {
            const angle = angles[i];
            const start = angle;
            const end =
              i === angles.length - 1 ? angles[0] + 360 : angles[i + 1];

            if (end - start > biggestGap.end - biggestGap.start) {
              biggestGap.start = start;
              biggestGap.end = end;
            }
          }

          separation =
            (biggestGap.end - biggestGap.start) /
            (nodePair.relationships.length + 1);

          nodePair.relationships.forEach((relationship, i) => {
            relationship.naturalAngle =
              (biggestGap.start + (i + 1) * separation - 90) % 360;
          });
        } else {
          separation = 360 / nodePair.relationships.length;

          nodePair.relationships.forEach((relationship, i) => {
            relationship.naturalAngle = i * separation;
          });
        }

        return nodePair;
      } else {
        return undefined;
      }
    });
  }
  //--- visulize or Graph component

  function updateRelationships(r, startDate = null, endDate = null) {
    let relationships = r;
    if (startDate && endDate) {
      relationships = relationships.filter((relationship) => {
        const relationshipDate = new Date(relationship.properties.datetime);
        return relationshipDate >= startDate && relationshipDate <= endDate;
      });
    } else if (startDate) {
      relationships = relationships.filter((relationship) => {
        const relationshipDate = new Date(relationship.properties.datetime);
        return relationshipDate >= startDate;
      });
    } else if (endDate) {
      relationships = relationships.filter((relationship) => {
        const relationshipDate = new Date(relationship.properties.datetime);
        return relationshipDate <= endDate;
      });
    }
    relationships = relationships.filter((d) => d.type !== "Contains_Device");

    // Update relationships in graph
    relationship = svgRelationships
      .selectAll(".relationship")
      .data(relationships, (d) => d.id);

    relationship.exit().remove();

    // Enter new relationships and merge with existing ones
    relationship = relationship
      .enter()
      .append("g")
      .attr("class", "relationship")
      .merge(relationship)
      .on("contextmenu", () => {
        d3.event.preventDefault();
        tool();
      });
    appendOverlayToRelationship(relationship);
    appendTextToRelationship(relationship);
    appendOutlineToRelationship(relationship);
  }

  function appendOutlineToRelationship(n) {
    relationshipOutline = n
      .selectAll(".outline")
      .data((d) => [d])
      .join(
        (enter) =>
          enter
            .append("path")
            .attr("fill", "#9a9a9a")
            .attr("stroke", "#a5abb6"),
        (update) => update,
        (exit) => exit.remove()
      )
      .attr("class", "outline");
  }

  function appendOverlayToRelationship(n) {
    relationshipOverlay = n
      .selectAll(".overlay")
      .data((d) => [d])
      .join(
        (enter) => enter.append("path"),
        (update) => update,
        (exit) => exit.remove()
      )
      .attr("class", "overlay")
      .attr("fill", () => {
        // TODO: Add overlaycolor as an option
      });
  }

  function appendTextToRelationship(n) {
    relationshipText = n
      .selectAll(".text")
      .data((d) => [d])
      .join(
        (enter) =>
          enter
            .append("text")
            .attr("class", "text")
            .attr("fill", "#000000")
            .attr("font-size", "7.5px")
            .attr("font-weight", 600)
            .attr("text-anchor", "middle"),
        (update) => update,
        (exit) => exit.remove()
      )
      .text((d) => {
        return options.relationshipCaption ? d.type : ""; // TODO: Choose what to show
      });
  }

  //---

  function updateNodes(n) {
    console.log(n);
    nodes = n.filter((d) => d.labels[0] !== "Domain");
    // nodes = n;
    node = svgNodes.selectAll(".node").data(nodes, (d) => {
      return d.id;
    });

    const menu = [
      {
        title: (d) => `Computer: ${d.properties.name}`,
      },
      { title: "Ip_adress: 192.168.56.1" },
      {
        title: "More Info",
        action: () => {},
        disabled: false,
      },
      { divider: true },
      {
        title: "Queries",
        children: [
          {
            title: "Show logons",
            action: () => {
              // const frameId = `frame_${d.properties.domain}`;
              // const targetDomain = d.properties.domain;
            },
          },
          {
            title: "Show attempts",
            action: (d) => {
              console.log("You have clicked the second item!");
              console.log("The data for this circle is:", d);
            },
          },
        ],
      },
    ];

    node.exit().remove();

    let nodeEnter = appendNodeToGraph();
    node = nodeEnter.merge(node).attr("r", (d) => class2size(d.labels[0]));

    node.on("contextmenu", (d) => {
      d3.event.preventDefault();
      tool(menu)(d);
    });

    appendRingToNode(node);
    appendOutlineToNode(node);
    appendTextUnderNode(node);
    appendIconToNode(node);
  }

  function appendNodeToGraph() {
    return (
      node

        .enter()
        // .filter((d) => d.labels[0] !== "Domain") // Filter out nodes with "Domain" as the first label

        .append("g")

        .attr("class", () => {
          // Add a class based on the label
          // return "node " + (d.labels[0] === "Domain" ? "domain-node" : "");
          return "node";
        })
        .on("click", () => {
          //TODO: Features will be added
        })
        .on("dblclick", () => {
          //TODO: Features will be added
        })
        .call(
          d3
            .drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded)
        )
    );
  }

  function appendOutlineToNode(node) {
    let n = node.selectAll(".noutline").data((d) => [d]);

    n.exit().remove();

    let nenter = n
      .enter()
      .append("circle")
      .attr("class", "noutline")
      .attr("r", (d) => class2size(d.labels[0]));

    let nmerge = nenter.merge(n);

    nmerge
      .style("fill", (d) => class2color(d.labels[0]))
      .style("stroke", (d) => {
        let originalColor = d3.color(class2color(d.labels[0]));
        return originalColor.darker(1); // You can adjust the value (1) to control the dimming intensity
      });
  }

  function appendRingToNode(node) {
    let n = node.selectAll(".ring").data((d) => {
      return [d];
    });

    n.exit().remove();

    let nenter = n
      .enter()
      .append("circle")
      .attr("class", "ring")
      .attr("r", (d) => class2size(d.labels[0]) + 5) // Add 5 to the node size for the ring radius

      .attr("fill", "none") // Make the fill transparent
      .attr("stroke-width", 2); // Set the stroke width

    nenter.merge(n).attr("stroke", (d) => {
      // You can set the ring color here or provide an option for users to choose
      return class2color(d.labels[0]);
    });
  }

  function appendTextUnderNode(node) {
    var n = node.selectAll(".nodetext").data(function (d) {
      return [d];
    });

    n.exit().remove();

    var nenter = n
      .enter()
      .append("text")
      .attr("class", "nodetext")
      .attr("pointer-events", "none")
      .attr("text-anchor", "middle")
      .attr("font-size", (d) => class2size(d.labels[0]) * 0.1) // You can adjust the factor (0.6) for the desired font size
      .attr("y", (d) => {
        return `${
          class2size(d.labels[0]) + class2size(d.labels[0]) * 0.6 + 5
        }px`;
      });

    nenter.merge(n).html(function (d) {
      return options.nodeCaption ? `${d.properties["name"]}` : "";
    });
  }

  // function appendImageToNode(node) {
  //   const squareCoordinates = getInscribedSquareCoordinates(options.nodeRadius);

  //   var n = node.selectAll(".image").data(function (d) {
  //     return [d];
  //   });

  //   n.exit().remove();

  //   var nenter = n.enter().append("image").attr("class", "image");

  //   // TODO: Adjust position to node size
  //   nenter
  //     .merge(n)
  //     .attr("xlink:href", function (d) {
  //       if (options.images[d.labels[0]] !== undefined)
  //         properties.images[d.labels[0]];
  //     })
  //     .attr("height", function () {
  //       return `${squareCoordinates.height}px`;
  //     })
  //     .attr("x", function () {
  //       return `${squareCoordinates.x}px`;
  //     })
  //     .attr("y", function () {
  //       return `${squareCoordinates.y}px`;
  //     })
  //     .attr("width", function () {
  //       return `${squareCoordinates.widht}px`;
  //     });
  // }

  function appendIconToNode(node) {
    var n = node.selectAll(".icon").data(function (d) {
      return [d];
    });

    n.exit().remove();

    var nenter = n.enter().append("svg");

    nenter
      .merge(n)
      .attr("class", function (d) {
        return `icon ${class2icon(d.labels[0]) || ""}`;
      })
      .attr("height", function (d) {
        const squareCoordinates = getInscribedSquareCoordinates(
          class2size(d.labels[0])
        );
        return `${squareCoordinates.height / 1.5}px`;
      })
      .attr("x", function (d) {
        const squareCoordinates = getInscribedSquareCoordinates(
          class2size(d.labels[0])
        );
        return `${squareCoordinates.x / 1.5}px`;
      })
      .attr("y", function (d) {
        const squareCoordinates = getInscribedSquareCoordinates(
          class2size(d.labels[0])
        );
        return `${squareCoordinates.y / 1.5}px`;
      })
      .attr("width", function (d) {
        const squareCoordinates = getInscribedSquareCoordinates(
          class2size(d.labels[0])
        );
        return `${squareCoordinates.width / 1.5}px`;
      });
  }

  function getInscribedSquareCoordinates(radius) {
    let hypotenuse = (radius * radius) / 2;
    let leg = Math.sqrt(hypotenuse);

    return { y: -leg, x: -leg, width: leg * 2, height: leg * 2 };
  }
  //----visulization

  function dragEnded(d) {
    if (!d3.event.active) simulation.alphaTarget(0);

    d.fx = null;
    d.fy = null;
  }

  function dragged(d) {
    stickNode(d);
  }

  function stickNode(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function dragStarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();

    d.fx = d.x;
    d.fy = d.y;
  }

  function zoomed() {
    g.attr("transform", d3.event.transform);
  }

  //___tick
  // eslint-disable-next-line no-unused-vars
  function createFrames(nodes) {
    const frames = [];
    const uniqueDomains = Array.from(
      new Set(nodes.map((node) => node.properties.domain))
    );
    uniqueDomains.forEach((domain, index) => {
      updateFrame(`frame-${index}`, domain, nodes);
      frames.push(index);
    });
    separateOverlappingFrames(frames, nodes);
  }
  function tick() {
    tickNodes();
    tickRelationships();
    createFrames(nodes);
  }

  function tickNodes() {
    // Check if 'node' is defined and visible before using it

    if (typeof node !== "undefined" && node.style.display !== "none") {
      node.attr("transform", (d) => {
        return `translate(${d.x}, ${d.y})`;
      });
    }
  }

  function tickRelationships() {
    // Check if 'relationship' is defined before using it
    if (typeof relationship !== "undefined") {
      //TODO: add multiple cases

      layoutRelationships();

      relationship.attr("transform", (d) => {
        return `translate(${d.source.x} ${d.source.y}) rotate(${
          d.naturalAngle + 180
        })`;
      });

      tickRelationshipsTexts();
      tickRelationshipsOutlines();
      tickRelationshipsOverlays();
    }
  }
  function distance(x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    return Math.sqrt(dx * dx + dy * dy);
  }

  function createNodesByDomain(nodes) {
    return nodes.reduce((acc, node) => {
      const domain = node.properties.domain;
      if (!acc[domain]) {
        acc[domain] = [];
      }
      acc[domain].push(node.id);
      return acc;
    }, {});
  }

  function framesOverlap(frame1, frame2, nodesByDomain) {
    const nodes1 = nodesByDomain[frame1.targetDomain];
    const nodes2 = nodesByDomain[frame2.targetDomain];

    if (!nodes1 || !nodes2) {
      return false;
    }

    // Use Array.prototype.some() method to check for overlap
    return nodes1.some((node1Id) => nodes2.includes(node1Id));
  }
  function getTextSize(radius, scaleFactor = 0.1, minimumFontSize = 12) {
    return Math.max(minimumFontSize, radius * scaleFactor);
  }
  function separateOverlappingFrames(frameDomains, nodes) {
    const forceStrength = 100000000;
    const timeStep = 0.5;
    const maxIterations = 10000;
    let iteration = 0;
    let shouldContinue = true;

    // Extract frame data from DOM
    const framesData = frameDomains
      .map((domain) => {
        const frame = svgNodes.select("#frame-" + domain);

        // Check if the frame exists
        if (!frame.empty()) {
          const x = parseFloat(frame.attr("cx"));
          const y = parseFloat(frame.attr("cy"));
          const radius = parseFloat(frame.attr("r"));

          return {
            id: "frame-" + domain,
            domain: domain,
            x: x,
            y: y,
            radius: radius,
            vx: 0,
            vy: 0,
          };
        }
      })
      .filter((frame) => frame); // Filter out undefined values

    while (shouldContinue && iteration < maxIterations) {
      // Update the frames' positions based on their velocities
      updateFramesPosition(framesData, timeStep);

      // Apply the separation force to overlapping frames
      applySeparationForce(framesData, nodes, forceStrength);
      const nodesByDomain = createNodesByDomain(nodes);

      // Check if there are still overlapping frames
      shouldContinue = framesData.some((frame1, i) => {
        return framesData.some((frame2, j) => {
          return i !== j && framesOverlap(frame1, frame2, nodesByDomain);
        });
      });

      iteration++;
    }
  }

  function applySeparationForce(frames, nodes, forceStrength) {
    const padding = 10;
    const frameCount = frames.length;

    for (let i = 0; i < frameCount; i++) {
      const frame1 = frames[i];

      for (let j = i + 1; j < frameCount; j++) {
        const frame2 = frames[j];

        if (framesOverlap(frame1, frame2, nodes)) {
          const dx = frame2.x - frame1.x;
          const dy = frame2.y - frame1.y;
          const dist = distance(frame1.x, frame1.y, frame2.x, frame2.y);
          const overlap = frame1.radius + frame2.radius + padding - dist;

          if (overlap > 0) {
            const force = (forceStrength * overlap) / dist;
            const forceX = dx * force;
            const forceY = dy * force;

            frame1.vx -= forceX;
            frame1.vy -= forceY;
            frame2.vx += forceX;
            frame2.vy += forceY;
          }
        }
      }
    }
  }
  function getRandomColor() {
    const min = 0;
    const max = 170;

    const getRandomComponent = () =>
      Math.floor(Math.random() * (max - min + 1) + min);

    const r = getRandomComponent();
    const g = getRandomComponent();
    const b = getRandomComponent();

    return `rgb(${r}, ${g}, ${b})`;
  }
  function updateFramesPosition(frames, timeStep) {
    for (let i = 0; i < frames.length; i++) {
      const frame = frames[i];
      frame.x += frame.vx * timeStep;
      frame.y += frame.vy * timeStep;

      // Update the frame position in the DOM
      d3.select("#" + frame.id)
        .attr("cx", frame.x)
        .attr("cy", frame.y);
    }
  }

  function updateFrame(frameId, targetDomain, nodes) {
    const framePadding = 2;
    const scaleFactor = 0.5;

    const domainNodeCounts = getDomainNodeCounts(nodes);
    const maxNodeCount = Math.max(...Object.values(domainNodeCounts));
    const targetNodes = nodes.filter(
      (d) => d.properties.domain === targetDomain
    );

    if (targetNodes.length === 0) return;

    const { xMin, xMax, yMin, yMax } = getNodeBounds(targetNodes, framePadding);
    const { centerX, centerY, radius } = calculateFrameParameters(
      xMin,
      xMax,
      yMin,
      yMax,
      domainNodeCounts,
      targetDomain,
      scaleFactor,
      maxNodeCount
    );

    const menu = getMenuDomain(nodes);
    const frame = createOrUpdateFrame(
      svgNodes,
      frameId,
      centerX,
      centerY,
      radius,
      menu
    );
    const labelData = [{ x: centerX, y: centerY - radius, text: targetDomain }];

    createOrUpdateLabels(svgNodes, frameId, labelData, radius, menu, nodes);

    initializeDragForFrameAndLabel(
      frame,
      d3.selectAll("text.domain-label#" + frameId + "-label")
    );
  }

  function getDomainNodeCounts(nodes) {
    return nodes.reduce((acc, node) => {
      acc[node.properties.domain] = (acc[node.properties.domain] || 0) + 1;
      return acc;
    }, {});
  }

  function getNodeBounds(targetNodes, framePadding) {
    return {
      xMin: d3.min(targetNodes, (d) => d.x) - framePadding,
      xMax: d3.max(targetNodes, (d) => d.x) + framePadding,
      yMin: d3.min(targetNodes, (d) => d.y) - framePadding,
      yMax: d3.max(targetNodes, (d) => d.y) + framePadding,
    };
  }

  function calculateFrameParameters(
    xMin,
    xMax,
    yMin,
    yMax,
    domainNodeCounts,
    targetDomain,
    scaleFactor,
    maxNodeCount
  ) {
    const centerX = (xMin + xMax) / 2;
    const centerY = (yMin + yMax) / 2;
    const baseRadius = Math.sqrt((xMax - xMin) ** 2 + (yMax - yMin) ** 2) / 2;
    const domainNodeCount = domainNodeCounts[targetDomain];
    const radius =
      baseRadius + (baseRadius * scaleFactor * domainNodeCount) / maxNodeCount;

    return { centerX, centerY, radius };
  }
  function createOrUpdateFrame(
    svgNodes,
    frameId,
    centerX,
    centerY,
    radius,
    menu
  ) {
    const frameData = [{ cx: centerX, cy: centerY, r: radius }];

    const frameSelection = svgNodes
      .selectAll("circle#" + frameId)

      .data(frameData);

    const frameEnter = frameSelection
      .enter()
      .append("circle")
      .attr("id", frameId)
      .attr("class", "frame")

      .attr("data-stroke-color", () => getRandomColor())
      .attr("stroke-opacity", 0.2);

    const frameUpdate = frameEnter
      .merge(frameSelection)
      .attr("stroke", function () {
        return d3.select(this).attr("data-stroke-color");
      })
      .attr("fill", "none")
      .attr("stroke-width", 20)
      .attr("cx", (d) => d.cx)
      .attr("cy", (d) => d.cy)
      .attr("r", (d) => d.r)
      .on("mouseenter", function () {
        d3.select(this).attr("stroke-width", 25).attr("stroke-opacity", 0.3);
      })
      .on("mouseleave", function () {
        d3.select(this).attr("stroke-width", 20).attr("stroke-opacity", 0.2);
      })
      .on("contextmenu", function (d) {
        d3.event.preventDefault();
        tool(menu)(d);
      });

    return frameUpdate;
  }
  function tickRelationshipsOutlines() {
    relationship.each(function () {
      // FIXME:

      let rel = d3.select(this),
        outline = rel.select(".outline"),
        text = rel.select(".text"),
        textPadding = 8,
        textLength = text.node().getComputedTextLength(),
        captionLength = textLength > 0 ? textLength + textPadding : 0;

      outline.attr("d", (d) => {
        if (captionLength > d.arrow.shaftLength) {
          captionLength = d.arrow.shaftLength;
        }

        return d.arrow.outline(captionLength);
      });
    });
  }

  function tickRelationshipsOverlays() {
    relationshipOverlay.attr("d", (d) => {
      return d.arrow.overlay(options.arrowSize);
    });
  }

  function tickRelationshipsTexts() {
    // Constants for font size and padding
    const fontSize = 8.5;
    const padding = 1;

    // Update the transform attribute to rotate the text based on the natural angle
    relationshipText.attr("transform", (rel) => {
      if (rel.naturalAngle < 90 || rel.naturalAngle > 270) {
        return `rotate(180 ${rel.arrow.midShaftPoint.x} ${rel.arrow.midShaftPoint.y})`;
      } else {
        return null;
      }
    });

    // Update the x and y attributes to position the text at the mid-point of the arrow
    relationshipText.attr("x", (rel) => rel.arrow.midShaftPoint.x);
    relationshipText.attr(
      "y",
      (rel) => rel.arrow.midShaftPoint.y + fontSize / 2 - padding
    );
  }
  function createLabelDragBehavior() {
    return d3
      .drag()
      .on("start", function () {
        const label = d3.select(this);
        const bbox = this.getBBox();
        const initialPosition = { x: bbox.x, y: bbox.y };
        label.datum({ initialPosition });
      })
      .on("drag", function () {
        const label = d3.select(this);
        const dx = d3.event.dx;
        const dy = d3.event.dy;
        const initialPosition = label.datum().initialPosition;
        label
          .attr("x", initialPosition.x + dx)
          .attr("y", initialPosition.y + dy);
      });
  }
  function createOrUpdateLabels(
    svgNodes,
    frameId,
    labelData,
    radius,
    menu,
    nodes
  ) {
    const labels = svgNodes
      .selectAll("text.domain-label#" + frameId + "-label")
      .data(labelData);

    const labelsEnter = labels
      .enter()
      .append("text")
      .attr("id", () => frameId + "-label")
      .attr("class", "domain-label")
      .attr("data-frame-id", frameId);

    const labelsUpdate = labelsEnter
      .merge(labels)
      .attr("x", (d) => d.x)
      .attr("y", (d) => d.y)
      .attr("font-size", () => getTextSize(radius) + "px")
      .attr("data-frame-id", frameId);

    const tspans = labelsUpdate.selectAll("tspan").data((d) => [d]);

    tspans
      .enter()
      .append("tspan")
      .merge(tspans)
      .attr("dy", "-0.5em")
      .attr("dx", "-0.5em")
      .text((d) => d.text)
      .attr("font-size", () => getTextSize(radius) + "px");

    labelsUpdate
      .on("click", function (d) {
        const targetDomain = d.text;
        const targetNodes = nodes.filter(
          (node) => node.properties.domain === targetDomain
        );
        // const frameId = d3.select(this).attr("data-frame-id");
        // const frame = d3.select(`circle#${frameId}`);

        targetNodes.forEach((node) => {
          node.fx = node.x;
          node.fy = node.y;
        });
      })
      .on("dblclick", function (d) {
        const targetDomain = d.text;
        const targetNodes = nodes.filter(
          (node) => node.properties.domain === targetDomain
        );
        targetNodes.forEach((node) => {
          node.fx = null;
          node.fy = null;
        });
      })
      .on("contextmenu", function (d) {
        d3.event.preventDefault();
        tool(menu)(d);
      });

    const labelDragBehavior = createLabelDragBehavior(frameId, nodes);
    labelsUpdate.call(labelDragBehavior);

    return labelsUpdate;
  }

  function initializeDragForFrameAndLabel(frame, label) {
    // Call the drag handler on both the frame and the label elements
    frame.call(createFrameDragBehavior(label));
    label.call(createLabelDragBehavior(frame.attr("id")));
  }

  function createFrameDragBehavior(label) {
    let targetNodes;
    let initialFramePosition;
    let initialNodePositions;

    return d3
      .drag()
      .on("start", function () {
        // Get target domain on drag start
        const frameId = d3.select(this).attr("id");
        const targetDomain = d3.select(`text#${frameId}-label`).text();

        // Get target nodes on drag start
        targetNodes = nodes.filter((d) => d.properties.domain === targetDomain);

        // Store initial frame position
        initialFramePosition = {
          x: parseFloat(d3.select(this).attr("cx")),
          y: parseFloat(d3.select(this).attr("cy")),
        };

        // Store initial node positions
        initialNodePositions = targetNodes.map((node) => ({
          x: node.x,
          y: node.y,
        }));

        // Add the highlighted-frame class to both the frame and the label
        d3.select(this).classed("highlighted-frame", true);
      })
      .on("drag", function () {
        const dx = d3.event.dx;
        const dy = d3.event.dy;

        // Update frame position
        const newFrameCx = initialFramePosition.x + dx;
        const newFrameCy = initialFramePosition.y + dy;
        d3.select(this).attr("cx", newFrameCx).attr("cy", newFrameCy);

        // Update label position
        const frameId = d3.select(this).attr("id");
        const draggedLabel = d3.select(`text#${frameId}-label`);
        const newLabelX = parseFloat(draggedLabel.attr("x")) + dx;
        const newLabelY = parseFloat(draggedLabel.attr("y")) + dy;
        draggedLabel.attr("x", newLabelX).attr("y", newLabelY);

        // Update nodes positions
        targetNodes.forEach((d, i) => {
          d.x = initialNodePositions[i].x + dx;
          d.y = initialNodePositions[i].y + dy;
          d.fx = d.x;
          d.fy = d.y;
        });

        // Update node elements
        node.attr("transform", (d) => `translate(${d.x}, ${d.y})`);
      })
      .on("end", function () {
        // Remove the highlighted-frame class from both the frame and the label
        d3.select(this).classed("highlighted-frame", false);
        label.classed("highlighted-frame", false);

        // Pin nodes to their current position
        targetNodes.forEach((d) => {
          d.fx = d.x;
          d.fy = d.y;
        });

        // Restart simulation to apply the changes
        simulation.alphaTarget(0.3).restart();
      });
  }
  9;

  // eslint-disable-next-line no-unused-vars
  function filterRelationsAndNodesBetweenDates(
    nodes,
    relationships,
    startDate,
    endDate
  ) {
    const filteredRelationships = relationships.filter((relationship) => {
      const relationshipDate = new Date(relationship.properties.datetime);
      return relationshipDate >= startDate && relationshipDate <= endDate;
    });

    const connectedNodeIds = new Set();
    filteredRelationships.forEach((relationship) => {
      connectedNodeIds.add(relationship.source);
      connectedNodeIds.add(relationship.target);
    });

    const filteredNodes = nodes.filter((node) => connectedNodeIds.has(node.id));

    return { filteredNodes, filteredRelationships };
  }
  return { drawGraph };
}
